use super::{
    graph_entity::{from_graph, to_graph, ActionGraph, RelationType},
    util::{get_all_cards, get_all_sources},
};

use actions::{Bunkerize, DragonKill, Goal, Move};
use board::PositionNoGoal;
use std::collections::HashSet;

use petgraph::visit::{EdgeRef, IntoNodeReferences};

pub fn merge_actions(
    descendant_action: &actions::All,
    parent_action: &actions::All,
) -> Result<actions::All, String> {
    debug_assert_eq!(
        get_all_cards(descendant_action),
        get_all_cards(parent_action)
    );
    match descendant_action {
        actions::All::Bunkerize(action) => {
            let parent_source = get_all_sources(parent_action.clone());
            if parent_source.len() != 1 {
                return Result::Err("Only operates on parents with one source".to_string());
            }
            let parent_source = &parent_source[0];
            if action.to_bunker {
                match parent_source {
                    PositionNoGoal::Field(parent_field) => {
                        return Result::Ok(actions::All::Bunkerize(Bunkerize {
                            field_position: *parent_field,
                            ..action.clone()
                        }));
                    }
                    PositionNoGoal::Bunker { .. } => {
                        return Result::Err("Cannot merge non field move to bunkerize".to_string());
                    }
                }
            } else {
                match parent_source {
                    PositionNoGoal::Field(parent_field) => {
                        return Result::Ok(actions::All::Move(Move::new(
                            *parent_field,
                            action.field_position,
                            &[action.card.add_hua()],
                        )));
                    }
                    PositionNoGoal::Bunker { .. } => panic!(
                        "How can you have two debunkerize actions after following each other?"
                    ),
                }
            }
        }
        actions::All::DragonKill(_) => return Result::Err("Not implemented".to_string()),
        actions::All::Goal(action) => {
            let parent_source = get_all_sources(parent_action.clone());
            if parent_source.len() != 1 {
                return Result::Err("Only operates on parents with one source".to_string());
            }
            let parent_source = parent_source.into_iter().next().unwrap();
            return Result::Ok(actions::All::Goal(Goal {
                source: parent_source,
                ..action.clone()
            }));
        }
        actions::All::HuaKill(_) => {
            panic!("How do you have a move parent for a hua kill?");
        }
        actions::All::Move(action) => {
            let parent_source = get_all_sources(parent_action.clone());
            if parent_source.len() != 1 {
                return Result::Err("Only operates on parents with one source".to_string());
            }
            let parent_source = parent_source.into_iter().next().unwrap();
            match parent_source {
                PositionNoGoal::Field(parent_field) => {
                    let mut result_action = action.clone();
                    result_action.source = parent_field;
                    return Result::Ok(actions::All::Move(result_action));
                }
                PositionNoGoal::Bunker { slot_index } => {
                    assert!(action.stack_len() == 1);
                    return Result::Ok(actions::All::Bunkerize(Bunkerize {
                        bunker_slot_index: slot_index,
                        card: action.cards()[0].remove_hua(),
                        field_position: action.destination,
                        to_bunker: false,
                    }));
                }
            }
        }
    }
}

fn get_parents(
    graph: &ActionGraph,
    index: petgraph::stable_graph::NodeIndex,
) -> Vec<petgraph::stable_graph::NodeIndex> {
    let parent = graph
        .edges_directed(index, petgraph::Direction::Incoming)
        .filter_map(|x| {
            if x.weight() == &RelationType::Move {
                return Option::Some(x.source());
            } else {
                return Option::None;
            }
        });
    return parent.collect();
}

fn socket_for(
    graph: &ActionGraph,
    index: petgraph::stable_graph::NodeIndex,
) -> Vec<petgraph::stable_graph::NodeIndex> {
    return graph
        .edges_directed(index, petgraph::Direction::Outgoing)
        .filter_map(|x| {
            if x.weight() == &RelationType::Socket {
                return Option::Some(x.target());
            } else {
                return Option::None;
            }
        })
        .collect();
}

/// # Relations when merging nodes
/// - To parent:
///     - Clearing     -> To merged node, needs to be cleared no matter destination
///     - Unblocking   -> remove
///     - Socketing    -> remove
/// - From parent:
///     - Clearing     -> From merged node, clears no matter of destination
///     - Unblocking   -> From merged node, when to child both nodes can be removed
///     - Socketing    -> Abort merging, probably needs to be still there
/// - To child:
///     - Clearing     -> Shouldn't happen when there is no traffic between parent
///     - Unblocking   -> Still required, keep
///     - Socketing    -> Still required, keep
/// - From child:
///     - Clearing     -> Should cancel the socket to parent, remove
///     - Unblocking   -> Join with incoming unblocking of parent, otherwise cell was always empty
///     - Socketing    -> keep, destination stays the same, as such still sockets the target of the relation
fn merge_edges(
    graph: &mut ActionGraph,
    parent: petgraph::stable_graph::NodeIndex,
    child: petgraph::stable_graph::NodeIndex,
) {
    let mut addable_edges = Vec::new();
    let mut removable_edges = Vec::new();
    let mut unblock_parent = Option::None;
    let mut socket_parent = Option::None;
    for parent_dependent in graph.edges_directed(parent, petgraph::Direction::Incoming) {
        match parent_dependent.weight() {
            RelationType::Socket => socket_parent = Option::Some(parent_dependent.source()),
            RelationType::Unblock => unblock_parent = Option::Some(parent_dependent.source()),
            RelationType::Move | RelationType::Clear => {
                addable_edges.push((parent_dependent.source(), child, *parent_dependent.weight()));
            }
            RelationType::Goal => panic!("Merging actions does not work on goal actions"),
        }
    }
    for parent_dependent in graph.edges_directed(parent, petgraph::Direction::Outgoing) {
        match parent_dependent.weight() {
            RelationType::Move => {
                debug_assert_eq!(parent_dependent.target(), child);
            }
            RelationType::Unblock | RelationType::Clear => {
                if parent_dependent.target() != child {
                    addable_edges.push((
                        child,
                        parent_dependent.target(),
                        *parent_dependent.weight(),
                    ));
                }
            }
            RelationType::Socket => {
                panic!("Cannot merge a parent which provides a socket for an action")
            }
            RelationType::Goal => panic!("Merging actions does not work on goal actions"),
        }
    }
    for child_dependent in graph.edges_directed(child, petgraph::Direction::Incoming) {
        match child_dependent.weight() {
            RelationType::Move => {
                if get_all_cards(&graph[child]).len() == 1 {
                    debug_assert_eq!(child_dependent.source(), parent);
                }
            }
            RelationType::Clear => {
                if get_all_cards(&graph[child]).len() == 1 {
                    panic!("What is being cleared between the parent and the child when no other interaction happened in between?\n{:?} {}\n{:?} {}",
                parent, graph.node_weight(parent).unwrap(), child, graph.node_weight(child).unwrap());
                }
            }
            RelationType::Unblock | RelationType::Socket | RelationType::Goal => {}
        }
    }
    for child_dependent in graph.edges_directed(child, petgraph::Direction::Outgoing) {
        match child_dependent.weight() {
            RelationType::Goal | RelationType::Move | RelationType::Socket => {}
            RelationType::Clear => removable_edges.push(child_dependent.id()),
            RelationType::Unblock => {
                debug_assert!(
                    !(unblock_parent.is_some() && socket_parent.is_some()),
                    "Both unblock {:?} and socket {:?} parent for {:?}",
                    unblock_parent.unwrap(),
                    socket_parent.unwrap(),
                    child
                );
                if let Option::Some(parent_unblocker) = unblock_parent {
                    addable_edges.push((
                        parent_unblocker,
                        child_dependent.target(),
                        *child_dependent.weight(),
                    ));
                    removable_edges.push(child_dependent.id());
                }
                if let Option::Some(parent_socket) = socket_parent {
                    addable_edges.push((
                        parent_socket,
                        child_dependent.target(),
                        RelationType::Socket,
                    ));
                    removable_edges.push(child_dependent.id());
                }
            }
        }
    }
    for (source, target, weight) in addable_edges {
        graph.add_edge(source, target, weight);
    }
    for edge in removable_edges {
        graph.remove_edge(edge);
    }
    graph.remove_node(parent);
}

pub fn try_merge(
    graph: &mut ActionGraph,
    parent: petgraph::stable_graph::NodeIndex,
    child: petgraph::stable_graph::NodeIndex,
) -> bool {
    if let Result::Ok(new_action) = merge_actions(
        graph.node_weight(child).unwrap(),
        graph.node_weight(parent).unwrap(),
    ) {
        *graph.node_weight_mut(child).unwrap() = new_action;
    } else {
        return false;
    }
    merge_edges(graph, parent, child);
    return true;
}

/// Remove an action from the graph which has no impact on the board
pub fn delete_null_node(graph: &mut ActionGraph, null_node: petgraph::stable_graph::NodeIndex) {
    let join_edge = |graph: &mut ActionGraph, reltype: RelationType| {
        let incoming_edge = graph
            .edges_directed(null_node, petgraph::Direction::Incoming)
            .find_map(|x| {
                if x.weight() == &reltype {
                    return Option::Some(x.source());
                } else {
                    return Option::None;
                }
            });
        let outgoing_edge = graph
            .edges_directed(null_node, petgraph::Direction::Outgoing)
            .find_map(|x| {
                if x.weight() == &reltype {
                    return Option::Some(x.target());
                } else {
                    return Option::None;
                }
            });
        if let Option::Some(incoming_edge) = incoming_edge {
            if let Option::Some(outgoing_edge) = outgoing_edge {
                graph.add_edge(incoming_edge, outgoing_edge, reltype);
            }
        }
    };
    join_edge(graph, RelationType::Move);
    join_edge(graph, RelationType::Unblock);
    for weird_edge in graph
        .edges_directed(null_node, petgraph::Direction::Incoming)
        .chain(graph.edges_directed(null_node, petgraph::Direction::Outgoing))
        .filter(|x| {
            return x.weight() != &RelationType::Move && x.weight() != &RelationType::Unblock;
        })
    {
        eprintln!(
            "Weird edge while deleting null node\n{}\n{:?} {}\n{:?} {}\n{:?} {}",
            weird_edge.weight(),
            null_node,
            graph.node_weight(null_node).unwrap(),
            weird_edge.source(),
            graph.node_weight(weird_edge.source()).unwrap(),
            weird_edge.target(),
            graph.node_weight(weird_edge.target()).unwrap(),
        )
    }
    graph.remove_node(null_node);
}

fn try_replace_bunker_slot(
    graph: &mut ActionGraph,
    index: petgraph::stable_graph::NodeIndex,
    parent_slot: u8,
    child_slot: u8,
) {
    let swap_slot = |slot| {
        if slot == child_slot {
            return parent_slot;
        } else if slot == parent_slot {
            return child_slot;
        } else {
            return slot;
        }
    };
    match graph.node_weight_mut(index).unwrap() {
        actions::All::Bunkerize(Bunkerize {
            bunker_slot_index, ..
        }) => {
            *bunker_slot_index = swap_slot(*bunker_slot_index);
        }
        actions::All::DragonKill(DragonKill {
            source,
            destination_slot_index,
            ..
        }) => {
            let slot_index = source.iter_mut().filter_map(|x| {
                if let board::PositionNoGoal::Bunker { slot_index } = x {
                    return Option::Some(slot_index);
                } else {
                    return Option::None;
                }
            });
            for current_slot in slot_index {
                *current_slot = swap_slot(*current_slot);
            }
            *destination_slot_index = swap_slot(*destination_slot_index);
        }
        actions::All::Goal(Goal { source, .. }) => {
            if let PositionNoGoal::Bunker { slot_index } = source {
                *slot_index = swap_slot(*slot_index);
            }
        }
        actions::All::HuaKill(_) | actions::All::Move(_) => {
            return;
        }
    }
}

fn flip_bunker_slots(
    graph: &mut ActionGraph,
    index: petgraph::stable_graph::NodeIndex,
    parent_slot: u8,
    child_slot: u8,
) {
    let unblock_move_graph = petgraph::visit::EdgeFiltered::from_fn(
        &*graph,
        &|x: petgraph::stable_graph::EdgeReference<RelationType>| match x.weight() {
            RelationType::Move | RelationType::Unblock => return true,
            RelationType::Clear | RelationType::Socket | RelationType::Goal => return false,
        },
    );
    let mut visitor = petgraph::visit::Dfs::new(&unblock_move_graph, index);

    while let Option::Some(index) = visitor.next(&*graph) {
        try_replace_bunker_slot(graph, index, parent_slot, child_slot);
    }
}

fn is_bunker_loop(
    graph: &ActionGraph,
    parent: petgraph::stable_graph::NodeIndex,
    child: petgraph::stable_graph::NodeIndex,
) -> bool {
    if let actions::All::Bunkerize(Bunkerize {
        to_bunker: parent_to_bunker,
        ..
    }) = graph.node_weight(parent).unwrap()
    {
        if let actions::All::Bunkerize(Bunkerize { to_bunker, .. }) =
            graph.node_weight(child).unwrap()
        {
            if !parent_to_bunker && *to_bunker {
                // if *parent_slot == *bunker_slot_index {
                //     return Option::Some((*parent_slot, *bunker_slot_index));
                // }
                return true;
            }
        }
    }
    return false;
}

fn is_field_loop(
    graph: &ActionGraph,
    parent: petgraph::stable_graph::NodeIndex,
    child: petgraph::stable_graph::NodeIndex,
) -> bool {
    if let actions::All::Move(move_action) = graph.node_weight(parent).unwrap() {
        if let actions::All::Move(child_move_action) = graph.node_weight(child).unwrap() {
            debug_assert_eq!(move_action.cards(), child_move_action.cards());
            debug_assert_eq!(move_action.destination, child_move_action.source);
            debug_assert_eq!(move_action.stack_len(), 1);
            return move_action.source == child_move_action.destination;
        }
    }
    return false;
}

pub fn merge_step(mut graph: ActionGraph) -> ActionGraph {
    let mut used_nodes = HashSet::new();
    let mut mergeable = Vec::new();
    let mut loop_deletion = Vec::new();
    let mut bunker_loop_deletion = Vec::new();
    for (index, _action) in graph.node_references() {
        if used_nodes.contains(&index) {
            continue;
        }
        let parents = get_parents(&graph, index);
        if parents.len() != 1 {
            continue;
        }
        let parent = parents.into_iter().next().unwrap();
        if used_nodes.contains(&parent) {
            continue;
        }

        if get_all_cards(graph.node_weight(parent).unwrap()).len() > 1 {
            continue;
        }
        if get_all_cards(graph.node_weight(index).unwrap()).len() > 1 {
            continue;
        }
        if socket_for(&graph, parent)
            .into_iter()
            .any(|x| return x != index)
        {
            continue;
        }
        let filtered_graph = petgraph::visit::EdgeFiltered::from_fn(&graph, |x| {
            return !(x.source() == parent && x.target() == index);
        });
        if petgraph::algo::has_path_connecting(&filtered_graph, parent, index, Option::None) {
            continue;
        }
        if is_bunker_loop(&graph, parent, index) {
            bunker_loop_deletion.push((parent, index));
        } else if is_field_loop(&graph, parent, index) {
            loop_deletion.push((parent, index));
        } else {
            mergeable.push((parent, index));
        }
        used_nodes.insert(parent);
        used_nodes.insert(index);
    }
    for (parent, child) in mergeable {
        try_merge(&mut graph, parent, child);
    }
    for (parent, child) in loop_deletion {
        merge_edges(&mut graph, parent, child);
        delete_null_node(&mut graph, child);
    }
    for (parent, child) in bunker_loop_deletion {
        let parent_slot = if let actions::All::Bunkerize(Bunkerize {
            bunker_slot_index,
            to_bunker,
            ..
        }) = &graph[parent]
        {
            assert!(!*to_bunker);
            *bunker_slot_index
        } else {
            panic!("Should be bunkerize action")
        };
        let child_slot = if let actions::All::Bunkerize(Bunkerize {
            bunker_slot_index,
            to_bunker,
            ..
        }) = &graph[child]
        {
            assert!(*to_bunker);
            *bunker_slot_index
        } else {
            panic!("Should be bunkerize action")
        };
        flip_bunker_slots(&mut graph, parent, parent_slot, child_slot);
        merge_edges(&mut graph, parent, child);
        delete_null_node(&mut graph, child);
    }

    return graph;
}

fn fix_dragonkill_destination(actions: &[actions::All]) -> Vec<actions::All> {
    let graph = to_graph(actions);
    let result = graph
        .node_indices()
        .map(|node| return graph.node_weight(node).unwrap().clone())
        .collect();
    return result;
}

fn fix_goal_ordering(actions: &[actions::All]) -> Vec<actions::All> {
    return actions.to_vec();
}

#[must_use]
pub fn optimize(actions: &[actions::All]) -> Vec<actions::All> {
    let mut graph = to_graph(actions);
    let mut last_length = graph.node_count();
    loop {
        graph = merge_step(graph);
        if graph.node_count() == last_length {
            break;
        }
        last_length = graph.node_count();
    }

    let optimized_sequence = from_graph(&graph);
    return fix_goal_ordering(&fix_dragonkill_destination(&optimized_sequence));
}
