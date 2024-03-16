use super::action_board::ActionBoard;
use super::stack_frame::StackFrame;

#[derive(Debug)]
pub(crate) struct BoardState<'a> {
    state_it: &'a mut BoardStateIterator,
}
impl<'a> BoardState<'a> {
    pub(crate) fn new(state_it: &'a mut BoardStateIterator) -> Self {
        return Self { state_it };
    }
    pub(crate) fn board(&'a self) -> &'a board::Board {
        return self.state_it.board.board();
    }
    pub(crate) fn action_stack(
        &'a self,
    ) -> Box<dyn std::iter::DoubleEndedIterator<Item = actions::All> + 'a> {
        return self.state_it.action_stack();
    }
    pub(crate) fn kill(&'a mut self) {
        if let Option::Some(node) = self.state_it.stack.last_mut() {
            node.taint_child();
        }
    }
}

#[derive(Clone, Debug)]
pub(crate) struct BoardStateIterator {
    board: ActionBoard,
    stack: Vec<StackFrame>,
}

impl BoardStateIterator {
    pub(crate) fn new(board: board::Board) -> Self {
        let mut result = Self {
            board: ActionBoard::new(board),
            stack: Vec::new(),
        };
        let actions = actions::possibilities::filter_actions(result.board.board());
        if !actions.is_empty() {
            result.push(actions);
        }
        return result;
    }

    fn unwind(&mut self) {
        for i in (0..self.stack.len()).rev() {
            self.board.pop();
            if let Option::Some(action) = self.stack[i].next() {
                self.board.push(action.clone());
                return;
            }
            self.stack.pop();
        }
    }

    fn pop(&mut self) {
        if self.stack.is_empty() {
            return;
        }
        assert_ne!(self.stack.pop().unwrap().get(), Option::None);
        self.board.pop();
        self.stack.pop();
        self.unwind();
    }

    fn push(&mut self, actions: Vec<actions::All>) {
        assert!(!actions.is_empty());
        self.board.push(actions.first().unwrap().clone());
        self.stack.push(StackFrame::new(actions));
    }

    fn action_stack<'a>(
        &'a self,
    ) -> Box<dyn std::iter::DoubleEndedIterator<Item = actions::All> + 'a> {
        return Box::new(self.stack.iter().map(|x| return x.get().unwrap().clone()));
    }

    pub(crate) fn get(&mut self) -> Option<BoardState> {
        if self.stack.is_empty() {
            return Option::None;
        }
        return Option::Some(BoardState::new(self));
    }

    pub(crate) fn next(&mut self) -> Option<BoardState> {
        self.advance();
        return self.get();
    }
    
    pub(crate) fn advance(&mut self) {
        if let Option::Some(node) = self.stack.last() {
            if node.child_tainted() {
                return self.unwind();
            }
        }
        if let Option::Some(current_board) = self.get() {
            let actions = actions::possibilities::filter_actions(current_board.board());
            if actions.is_empty() {
                return self.unwind();
            }
            self.push(actions);
        }
    }
}
