use super::relation::{
    get_clear_parents, get_destination_parent, get_goal_parent, get_move_parents,
};

#[derive(Debug, Copy, Clone, PartialEq)]
pub enum RelationType {
    Move,
    Unblock,
    Clear,
    Socket,
    Goal,
}

impl std::fmt::Display for RelationType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let stringed = match self {
            Self::Move => "Move",
            Self::Unblock => "Unblock",
            Self::Clear => "Clear",
            Self::Socket => "Socket",
            Self::Goal => "Goal",
        };
        return write!(f, "{}", stringed);
    }
}
pub type ActionGraph = petgraph::stable_graph::StableDiGraph<actions::All, RelationType>;

pub fn to_graph(actions: &[actions::All]) -> ActionGraph {
    let mut x = ActionGraph::new();

    macro_rules! relations {
        ($actions:expr, $index: expr, $( $x:expr, $y: expr ),*) => {{
            [
                $(
                    ($x)($actions, $index).into_iter().map(|b| return (b, $y)).collect::<Vec<(usize, RelationType)>>(),
                )*
            ]
        }};
    }
    // can you ActionGraph::from_elements here
    for (index, action) in actions.iter().enumerate() {
        let current_node = x.add_node(action.clone());

        let relations = relations!(
            actions,
            index,
            get_move_parents,
            RelationType::Move,
            get_clear_parents,
            RelationType::Clear,
            get_goal_parent,
            RelationType::Goal
        );
        for (parent, relation) in relations.iter().flatten() {
            x.add_edge(
                petgraph::stable_graph::NodeIndex::new(*parent),
                current_node,
                *relation,
            );
        }
        if let Option::Some((parent, relation)) = get_destination_parent(actions, index) {
            x.add_edge(
                petgraph::stable_graph::NodeIndex::new(parent),
                current_node,
                relation,
            );
        }
    }
    return x;
}

pub fn from_graph(graph: &ActionGraph) -> Vec<actions::All> {
    match petgraph::algo::toposort(graph, Option::None) {
        Ok(topo_actions) => {
            let topo_actions = topo_actions
                .into_iter()
                .map(|index| return graph.node_weight(index).unwrap().clone())
                .collect::<Vec<actions::All>>();
            return topo_actions;
        }
        Err(c) => panic!(
            "Could not toposort the graph, {:#?}, Graph: {:?}",
            c,
            super::draw_graph(graph, std::path::Path::new("cycle_graph.svg"))
        ),
    }
}
