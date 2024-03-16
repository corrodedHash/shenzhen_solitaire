use crate::solve;

#[test]
pub fn test_almost_solved() -> Result<(), Box<dyn std::error::Error>> {
    //! # Errors
    let x = board::load_test_board!("specific/scarce.json")?;
    assert_eq!(x.check(), Result::Ok(()));
    let result = solve(&x);
    assert!(result.is_ok());
    return Result::Ok(());
}
