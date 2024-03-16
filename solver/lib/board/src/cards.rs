use enum_iterator::IntoEnumIterator;
use serde::{Deserialize, Serialize};
use std::fmt::Display;
#[derive(
    Serialize, Deserialize, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Clone, IntoEnumIterator,
)]
pub enum SpecialCardType {
    Zhong,
    Bai,
    Fa,
}

impl Display for SpecialCardType {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(f, "{:#?}", self);
    }
}

#[derive(
    Serialize, Deserialize, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Clone, IntoEnumIterator,
)]
pub enum NumberCardColor {
    Red,
    Green,
    Black,
}

impl Display for NumberCardColor {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(f, "{:#?}", self);
    }
}

#[derive(Serialize, Deserialize, Debug, Clone, Eq, PartialEq, Hash, PartialOrd, Ord)]
pub struct NumberCard {
    pub value: u8,
    pub suit: NumberCardColor,
}
impl Display for NumberCard {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(f, "{} {}", self.suit, self.value);
    }
}

#[derive(Serialize, Deserialize, Debug, Clone, Eq, PartialEq, Hash, Ord, PartialOrd)]
pub enum CardType {
    Hua,
    Number(NumberCard),
    Special(SpecialCardType),
}

impl CardType {
    #[must_use]
    pub fn remove_hua(&self) -> CardTypeNoHua {
        match self {
            Self::Number(x) => return CardTypeNoHua::Number(x.clone()),
            Self::Special(x) => return CardTypeNoHua::Special(x.clone()),
            Self::Hua => panic!("Remove hua on hua"),
        }
    }

    /// Returns a number from (1..=31)
    #[must_use]
    pub fn to_byte(&self) -> u8 {
        match self {
            Self::Number(numbercard) => {
                let result = numbercard.value
                    + 9 * (NumberCardColor::into_enum_iter()
                        .position(|suit| return numbercard.suit == suit)
                        .unwrap() as u8);
                debug_assert!(result >= 1 && result <= 27);
                return result;
            }
            Self::Special(specialcard) => {
                let result = 28
                    + (SpecialCardType::into_enum_iter()
                        .position(|x| return x == *specialcard)
                        .unwrap() as u8);
                debug_assert!(result >= 28 && result <= 30);
                return result;
            }
            Self::Hua => return 31,
        }
    }
}

impl Display for CardType {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Self::Hua => return write!(f, "Hua"),
            Self::Number(x) => return write!(f, "{}", x),
            Self::Special(x) => return write!(f, "{}", x),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Eq, PartialEq, Clone, Ord, PartialOrd, Hash)]
pub enum CardTypeNoHua {
    Number(NumberCard),
    Special(SpecialCardType),
}
impl Display for CardTypeNoHua {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Self::Number(x) => return write!(f, "{}", x),
            Self::Special(x) => return write!(f, "{}", x),
        }
    }
}

impl CardTypeNoHua {
    #[must_use] pub fn add_hua(&self) -> CardType {
        match self {
            Self::Number(x) => return CardType::Number(x.clone()),
            Self::Special(x) => return CardType::Special(x.clone()),
        }
    }
}
