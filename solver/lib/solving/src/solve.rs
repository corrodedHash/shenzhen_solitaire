use super::board_state_iterator::adapter::BoardStateIteratorAdapter;
use super::board_state_iterator::BoardStateIterator;

#[derive(Debug)]
pub struct Error {}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        return write!(f, "Board options exhausted, no solution found");
    }
}

impl std::error::Error for Error {}

pub fn solve(solboard: &board::Board) -> Result<Vec<actions::All>, Error> {
    //! # Errors
    //! Returns error when no solution could be found
    if solboard.solved() {
        return Result::Ok(vec![]);
    }
    let mut stack = BoardStateIterator::new(solboard.clone())
        .unique()
        .avoid_loops();
    while let Option::Some(current_board) = stack.next() {
        if current_board.board().solved() {
            return Result::Ok(current_board.action_stack().collect());
        }
    }
    return Result::Err(Error {});
}
