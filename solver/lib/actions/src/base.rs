use board::{
    Board, BunkerSlot, CardType, CardTypeNoHua, FieldPosition, NumberCard, PositionNoGoal,
    SpecialCardType,
};

use serde::{Deserialize, Serialize};

pub(super) trait BoardApplication {
    fn apply(&self, solboard: &mut Board);
    fn undo(&self, solboard: &mut Board);
    fn can_apply(&self, solboard: &Board) -> bool;
    fn can_undo(&self, solboard: &Board) -> bool;
    fn checked_apply(&self, solboard: &mut Board) -> bool {
        if self.can_apply(solboard) {
            self.apply(solboard);
            return true;
        }
        return false;
    }
    fn checked_undo(&self, solboard: &mut Board) -> bool {
        if self.can_undo(solboard) {
            self.undo(solboard);
            return true;
        }
        return false;
    }
}

fn can_pop_top(solboard: &Board, position: &PositionNoGoal, card: &CardType) -> bool {
    match position {
        PositionNoGoal::Field(fieldpos) => {
            if solboard.field[usize::from(fieldpos.column())]
                .last()
                .expect("Trying to pop top of empty field stack")
                != card
            {
                return false;
            }
        }
        PositionNoGoal::Bunker { slot_index } => {
            if solboard.bunker[usize::from(*slot_index)] != BunkerSlot::Stash(card.remove_hua()) {
                return false;
            }
        }
    };
    return true;
}

fn pop_top(solboard: &mut Board, position: &PositionNoGoal, card: &CardType) {
    debug_assert!(can_pop_top(solboard, position, card));
    match position {
        PositionNoGoal::Field(fieldpos) => {
            solboard
                .field
                .get_mut(usize::from(fieldpos.column()))
                .expect("Column index fucked")
                .pop();
        }
        PositionNoGoal::Bunker { slot_index } => {
            solboard.bunker[usize::from(*slot_index)] = BunkerSlot::Empty;
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct Goal {
    pub card: NumberCard,
    pub source: PositionNoGoal,
    pub goal_slot_index: u8,
}

impl BoardApplication for Goal {
    fn can_apply(&self, solboard: &Board) -> bool {
        match &solboard.goal[usize::from(self.goal_slot_index)] {
            Option::Some(NumberCard { value, suit }) => {
                if self.card.value != *value + 1 {
                    return false;
                }
                if self.card.suit != *suit {
                    return false;
                }
            }
            Option::None => {
                if self.card.value != 1 {
                    return false;
                }
            }
        }
        if !can_pop_top(solboard, &self.source, &CardType::Number(self.card.clone())) {
            return false;
        }
        return true;
    }
    fn can_undo(&self, _solboard: &Board) -> bool {
        return true;
    }
    fn apply(&self, solboard: &mut Board) {
        pop_top(solboard, &self.source, &CardType::Number(self.card.clone()));
        *solboard
            .goal
            .get_mut(usize::from(self.goal_slot_index))
            .expect("Slot index fucked") = Option::Some(self.card.clone());
    }
    fn undo(&self, solboard: &mut Board) {
        match &self.source {
            PositionNoGoal::Field(position) => {
                solboard
                    .field
                    .get_mut(usize::from(position.column()))
                    .expect("Column index fucked")
                    .push(CardType::Number(self.card.clone()));
            }
            PositionNoGoal::Bunker { slot_index } => {
                solboard.bunker[usize::from(*slot_index)] =
                    BunkerSlot::Stash(CardTypeNoHua::Number(self.card.clone()));
            }
        }
        if self.card.value == 1 {
            solboard.goal[usize::from(self.goal_slot_index)] = Option::None;
        } else {
            solboard.goal[usize::from(self.goal_slot_index)] = Option::Some(NumberCard {
                suit: self.card.suit.clone(),
                value: self.card.value - 1,
            });
        }
    }
}

impl std::fmt::Display for Goal {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(
            f,
            "Goal {} from {} to slot #{}",
            self.card, self.source, self.goal_slot_index
        );
    }
}
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct DragonKill {
    pub card: SpecialCardType,
    pub source: [PositionNoGoal; 4],
    pub destination_slot_index: u8,
}

impl BoardApplication for DragonKill {
    fn apply(&self, solboard: &mut Board) {
        for position in &self.source {
            pop_top(solboard, position, &CardType::Special(self.card.clone()));
        }
        solboard.bunker[usize::from(self.destination_slot_index)] =
            BunkerSlot::Blocked(Option::Some(self.card.clone()));
    }
    fn undo(&self, solboard: &mut Board) {
        solboard.bunker[usize::from(self.destination_slot_index)] = BunkerSlot::Empty;
        for position in &self.source {
            match &position {
                PositionNoGoal::Field(field_position) => {
                    solboard.field[usize::from(field_position.column())]
                        .push(CardType::Special(self.card.clone()));
                }
                PositionNoGoal::Bunker { slot_index } => {
                    solboard.bunker[usize::from(*slot_index)] =
                        BunkerSlot::Stash(CardTypeNoHua::Special(self.card.clone()));
                }
            }
        }
    }
    fn can_apply(&self, solboard: &Board) -> bool {
        if self.destination_slot_index >= 3 {
            return false;
        }
        let previous_slot_empty = solboard
            .bunker
            .iter()
            .take(self.destination_slot_index.saturating_sub(1).into())
            .all(|x| {
                if let BunkerSlot::Empty = x {
                    return true;
                } else {
                    return false;
                }
            });
        if previous_slot_empty {
            return false;
        }
        return true;
    }
    fn can_undo(&self, _solboard: &Board) -> bool {
        return true;
    }
}

impl std::fmt::Display for DragonKill {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(
            f,
            "Kill {} to bunker #{} from {}, {}, {}, {}",
            self.card,
            self.destination_slot_index,
            self.source[0],
            self.source[1],
            self.source[2],
            self.source[3],
        );
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct Bunkerize {
    pub card: CardTypeNoHua,
    pub bunker_slot_index: u8,
    pub field_position: FieldPosition,
    pub to_bunker: bool,
}
impl Bunkerize {
    fn can_move_to_bunker(&self, solboard: &Board) -> bool {
        if self.field_position.row() + 1
            != solboard.field[usize::from(self.field_position.column())].len() as u8
        {
            return false;
        }
        if self.card.add_hua()
            != *solboard.field[usize::from(self.field_position.column())]
                .last()
                .unwrap()
        {
            return false;
        }
        if solboard.bunker[usize::from(self.bunker_slot_index)] != BunkerSlot::Empty {
            return false;
        }
        return true;
    }
    fn move_to_bunker(&self, solboard: &mut Board) {
        debug_assert!(self.can_move_to_bunker(solboard));
        solboard.field[usize::from(self.field_position.column())].pop();
        solboard.bunker[usize::from(self.bunker_slot_index)] = BunkerSlot::Stash(self.card.clone());
    }
    fn can_move_from_bunker(&self, solboard: &Board) -> bool {
        if solboard.bunker[usize::from(self.bunker_slot_index)]
            != BunkerSlot::Stash(self.card.clone())
        {
            return false;
        }
        if self.field_position.row()
            != solboard.field[usize::from(self.field_position.column())].len() as u8
        {
            return false;
        }
        return true;
    }
    fn move_from_bunker(&self, solboard: &mut Board) {
        debug_assert!(self.can_move_from_bunker(solboard));
        solboard.field[usize::from(self.field_position.column())].push(self.card.add_hua());
        solboard.bunker[usize::from(self.bunker_slot_index)] = BunkerSlot::Empty;
    }
}

impl BoardApplication for Bunkerize {
    fn apply(&self, solboard: &mut Board) {
        if self.to_bunker {
            self.move_to_bunker(solboard);
        } else {
            self.move_from_bunker(solboard);
        }
    }
    fn undo(&self, solboard: &mut Board) {
        if self.to_bunker {
            self.move_from_bunker(solboard);
        } else {
            self.move_to_bunker(solboard);
        }
    }
    fn can_apply(&self, solboard: &Board) -> bool {
        if self.to_bunker {
            return self.can_move_to_bunker(solboard);
        } else {
            return self.can_move_from_bunker(solboard);
        }
    }
    fn can_undo(&self, solboard: &Board) -> bool {
        if self.to_bunker {
            return self.can_move_from_bunker(solboard);
        } else {
            return self.can_move_to_bunker(solboard);
        }
    }
}

impl std::fmt::Display for Bunkerize {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        if self.to_bunker {
            return write!(
                f,
                "Move {} from {} to bunker #{}",
                self.card, self.field_position, self.bunker_slot_index,
            );
        } else {
            return write!(
                f,
                "Move {} from bunker #{} to {}",
                self.card, self.bunker_slot_index, self.field_position,
            );
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct HuaKill {
    pub field_position: FieldPosition,
}

impl BoardApplication for HuaKill {
    fn can_apply(&self, solboard: &Board) -> bool {
        if solboard.field[usize::from(self.field_position.column())].last()
            != Option::Some(&CardType::Hua)
        {
            return false;
        }
        if solboard.field[usize::from(self.field_position.column())].len()
            != (self.field_position.row() + 1) as usize
        {
            return false;
        }
        return true;
    }
    fn apply(&self, solboard: &mut Board) {
        debug_assert!(self.can_apply(solboard));
        solboard.field[usize::from(self.field_position.column())].pop();
        solboard.hua_set = true;
    }
    fn can_undo(&self, solboard: &Board) -> bool {
        if solboard.field[usize::from(self.field_position.column())].len()
            != self.field_position.row() as usize
        {
            return false;
        }
        return true;
    }
    fn undo(&self, solboard: &mut Board) {
        debug_assert!(self.can_undo(solboard));
        solboard.field[usize::from(self.field_position.column())].push(CardType::Hua);
        solboard.hua_set = false;
    }
}
impl std::fmt::Display for HuaKill {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(f, "Kill hua from {}", self.field_position);
    }
}
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub enum All {
    Bunkerize(Bunkerize),
    DragonKill(DragonKill),
    Goal(Goal),
    HuaKill(HuaKill),
    Move(super::Move),
}
impl std::fmt::Display for All {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Self::Bunkerize(x) => return write!(f, "{}", x),
            Self::DragonKill(x) => return write!(f, "{}", x),
            Self::Goal(x) => return write!(f, "{}", x),
            Self::HuaKill(x) => return write!(f, "{}", x),
            Self::Move(x) => return write!(f, "{}", x),
        }
    }
}
impl All {
    pub fn apply(&self, solboard: &mut Board) {
        match self {
            Self::HuaKill(obj) => {
                obj.apply(solboard);
            }
            Self::DragonKill(obj) => {
                obj.apply(solboard);
            }
            Self::Goal(obj) => {
                obj.apply(solboard);
            }
            Self::Bunkerize(obj) => {
                obj.apply(solboard);
            }
            Self::Move(obj) => obj.apply(solboard),
        }
    }
    pub fn undo(&self, solboard: &mut Board) {
        match self {
            Self::HuaKill(obj) => {
                obj.undo(solboard);
            }
            Self::DragonKill(obj) => {
                obj.undo(solboard);
            }
            Self::Goal(obj) => {
                obj.undo(solboard);
            }
            Self::Bunkerize(obj) => {
                obj.undo(solboard);
            }
            Self::Move(obj) => obj.undo(solboard),
        }
    }
}
