use crate::{
    BunkerSlot, CardType, CardTypeNoHua, FieldPosition, NumberCard, NumberCardColor,
    PositionNoGoal, SpecialCardType,
};
use enum_iterator::IntoEnumIterator;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

#[derive(Debug, Clone, Eq, PartialEq, Hash)]
pub enum Error {
    CardMissing(CardType),
    CardDouble(CardType),
    GoalTooHigh(NumberCard),
    ErraneousCard(NumberCard),
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
pub struct Board {
    pub field: [Vec<CardType>; 8],
    pub goal: [Option<NumberCard>; 3],
    pub hua_set: bool,
    pub bunker: [BunkerSlot; 3],
}

impl Default for Board {
    fn default() -> Self {
        return Self {
            field: [
                Vec::new(),
                Vec::new(),
                Vec::new(),
                Vec::new(),
                Vec::new(),
                Vec::new(),
                Vec::new(),
                Vec::new(),
            ],
            goal: [
                Option::Some(NumberCard {
                    value: 9,
                    suit: NumberCardColor::Black,
                }),
                Option::Some(NumberCard {
                    value: 9,
                    suit: NumberCardColor::Red,
                }),
                Option::Some(NumberCard {
                    value: 9,
                    suit: NumberCardColor::Green,
                }),
            ],
            hua_set: false,
            bunker: [
                BunkerSlot::Blocked(Option::Some(SpecialCardType::Bai)),
                BunkerSlot::Blocked(Option::Some(SpecialCardType::Zhong)),
                BunkerSlot::Blocked(Option::Some(SpecialCardType::Fa)),
            ],
        };
    }
}
pub struct BoardEqHash([u8; 32]);
impl PartialEq for BoardEqHash {
    fn eq(&self, other: &Self) -> bool {
        return self
            .0
            .iter()
            .zip(other.0.iter())
            .all(|(this_cell, other_cell)| return this_cell == other_cell);
    }
}
impl Eq for BoardEqHash {}

impl std::hash::Hash for BoardEqHash {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        state.write(&self.0);
    }
}
impl std::str::FromStr for Board {
    type Err = serde_json::error::Error;
    fn from_str(json_string: &str) -> Result<Self, Self::Err> {
        //! # Errors
        //! Will return `io::Result::Err` when the path cannot be found,
        //! and `Result::Err` when the json in the file is incorrect
        return serde_json::from_str::<Self>(json_string);
    }
}

struct BitSquasher<'a> {
    sink: &'a mut [u8],
    byte: usize,
    bit: u8,
}

impl<'a> BitSquasher<'a> {
    pub fn new(sink: &'a mut [u8]) -> Self {
        return BitSquasher {
            sink,
            byte: 0,
            bit: 0,
        };
    }
    pub fn squash(&mut self, input: u8, count: u8) {
        debug_assert!(count <= 8);
        debug_assert!(count > 0);
        self.sink[self.byte] |= input << self.bit;
        if (8 - self.bit) < count {
            self.sink[self.byte + 1] |= input >> (8 - self.bit);
        }
        self.bit += count;
        self.byte += usize::from(self.bit / 8);
        self.bit %= 8;
    }
}

#[test]
fn bit_squasher_test() {
    let mut buffer: [u8; 4] = Default::default();

    let mut squasher = BitSquasher::new(&mut buffer);
    squasher.squash(0b101, 3);
    squasher.squash(0b1111000, 7);
    squasher.squash(0b11001100, 8);
    squasher.squash(0b101010, 6);

    assert_eq!(buffer, [0b11000101, 0b00110011, 0b10101011, 0]);
}

impl Board {
    pub fn from_file(path: &Path) -> Result<Self, Box<dyn std::error::Error>> {
        //! # Errors
        //! Will return `io::Result::Err` when the path cannot be found,
        //! and `Result::Err` when the json in the file is incorrect
        let f = File::open(path)?;
        let reader = BufReader::new(f);
        let x: Self = serde_json::from_reader(reader)?;
        return Result::Ok(x);
    }

    #[must_use]
    pub fn goal_value(&self, suit: &NumberCardColor) -> u8 {
        return self
            .goal
            .iter()
            .filter_map(|card| return card.clone())
            .find_map(|card| {
                if &card.suit == suit {
                    return Option::Some(card.value);
                } else {
                    return Option::None;
                }
            })
            .unwrap_or(0);
    }
    #[must_use]
    pub fn equivalence_hash(&self) -> BoardEqHash {
        // up to 40 cards on the field
        // 8 empty card represents end of slot
        // 3 bunker
        // If hua in field -> hua not set, does not need representation
        // We can skip goal, as the value of the card in the goal
        // is the highest value missing from the board;
        let mut result = [0_u8; 32];
        let mut squasher = BitSquasher::new(&mut result);

        let mut field_lengths: [usize; 8] = Default::default();
        for (index, cell) in field_lengths.iter_mut().enumerate() {
            *cell = index;
        }
        field_lengths.sort_unstable_by(|left_index, right_index| {
            return self.field[*left_index].cmp(&self.field[*right_index]);
        });
        let sorted_iter = field_lengths.iter().map(|index| return &self.field[*index]);

        for slot in sorted_iter {
            let slot_size = slot.len();
            debug_assert!(slot.len() < 16);
            squasher.squash(slot_size as u8, 4);
            for cell in slot {
                let cell_byte = cell.to_byte();
                debug_assert!(cell_byte < 32);
                squasher.squash(cell_byte, 5);
            }
        }
        let mut sorted_bunker = self.bunker.clone();
        sorted_bunker.sort_unstable();
        for slot in sorted_bunker.iter() {
            let bunker_byte = match slot {
                BunkerSlot::Empty => 0,
                BunkerSlot::Stash(card) => card.add_hua().to_byte(),
                BunkerSlot::Blocked(Option::Some(card)) => {
                    CardType::Special(card.clone()).to_byte() | (1 << 5)
                }
                BunkerSlot::Blocked(Option::None) => (1 << 5),
            };
            debug_assert!(bunker_byte < 64);
            squasher.squash(bunker_byte, 6);
        }
        return BoardEqHash(result);
    }
    pub fn movable_cards<'a>(&'a self) -> impl Iterator<Item = (PositionNoGoal, CardType)> + 'a {
        let bunker_iterator = (0_u8..)
            .zip(self.bunker.iter())
            .filter_map(|(index, card)| {
                let pos = PositionNoGoal::Bunker { slot_index: index };
                let ret_card = match card {
                    BunkerSlot::Stash(CardTypeNoHua::Special(card)) => {
                        Option::Some(CardType::Special(card.clone()))
                    }
                    BunkerSlot::Stash(CardTypeNoHua::Number(card)) => {
                        Option::Some(CardType::Number(card.clone()))
                    }
                    _ => Option::None,
                };
                return ret_card.map(|card| return (pos, card));
            });
        let field_iterator = (0_u8..)
            .zip(self.field.iter())
            .filter_map(|(column_index, row)| {
                return row.last().map(|ret_card| {
                    let pos = PositionNoGoal::Field(FieldPosition::new(
                        column_index,
                        (row.len() - 1) as u8,
                    ));
                    return (pos, ret_card.clone());
                });
            });
        let result = bunker_iterator.chain(field_iterator);
        return result;
    }

    fn handle_number_card(
        card: &NumberCard,
        number_card_map: &mut HashMap<NumberCardColor, [bool; 9]>,
    ) -> Result<(), Error> {
        if card.value > 9 || card.value < 1 {
            return Result::Err(Error::ErraneousCard(card.clone()));
        }
        if *number_card_map
            .get_mut(&card.suit)
            .unwrap()
            .get(usize::from(card.value - 1))
            .unwrap()
        {
            return Result::Err(Error::CardDouble(CardType::Number(card.clone())));
        }
        *number_card_map
            .get_mut(&card.suit)
            .unwrap()
            .get_mut(usize::from(card.value - 1))
            .unwrap() = true;
        return Result::Ok(());
    }
    fn handle_special_card(
        card: &SpecialCardType,
        special_card_map: &mut HashMap<SpecialCardType, i8>,
    ) -> Result<(), Error> {
        let card_slot = special_card_map.entry(card.clone()).or_insert(0);
        if *card_slot > 4 {
            return Result::Err(Error::CardDouble(CardType::Special(card.clone())));
        }
        *card_slot += 1;
        return Result::Ok(());
    }

    pub fn check(&self) -> Result<(), Error> {
        //! # Errors
        //!
        //! Returns the error in the board
        let mut special_card_map: HashMap<SpecialCardType, i8> = HashMap::new();
        let mut number_card_map: HashMap<NumberCardColor, [bool; 9]> = HashMap::new();
        let mut unknown_blocked_count: u8 = 0;
        for color in NumberCardColor::into_enum_iter() {
            number_card_map.insert(color.clone(), [false; 9]);
        }
        for special_card_type in SpecialCardType::into_enum_iter() {
            special_card_map.insert(special_card_type.clone(), 0);
        }
        let mut hua_exists: bool = self.hua_set;

        for field_row in &self.field {
            for cell in field_row.iter() {
                match cell {
                    CardType::Number(number_card) => {
                        Self::handle_number_card(number_card, &mut number_card_map)?;
                    }
                    CardType::Special(card_type) => {
                        Self::handle_special_card(card_type, &mut special_card_map)?;
                    }
                    CardType::Hua => {
                        if hua_exists {
                            return Result::Err(Error::CardDouble(CardType::Hua));
                        } else {
                            hua_exists = true
                        }
                    }
                }
            }
        }

        for bunker_cell in &self.bunker {
            match bunker_cell {
                BunkerSlot::Blocked(Option::None) => unknown_blocked_count += 1,
                BunkerSlot::Blocked(Option::Some(special_card_type)) => {
                    for _ in 0..4 {
                        Self::handle_special_card(special_card_type, &mut special_card_map)?;
                    }
                }
                BunkerSlot::Stash(CardTypeNoHua::Special(special_card_type)) => {
                    Self::handle_special_card(special_card_type, &mut special_card_map)?;
                }
                BunkerSlot::Stash(CardTypeNoHua::Number(number_card)) => {
                    Self::handle_number_card(number_card, &mut number_card_map)?;
                }
                BunkerSlot::Empty => {}
            }
        }

        for goal_cell in &self.goal {
            if let Some(NumberCard { suit, value }) = goal_cell {
                let color_slice = number_card_map.get_mut(suit).unwrap();
                for i in 0..*value {
                    if *color_slice.get(usize::from(i)).unwrap() {
                        return Result::Err(Error::GoalTooHigh(NumberCard {
                            suit: suit.clone(),
                            value: *value,
                        }));
                    }
                    *color_slice.get_mut(usize::from(i)).unwrap() = true;
                }
            }
        }
        for (card_type, count) in &special_card_map {
            if *count != 4 {
                if unknown_blocked_count == 0 {
                    return Result::Err(Error::CardMissing(CardType::Special(card_type.clone())));
                }
                unknown_blocked_count -= 1;
            }
        }
        for (card_type, value_array) in &number_card_map {
            for (index, value_hit) in (0_u8..).zip(value_array.iter()) {
                if !*value_hit {
                    return Result::Err(Error::CardMissing(CardType::Number(NumberCard {
                        suit: card_type.clone(),
                        value: (index + 1),
                    })));
                }
            }
        }
        return Result::Ok(());
    }

    #[must_use]
    pub fn solved(&self) -> bool {
        for row in &self.field {
            if !row.is_empty() {
                return false;
            }
        }
        for slot in &self.bunker {
            if let BunkerSlot::Blocked(_) = slot {
            } else {
                return false;
            }
        }
        if !self.hua_set {
            return false;
        }

        for goal_slot in &self.goal {
            if goal_slot.is_none() {
                return false;
            }
        }
        for color in NumberCardColor::into_enum_iter() {
            let color_position = self.goal.iter().position(|goal_card| {
                return goal_card
                    .as_ref()
                    .expect("We already checked that every goal slot is not None")
                    .suit
                    == color;
            });
            if color_position.is_none() {
                return false;
            }
        }

        for card in &self.goal {
            if card
                .as_ref()
                .expect("We already checked that every goal slot is not None")
                .value
                != 9
            {
                return false;
            }
        }
        return true;
    }
}
