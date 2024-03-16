use super::super::BoardState;
use super::BoardStateIteratorAdapter;

pub(crate) struct Unique<T> {
    base_iterator: T,
    known_boards: std::collections::HashSet<board::BoardEqHash>,
}
impl<T> Unique<T> {
    pub(crate) fn new(base_iterator: T) -> Self {
        return Self {
            base_iterator,
            known_boards: std::collections::HashSet::new(),
        };
    }
}
impl<T: BoardStateIteratorAdapter> BoardStateIteratorAdapter for Unique<T> {
    fn get(&mut self) -> Option<BoardState> {
        return self.base_iterator.get();
    }
    fn advance(&mut self) {
        while let Option::Some(mut nextboard) = self.base_iterator.next() {
            let eq_hash = nextboard.board().equivalence_hash();
            if !self.known_boards.contains(&eq_hash) {
                self.known_boards.insert(eq_hash);
                return;
            }
            nextboard.kill();
        }
    }
}
