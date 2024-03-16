use crate::{CardType, Error, NumberCard, NumberCardColor};
#[test]
pub fn check_test() -> Result<(), Box<dyn std::error::Error>> {
    // let mut x = Board::from_file(std::path::Path::new(crate::test_boards::SPECIFIC)?;
    let mut x = crate::load_test_board!("specific/solved.json")?;
    assert_eq!(x.check(), Result::Ok(()));
    assert_eq!(x.solved(), true);
    x.field[2].push(CardType::Hua);
    assert_eq!(x.check(), Result::Err(Error::CardDouble(CardType::Hua)));
    x.hua_set = false;
    assert_eq!(x.check(), Result::Ok(()));
    x.field[2].push(CardType::Number(NumberCard {
        suit: NumberCardColor::Black,
        value: 9,
    }));
    assert_eq!(
        x.check(),
        Result::Err(Error::GoalTooHigh(NumberCard {
            value: 9,
            suit: NumberCardColor::Black
        }))
    );
    x.goal[0] = Some(NumberCard {
        suit: NumberCardColor::Black,
        value: 8,
    });
    assert_eq!(x.check(), Result::Ok(()));
    assert_eq!(x.solved(), false);
    return Result::Ok(());
}
