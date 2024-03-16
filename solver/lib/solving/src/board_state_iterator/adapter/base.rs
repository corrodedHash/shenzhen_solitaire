use super::{ super::BoardState};
use crate::board_state_iterator::BoardStateIterator;
use super::loop_move_avoider::LoopMoveAvoider;
pub(crate) trait BoardStateIteratorAdapter {
    fn advance(&mut self);
    fn get(&mut self) -> Option<BoardState>;
    fn next(&mut self) -> Option<BoardState> {
        self.advance();
        return self.get();
    }
    fn unique(self) -> super::Unique<Self>
    where
        Self: Sized,
    {
      return super::Unique::new(self);
    }

    fn avoid_loops(self) -> LoopMoveAvoider<Self>
    where Self: Sized,
    {
      return LoopMoveAvoider::new(self);
    }
}

impl BoardStateIteratorAdapter for BoardStateIterator {
    fn advance(&mut self) {
        self.advance();
    }
    fn get(&mut self) -> Option<BoardState> {
        return self.get();
    }
}
