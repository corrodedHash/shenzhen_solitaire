use actions::{Bunkerize, DragonKill, Goal, HuaKill, Move};
use board::{CardType, FieldPosition};
use std::convert::TryFrom;

fn node_name(index: usize) -> String {
    return format!("action_{:04}", index);
}

/// Position on top of this position (increments `position.row_index` by one)
pub fn top_card(position: &FieldPosition) -> FieldPosition {
    return FieldPosition::new(position.column(), position.row() + 1);
}

pub fn column_range(position: &FieldPosition, count: usize) -> Vec<FieldPosition> {
    return (0..count)
        .map(|i| {
            return FieldPosition::new(
                position.column(),
                position.row() + u8::try_from(i).unwrap(),
            );
        })
        .collect();
}

pub fn get_all_sources(action: actions::All) -> Vec<board::PositionNoGoal> {
    match action {
        actions::All::Bunkerize(Bunkerize {
            bunker_slot_index,
            to_bunker,
            field_position,
            ..
        }) => {
            if to_bunker {
                return vec![board::PositionNoGoal::Field(field_position)];
            } else {
                return vec![board::PositionNoGoal::Bunker {
                    slot_index: bunker_slot_index,
                }];
            }
        }
        actions::All::DragonKill(DragonKill { source, .. }) => {
            return source.to_vec();
        }
        actions::All::Goal(Goal { source, .. }) => {
            return vec![source];
        }
        actions::All::HuaKill(HuaKill { field_position }) => {
            return vec![board::PositionNoGoal::Field(field_position)]
        }
        actions::All::Move(move_action) => {
            return column_range(&move_action.source, usize::from(move_action.stack_len()))
                .into_iter()
                .map(board::PositionNoGoal::Field)
                .collect()
        }
    }
}

pub fn get_all_top_sources(action: &actions::All) -> Vec<board::PositionNoGoal> {
    if let actions::All::Move(move_action) = &action {
        return vec![board::PositionNoGoal::Field(FieldPosition::new(
            move_action.source.column(),
            move_action.source.row() + move_action.stack_len() - 1,
        ))];
    } else {
        return get_all_sources(action.clone());
    };
}

pub fn get_all_bottom_sources(action: &actions::All) -> Vec<board::PositionNoGoal> {
    if let actions::All::Move(Move { source, .. }) = &action {
        return vec![board::PositionNoGoal::Field(*source)];
    } else {
        return get_all_sources(action.clone());
    };
}

pub fn get_all_cards(action: &actions::All) -> Vec<board::CardType> {
    match action {
        actions::All::Bunkerize(Bunkerize { card, .. }) => return vec![card.add_hua()], /* Does this actually work? */
        actions::All::DragonKill(DragonKill { card, .. }) => {
            return vec![
                CardType::Special(card.clone()),
                CardType::Special(card.clone()),
                CardType::Special(card.clone()),
                CardType::Special(card.clone()),
            ]
        }
        actions::All::Goal(Goal { card, .. }) => return vec![CardType::Number(card.clone())],
        actions::All::HuaKill(_) => return vec![CardType::Hua],
        actions::All::Move(move_action) => return move_action.cards(),
    }
}

pub fn get_destination(action: &actions::All) -> Option<board::Position> {
    match action {
        actions::All::Bunkerize(Bunkerize {
            field_position,
             to_bunker,
            bunker_slot_index,
            ..
        }) => {
            if *to_bunker {
                return Option::Some(board::Position::Bunker {
                    slot_index: *bunker_slot_index,
                });
            } else {
                return Option::Some(board::Position::Field(*field_position));
            }
        }
        actions::All::DragonKill(DragonKill {
            destination_slot_index,
            ..
        }) => {
            return Option::Some(board::Position::Bunker {
                slot_index: *destination_slot_index,
            });
        }
        actions::All::Goal(Goal {
            goal_slot_index, ..
        }) => {
            return Option::Some(board::Position::Goal {
                slot_index: *goal_slot_index,
            });
        }
        actions::All::HuaKill(_) => return Option::None,
        actions::All::Move(Move { destination, .. }) => {
            return Option::Some(board::Position::Field(*destination));
        }
    }
}

/// Returns the destination of a move, or the topmost card in its destination when moving multiple cards
pub fn get_top_destination(action: actions::All) -> Option<board::Position> {
    if let actions::All::Move(move_action) = action {
        return Option::Some(board::Position::Field(FieldPosition::new(
            move_action.destination.column(),
            move_action.destination.row() + move_action.stack_len() - 1,
        )));
    } else {
        return get_destination(&action);
    };
}

pub fn get_all_destinations(action: actions::All) -> Vec<board::Position> {
    if let actions::All::Move(move_action) = action {
        return column_range(
            &move_action.destination,
            usize::from(move_action.stack_len()),
        )
        .into_iter()
        .map(board::Position::Field)
        .collect();
    } else {
        return get_destination(&action).into_iter().collect();
    };
}

pub fn search_parent_tree<F>(
    actions: &[actions::All],
    current_action: usize,
    predicate: F,
) -> Option<(usize, &actions::All)>
where
    F: Fn(&actions::All) -> bool,
{
    return actions
        .iter()
        .enumerate()
        .take(current_action)
        .rev()
        .find(|&(_, action)| return predicate(action));
}
