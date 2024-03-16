use crate::possibilities::{all_actions, bunkerize_actions, dragonkill_actions};
use board::{BunkerSlot, CardTypeNoHua, SpecialCardType};
#[test]
pub fn dragonkill_test() -> Result<(), Box<dyn std::error::Error>> {
    let mut x = board::load_test_board!("specific/dragonkill.json")?;
    assert_eq!(dragonkill_actions(&x).len(), 1);
    x.field[3].pop();
    x.bunker[2] = BunkerSlot::Stash(CardTypeNoHua::Special(SpecialCardType::Zhong));
    assert_eq!(dragonkill_actions(&x).len(), 1);
    return Result::Ok(());
}

#[test]
pub fn bunkerize_test() -> Result<(), Box<dyn std::error::Error>> {
    let x = board::load_test_board!("specific/dragonkill.json")?;
    assert_eq!(bunkerize_actions(&x).len(), 5);
    return Result::Ok(());
}

#[test]
pub fn all_actions_test() -> Result<(), Box<dyn std::error::Error>> {
    let x = board::load_test_board!("specific/dragonkill.json")?;
    let possible_actions = all_actions(&x);
    assert_eq!(possible_actions.len(), 12);
    assert_eq!(
        possible_actions.iter().fold([0, 0, 0, 0, 0], |mut sum, x| {
            match x {
                crate::All::Bunkerize(_) => sum[0] += 1,
                crate::All::Move(_) => sum[1] += 1,
                crate::All::Goal(_) => sum[2] += 1,
                crate::All::DragonKill(_) => sum[3] += 1,
                _ => sum[4] += 1,
            }
            return sum;
        }),
        [5, 5, 1, 1, 0]
    );
    return Result::Ok(());
}
