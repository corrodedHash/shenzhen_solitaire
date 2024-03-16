#[derive(Clone, Debug)]
pub(super) struct StackFrame {
    all_options: Vec<actions::All>,
    options_iter: usize,
    child_tainted: bool,
}
impl StackFrame {
    pub(super) fn new(actions: Vec<actions::All>) -> Self {
        return Self {
            all_options: actions,
            child_tainted: false,
            options_iter: 0,
        };
    }
    pub(super) fn get(&self) -> Option<&actions::All> {
        if self.options_iter >= self.all_options.len() {
            return Option::None;
        }
        return Option::Some(&self.all_options[self.options_iter]);
    }
    pub(super) fn advance(&mut self) {
        self.options_iter += 1;
        self.child_tainted = false;
    }
    pub(super) fn next(&mut self) -> Option<&actions::All> {
        self.advance();
        return self.get();
    }
    pub(super) fn taint_child(&mut self) {
        assert_eq!(self.child_tainted, false);
        self.child_tainted = true;
    }
    pub(super) fn child_tainted(&self) -> bool {
        return self.child_tainted;
    }
}
