use super::{
    graph_entity::RelationType,
    util::{
        get_all_bottom_sources, get_all_destinations, get_all_sources, get_all_top_sources,
        get_destination, get_top_destination, search_parent_tree, top_card,
    },
};
use actions::{Goal, Move};
use board::PositionNoGoal;
pub fn get_move_parents(actions: &[actions::All], current_action: usize) -> Vec<usize> {
    let result = get_all_sources(actions[current_action].clone())
        .into_iter()
        .filter_map(|cur_source_pos| {
            let is_move_parent = |other_action: &actions::All| {
                let destinations =
                    get_all_destinations(other_action.clone())
                        .into_iter()
                        .any(|cur_dest_pos| {
                            return cur_dest_pos == cur_source_pos;
                        });
                return destinations;
            };

            let source_action = search_parent_tree(actions, current_action, is_move_parent);
            return source_action.map(|(index, _)| return index);
        })
        .collect();
    return result;
}
fn get_unblocking_parent(actions: &[actions::All], current_action: usize) -> Option<usize> {
    let destination = get_destination(&actions[current_action])?;
    let is_unblocking = |other_action: &actions::All| {
        return get_all_sources(other_action.clone())
            .into_iter()
            .any(|source| return source == destination);
    };
    return search_parent_tree(actions, current_action, is_unblocking)
        .filter(|&(_, found_action)| {
            if let actions::All::Move(Move { ref source, .. }) = found_action {
                return board::Position::Field(*source) == destination;
            }
            return true;
        })
        .map(|(index, _)| return index);
}

fn get_socket_parent(actions: &[actions::All], current_action: usize) -> Option<usize> {
    let top_action = get_destination(&actions[current_action]);

    if let Option::Some(board::Position::Field(top_action)) = top_action {
        let is_socket = |action: &actions::All| {
            let socket_destination = get_top_destination(action.clone());
            if let Option::Some(board::Position::Field(destination)) = socket_destination {
                return top_card(&destination) == top_action;
            }
            return false;
        };
        let added_socket =
            search_parent_tree(actions, current_action, is_socket).map(|(index, _)| {
                return index;
            });
        let unblocking_parent = get_unblocking_parent(actions, current_action);
        if added_socket < unblocking_parent {
            return Option::None;
        } else {
            return added_socket;
        }
    }
    return Option::None;
}

pub fn get_destination_parent(
    actions: &[actions::All],
    current_action: usize,
) -> Option<(usize, RelationType)> {
    let socket_parent = get_socket_parent(actions, current_action);
    let unblock_parent = get_unblocking_parent(actions, current_action);
    if socket_parent.is_none() && unblock_parent.is_none() {
        return Option::None;
    } else if socket_parent > unblock_parent {
        return Option::Some((socket_parent.unwrap(), RelationType::Socket));
    } else {
        return Option::Some((unblock_parent.unwrap(), RelationType::Unblock));
    }
}

/// Actions which moved cards on top of other cards away
pub fn get_clear_parents(actions: &[actions::All], current_action: usize) -> Vec<usize> {
    let filter_fields = |x: PositionNoGoal| {
        if let PositionNoGoal::Field(f) = x {
            return Some(f);
        } else {
            return None;
        }
    };
    let source_positions = get_all_top_sources(&actions[current_action]);

    let parents: Vec<usize> = source_positions
        .into_iter()
        .filter_map(|current_source_pos| {
            let current_source_pos = filter_fields(current_source_pos)?;
            let latest_moves = get_move_parents(actions, current_action);
            let latest_move = if let actions::All::DragonKill(_) = actions[current_action] {
                latest_moves
                    .into_iter()
                    .find(|index| {
                        return get_destination(&actions[*index])
                            == Option::Some(board::Position::Field(current_source_pos));
                    })
                    .unwrap_or(0)
            } else {
                latest_moves.into_iter().max().unwrap_or(0)
            };
            let is_clearing = move |other_action: &actions::All| {
                let sources = get_all_bottom_sources(other_action);
                let clear_parent = sources
                    .into_iter()
                    .filter_map(filter_fields)
                    .any(|cur_dest_pos| return top_card(&current_source_pos) == cur_dest_pos);

                return clear_parent;
            };
            return search_parent_tree(actions, current_action, is_clearing)
                .map(|(index, _)| return index)
                .filter(|index| return *index >= latest_move);
        })
        .collect();
    return parents;
}

pub fn get_goal_parent(actions: &[actions::All], current_action: usize) -> Option<usize> {
    if let actions::All::Goal(Goal { card, .. }) = &actions[current_action] {
        let is_successive_goal = move |other_action: &actions::All| {
            if let actions::All::Goal(Goal {
                card: other_card, ..
            }) = other_action
            {
                return other_card.value + 1 == card.value && other_card.suit == card.suit;
            }
            return false;
        };
        if card.value > 1 {
            let parent_goal = search_parent_tree(actions, current_action, is_successive_goal)
                .map(|(index, _)| return index);
            return parent_goal;
        }
    }
    return Option::None;
}
