use board::{Board, CardType, FieldPosition, NumberCard, NumberCardColor};
use serde::{Deserialize, Serialize};

const COLOR_SEQUENCE: [NumberCardColor; 3] = [
    NumberCardColor::Red,
    NumberCardColor::Green,
    NumberCardColor::Black,
];

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct Move {
    start_card: CardType,
    stack_len: u8,
    pattern: u8,
    pub source: FieldPosition,
    pub destination: FieldPosition,
}

impl Move {
    #[must_use]
    fn alternate_card(bottom_suit: &NumberCardColor, bit: u8) -> NumberCardColor {
        let pos = COLOR_SEQUENCE
            .iter()
            .position(|x| return x == bottom_suit)
            .unwrap();
        let shift_value = if bit == 0 { 0 } else { 1 };
        return COLOR_SEQUENCE[(pos + shift_value + 1) % 3].clone();
    }

    #[must_use]
    fn bit_card(last_card: &board::NumberCardColor, current_card: &board::NumberCardColor) -> u8 {
        let last_pos = COLOR_SEQUENCE
            .iter()
            .position(|x| return x == last_card)
            .unwrap();
        let current_pos = COLOR_SEQUENCE
            .iter()
            .position(|x| return x == current_card)
            .unwrap();
        if (last_pos + 1) % 3 == current_pos {
            return 0;
        } else {
            return 1;
        }
    }
    #[must_use]
    pub fn cards(&self) -> Vec<CardType> {
        if let CardType::Number(NumberCard { value, .. }) = self.start_card {
            let mut result = Vec::with_capacity(usize::from(self.stack_len));
            result.push(self.start_card.clone());
            for index in 1..self.stack_len {
                let new_color = if let board::CardType::Number(board::NumberCard {
                    suit: last_suit,
                    ..
                }) = result.last().unwrap()
                {
                    Self::alternate_card(last_suit, self.pattern & (1 << (index - 1)))
                } else {
                    panic!("");
                };
                result.push(board::CardType::Number(board::NumberCard {
                    suit: new_color,
                    value: value - index,
                }));
            }
            return result;
        } else {
            return vec![self.start_card.clone()];
        }
    }

    #[must_use]
    pub fn stack_len(&self) -> u8 {
        return self.stack_len;
    }

    #[must_use]
    pub fn new<'a>(
        source: FieldPosition,
        destination: FieldPosition,
        cards: &'a [board::CardType],
    ) -> Self {
        let mut pattern: u8 = 0;
        let numbercard_filter = |card: &'a CardType| -> Option<&'a NumberCard> {
            if let board::CardType::Number(numbercard) = card {
                return Option::Some(numbercard);
            } else {
                return Option::None;
            }
        };
        for (index, (last_card, card)) in (0_u8..).zip(
            cards
                .iter()
                .filter_map(numbercard_filter)
                .zip(cards.iter().skip(1).filter_map(numbercard_filter)),
        ) {
            pattern |= Self::bit_card(&last_card.suit, &card.suit) << index;
            debug_assert_eq!(card.value + 1, last_card.value);
        }

        return Self {
            source,
            destination,
            start_card: cards[0].clone(),
            stack_len: cards.len() as u8,
            pattern,
        };
    }
}

impl super::BoardApplication for Move {
    fn apply(&self, solboard: &mut Board) {
        solboard.field[usize::from(self.source.column())].truncate(
            solboard.field[usize::from(self.source.column())].len() - usize::from(self.stack_len()),
        );
        solboard.field[usize::from(self.destination.column())].append(&mut self.cards());
    }

    fn undo(&self, solboard: &mut Board) {
        solboard.field[usize::from(self.destination.column())].truncate(
            solboard.field[usize::from(self.destination.column())].len()
                - usize::from(self.stack_len()),
        );
        solboard.field[usize::from(self.source.column())].append(&mut self.cards());
    }

    #[must_use]
    fn can_apply(&self, _solboard: &Board) -> bool {
        return true;
    }

    #[must_use]
    fn can_undo(&self, _solboard: &Board) -> bool {
        return true;
    }
}

impl std::fmt::Display for Move {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        let card_name = if self.stack_len() == 1 {
            format!("{}", self.cards()[0])
        } else {
            format!("{} cards", self.stack_len())
        };
        return write!(
            f,
            "Move {} from {} to {}",
            card_name, self.source, self.destination
        );
    }
}

#[test]
fn move_storage() {
    let card_stack = vec![
        board::CardType::Number(NumberCard {
            value: 5,
            suit: board::NumberCardColor::Red,
        }),
        board::CardType::Number(NumberCard {
            value: 4,
            suit: board::NumberCardColor::Black,
        }),
        board::CardType::Number(NumberCard {
            value: 3,
            suit: board::NumberCardColor::Green,
        }),
    ];
    let source = FieldPosition::new(0, 0);
    let destination = FieldPosition::new(0, 1);
    let my_move = Move::new(source.clone(), destination.clone(), &card_stack);
    assert_eq!(my_move.cards(), card_stack);
    let my_move = Move::new(source, destination, &card_stack[0..1]);
    assert_eq!(
        my_move.cards().iter().collect::<Vec<_>>(),
        card_stack.iter().take(1).collect::<Vec<_>>()
    )
}
