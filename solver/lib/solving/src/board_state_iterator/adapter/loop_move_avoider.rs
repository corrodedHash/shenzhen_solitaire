use super::super::BoardState;
use super::BoardStateIteratorAdapter;
pub(crate) struct LoopMoveAvoider<T: BoardStateIteratorAdapter> {
    base_iterator: T,
}
impl<T: BoardStateIteratorAdapter> LoopMoveAvoider<T> {
    pub(crate) fn new(base_iterator: T) -> Self {
        return Self { base_iterator };
    }
    fn is_loop_move(state: &BoardState) -> bool {
        let last_action = state.action_stack().rev().next();
        if let Option::Some(actions::All::Move(last_move_action)) = last_action {
            let loop_move = state.action_stack().rev().skip(1).find(|x| {
                if let actions::All::Move(action) = x {
                    return action.cards() == last_move_action.cards();
                } else {
                    return false;
                }
            });
            return loop_move.is_some();
        } else {
            return false;
        }
    }
}
impl<T: BoardStateIteratorAdapter> BoardStateIteratorAdapter for LoopMoveAvoider<T> {
    fn advance(&mut self) {
        while let Option::Some(mut state) = self.base_iterator.next() {
            if !Self::is_loop_move(&state) {
                return;
            }
            state.kill();
        }
    }
    fn get(&mut self) -> Option<BoardState> {
        return self.base_iterator.get();
    }
}
