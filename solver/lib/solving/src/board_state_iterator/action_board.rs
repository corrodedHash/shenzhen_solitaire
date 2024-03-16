#[derive(Clone, Debug)]
pub(super) struct ActionBoard {
    board: board::Board,
    stack: Vec<actions::All>,
}

impl ActionBoard {
    pub(super) fn new(board: board::Board) -> Self {
        return Self {
            board,
            stack: Vec::new(),
        };
    }
    pub(super) fn push(&mut self, action: actions::All) {
        action.apply(&mut self.board);
        self.stack.push(action);
        debug_assert_eq!(self.board.check(), Result::Ok(()));
    }
    pub(super) fn pop(&mut self) -> Option<actions::All> {
        if let Option::Some(action) = self.stack.pop() {
            action.undo(&mut self.board);
            debug_assert_eq!(self.board.check(), Result::Ok(()));
            return Option::Some(action);
        }
        return Option::None;
    }
    pub(super) const fn board(&self) -> &board::Board {
        return &self.board;
    }
}
