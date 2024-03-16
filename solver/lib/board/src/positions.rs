use crate::cards::{CardTypeNoHua, SpecialCardType};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, PartialEq, Eq, Ord, PartialOrd, Hash, Clone)]
pub enum BunkerSlot {
    Empty,
    Blocked(Option<SpecialCardType>),
    Stash(CardTypeNoHua),
}

#[derive(Debug, Serialize, Deserialize, Clone, Eq, PartialEq, Hash)]
pub enum Position {
    Field(crate::FieldPosition),
    Bunker { slot_index: u8 },
    Goal { slot_index: u8 },
}

impl std::fmt::Display for Position {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Self::Field(x) => return write!(f, "Field ({})", x),
            Self::Bunker { slot_index } => return write!(f, "Bunker #{}", slot_index),
            Self::Goal { slot_index } => return write!(f, "Goal #{}", slot_index),
        }
    }
}

impl From<PositionNoGoal> for Position {
    fn from(input: PositionNoGoal) -> Self {
        match input {
            PositionNoGoal::Field(x) => return Self::Field(x),
            PositionNoGoal::Bunker { slot_index } => return Self::Bunker { slot_index },
        };
    }
}

impl PartialEq<PositionNoGoal> for Position {
    fn eq(&self, other: &PositionNoGoal) -> bool {
        return other.eq(self);
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Copy, Eq, PartialEq, Hash)]
pub enum PositionNoGoal {
    Field(crate::FieldPosition),
    Bunker { slot_index: u8 },
}

impl std::fmt::Display for PositionNoGoal {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(f, "{}", Position::from(*self));
    }
}

#[derive(Debug, Clone)]
pub struct GoalTransformError;

impl std::convert::TryFrom<Position> for PositionNoGoal {
    type Error = GoalTransformError;
    fn try_from(input: Position) -> Result<Self, Self::Error> {
        match input {
            Position::Field(field_position) => return Result::Ok(Self::Field(field_position)),
            Position::Bunker { slot_index } => {
                return Result::Ok(Self::Bunker { slot_index });
            }
            Position::Goal { .. } => {
                return Result::Err(GoalTransformError);
            }
        }
    }
}

impl PartialEq<Position> for PositionNoGoal {
    fn eq(&self, other: &Position) -> bool {
        let other = <Self as std::convert::TryFrom<Position>>::try_from(other.clone());
        match other {
            Ok(other) => {
                return Self::eq(self, &other);
            }
            Err(GoalTransformError) => {
                return false;
            }
        }
    }
}
