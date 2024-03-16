enum SearcherNodeState<'a> {
  Unexplored,
  Exhausted,
  Exploring(Box<SearcherNode<'a>>),
}

struct SearcherNode<'a> {
  children: Vec<SearcherNodeState<'a>>,
  parent: &'a SearcherNodeType<'a>,
  parent_id: usize,
  action: board::actions::All,
}
struct SearcherNodeRoot<'a> {
  children: Vec<SearcherNodeState<'a>>,
}

enum SearcherNodeType<'a> {
  Root(SearcherNodeRoot<'a>),
  Normal(SearcherNode<'a>),
}

fn toSearcherNodes<'a>(
  parent: &'a SearcherNodeType<'a>,
  actions: Vec<board::actions::All>,
) -> Vec<SearcherNodeState<'a>> {
  return actions
      .into_iter()
      .enumerate()
      .map(|(index, action)| {
          return SearcherNodeState::Exploring(Box::new(SearcherNode {
              parent,
              children: vec![],
              parent_id: index,
              action,
          }));
      })
      .collect();
}
struct Searcher<'a> {
  root: SearcherNodeRoot<'a>,
  board: board::Board,
  current_node: Option<&'a mut SearcherNodeState<'a>>,
  current_board: board::Board,
}
impl<'a> Searcher<'a> {
  pub(crate) fn new(board: board::Board) -> Self {
      let actions = super::filter_actions(&board, &board::possibilities::all_actions(&board));
      let mut root = SearcherNodeRoot { children: vec![] };
      root.children = toSearcherNodes(&SearcherNodeType::Root(root), actions);

      let mut current_board = board.clone();
      let current_node = root.children.first_mut();
      if let Option::Some(SearcherNodeState::Exploring(action_node)) = current_node {
          action_node.action.apply(&mut current_board);
      }

      return Self {
          root,
          board,
          current_node,
          current_board,
      };
  }
  pub(crate) fn advance(&'a mut self) {
      if let Option::Some(action_node) = self.current_node {
          if let SearcherNodeState::Exploring(expl_action_node) = action_node {
              let actions = super::filter_actions(
                  &self.current_board,
                  &board::possibilities::all_actions(&self.current_board),
              );
              expl_action_node.children =
                  toSearcherNodes(&SearcherNodeType::Normal(**expl_action_node), actions);
          }
      }
  }
  pub(crate) fn get(&'a self) -> Option<&'a board::Board> {
      self.current_node?;
      return Option::Some(&self.current_board);
  }
  pub(crate) fn next(&'a mut self) -> Option<&'a board::Board> {
      self.advance();
      return self.get();
  }
  pub(crate) fn kill_children(&'a mut self) {
  }
}