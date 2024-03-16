use board::{
    Board, BunkerSlot, CardType, CardTypeNoHua, FieldPosition, NumberCard, NumberCardColor,
    PositionNoGoal, SpecialCardType,
};

#[must_use]
pub fn bunkerize_actions(solboard: &Board) -> Vec<crate::All> {
    let first_empty_bunker_index = solboard.bunker.iter().position(|x| match x {
        BunkerSlot::Empty => return true,
        _ => return false,
    });
    if let Option::Some(first_empty_bunker_index) = first_empty_bunker_index {
        return solboard
            .field
            .iter()
            .enumerate()
            .filter_map(|(index, row)| {
                return row
                    .last()
                    .filter(|card| {
                        if let CardType::Hua = card {
                            return false;
                        } else {
                            return true;
                        }
                    })
                    .map(|card| {
                        let field_position = FieldPosition::new(index as u8, (row.len() - 1) as u8);
                        return crate::All::Bunkerize(crate::Bunkerize {
                            field_position,
                            card: card.remove_hua(),
                            bunker_slot_index: first_empty_bunker_index as u8,
                            to_bunker: true,
                        });
                    });
            })
            .collect();
    }
    return Vec::new();
}

fn card_fits(source: &NumberCard, dest: &NumberCard) -> bool {
    return (source.suit != dest.suit) && (source.value + 1 == dest.value);
}

fn fitting_field_number_position(card: &NumberCard, board: &Board) -> Option<FieldPosition> {
    return board.field.iter().enumerate().find_map(|(index, row)| {
        if let Option::Some(CardType::Number(top_card)) = row.last() {
            if card_fits(card, top_card) {
                return Option::Some(FieldPosition::new(index as u8, (row.len()) as u8));
            }
        }
        return Option::None;
    });
}

fn fitting_field_positions(card: &CardType, board: &Board) -> Vec<FieldPosition> {
    let mut result = Vec::new();
    if let CardType::Number(card) = card {
        if let Option::Some(position) = fitting_field_number_position(card, board) {
            result.push(position);
        }
    }
    if let Option::Some(position) =
        (0_u8..)
            .zip(board.field.iter())
            .find_map(|(column_index, slot)| {
                if slot.is_empty() {
                    return Option::Some(FieldPosition::new(column_index, 0));
                } else {
                    return Option::None;
                }
            })
    {
        result.push(position)
    }
    return result;
}

#[must_use]
pub fn debunkerize_actions(solboard: &Board) -> Vec<crate::All> {
    let number_matching_cards =
        (0_u8..)
            .zip(solboard.bunker.iter())
            .filter_map(|(bunker_slot_index, slot)| {
                if let BunkerSlot::Stash(CardTypeNoHua::Number(card)) = slot {
                    return fitting_field_number_position(card, solboard).map(|field_position| {
                        return crate::All::Bunkerize(crate::Bunkerize {
                            card: CardTypeNoHua::Number(card.clone()),
                            field_position,
                            bunker_slot_index,
                            to_bunker: false,
                        });
                    });
                } else {
                    return Option::None;
                }
            });
    let empty_slot = solboard
        .field
        .iter()
        .position(|row| return row.is_empty())
        .map(|column_index| {
            return FieldPosition::new(column_index as u8, 0);
        });
    if let Option::Some(field_position) = empty_slot {
        let empty_slot_cards =
            (0_u8..)
                .zip(solboard.bunker.iter())
                .filter_map(|(bunker_slot_index, slot)| {
                    if let BunkerSlot::Stash(card) = slot {
                        let result = crate::Bunkerize {
                            card: card.clone(),
                            bunker_slot_index,
                            field_position,
                            to_bunker: false,
                        };
                        return Option::Some(crate::All::Bunkerize(result));
                    } else {
                        return Option::None;
                    }
                });

        return number_matching_cards.chain(empty_slot_cards).collect();
    } else {
        return number_matching_cards.collect();
    }
}

struct DragonTracker {
    dragons: [(u8, [PositionNoGoal; 4]); 3],
}
impl DragonTracker {
    fn new() -> Self {
        return Self {
            dragons: [(0, [PositionNoGoal::Bunker { slot_index: 0 }; 4]); 3],
        };
    }

    fn dragon_to_id(dragon: &SpecialCardType) -> u8 {
        return match dragon {
            SpecialCardType::Zhong => 0,
            SpecialCardType::Bai => 1,
            SpecialCardType::Fa => 2,
        };
    }
    fn id_to_dragon(id: u8) -> SpecialCardType {
        return match id {
            0 => SpecialCardType::Zhong,
            1 => SpecialCardType::Bai,
            2 => SpecialCardType::Fa,
            _ => panic!("Dragon id too high"),
        };
    }

    fn push(&mut self, dragon: &SpecialCardType, position: PositionNoGoal) {
        let (ref mut count, ref mut cell) = self.dragons[usize::from(Self::dragon_to_id(dragon))];
        cell[usize::from(*count)] = position;
        *count += 1;
    }

    fn found_dragons(&self) -> impl Iterator<Item = (SpecialCardType, &[PositionNoGoal; 4])> {
        return (0_u8..)
            .zip(self.dragons.iter())
            .filter_map(|(index, (count, positions))| {
                if *count == 4 {
                    return Option::Some((Self::id_to_dragon(index), positions));
                } else {
                    return Option::None;
                }
            });
    }
}

#[must_use]
pub fn dragonkill_actions(solboard: &Board) -> Vec<crate::All> {
    let mut dragon_position = DragonTracker::new();
    for (position, card) in solboard.movable_cards() {
        if let CardType::Special(card) = card {
            dragon_position.push(&card, position);
        }
    }
    let mut result: Vec<crate::All> = Vec::new();
    for (card_type, positions) in dragon_position.found_dragons() {
        let dragon_destination = solboard.bunker.iter().position(|x| {
            return match x {
                BunkerSlot::Empty => true,
                BunkerSlot::Stash(CardTypeNoHua::Special(special_card_type)) => {
                    special_card_type == &card_type
                }
                _ => false,
            };
        });
        if let Option::Some(dragon_destination) = dragon_destination {
            let mut my_positions: [PositionNoGoal; 4] =
                [PositionNoGoal::Bunker { slot_index: 0 }; 4];
            my_positions.clone_from_slice(positions);
            result.push(crate::All::DragonKill(crate::DragonKill {
                card: card_type.clone(),
                source: my_positions,
                destination_slot_index: dragon_destination as u8,
            }));
        }
    }

    return result;
}

fn get_max_stack_count(board: &Board) -> [u8; 8] {
    let mut result = [0; 8];
    for (index, row) in result.iter_mut().zip(&board.field) {
        let row_iterator = row.iter().rev();
        let mut next_row_iterator = row.iter().rev();
        if next_row_iterator.next().is_none() {
            *index = 0;
            continue;
        }
        *index = (row_iterator
            .zip(next_row_iterator)
            .take_while(|(card, bottom_card)| {
                if let (CardType::Number(card), CardType::Number(bottom_card)) = (card, bottom_card)
                {
                    return card_fits(card, bottom_card);
                } else {
                    return false;
                }
            })
            .count()
            + 1) as u8;
    }
    return result;
}

#[must_use]
pub fn field_move_actions(solboard: &Board) -> Vec<crate::All> {
    let max_stack_counts: [u8; 8] = get_max_stack_count(solboard);
    let required_size: u8 = max_stack_counts.iter().cloned().sum();
    let mut result = Vec::with_capacity(usize::from(required_size));
    for ((column_index, row), stack_size) in (0_u8..)
        .zip(solboard.field.iter())
        .zip(max_stack_counts.iter())
        .filter(|(_, size)| return **size > 0)
    {
        for row_index in (row.len() - usize::from(*stack_size)) as u8..(row.len()) as u8 {
            let my_stack = &row
                .get(usize::from(row_index)..row.len())
                .expect("Slicing failed");
            for position in fitting_field_positions(
                my_stack
                    .first()
                    .expect("Stack should at least have one entry"),
                solboard,
            ) {
                result.push(crate::All::Move(crate::Move::new(
                    FieldPosition::new(column_index, row_index),
                    position,
                    my_stack,
                )));
            }
        }
    }
    return result;
}

#[must_use]
pub fn goal_move_actions(solboard: &Board) -> Vec<crate::All> {
    let suit_to_id = |suit: &NumberCardColor| -> u8 {
        return match suit {
            NumberCardColor::Red => 0,
            NumberCardColor::Green => 1,
            NumberCardColor::Black => 2,
        };
    };
    let first_empty_goal_slot_index = (0_u8..)
        .zip(solboard.goal.iter())
        .find_map(|(index, card)| {
            if card.is_none() {
                return Option::Some(index);
            } else {
                return Option::None;
            }
        })
        .unwrap_or(3);
    let mut goal_desired_pos = [(1_u8, first_empty_goal_slot_index); 3];

    for (slot_id, card) in (0_u8..).zip(solboard.goal.iter()) {
        match card {
            Option::Some(NumberCard { value, suit }) => {
                goal_desired_pos[usize::from(suit_to_id(suit))] = (*value + 1, slot_id);
            }
            Option::None => {}
        };
    }
    let mut result = Vec::<crate::All>::new();
    for (position, card) in solboard.movable_cards() {
        if let CardType::Number(card) = card {
            if goal_desired_pos[usize::from(suit_to_id(&card.suit))].0 == card.value {
                result.push(crate::All::Goal(crate::Goal {
                    card: card.clone(),
                    source: position,
                    goal_slot_index: goal_desired_pos[usize::from(suit_to_id(&card.suit))].1,
                }));
            }
        }
    }
    return result;
}

#[must_use]
pub fn huakill_actions(solboard: &Board) -> Vec<crate::All> {
    for (slot_id, field_column) in (0_u8..).zip(solboard.field.iter()) {
        if let Option::Some(CardType::Hua) = field_column.last() {
            return vec![crate::All::HuaKill(crate::HuaKill {
                field_position: FieldPosition::new(slot_id, (field_column.len() - 1) as u8),
            })];
        }
    }
    return Vec::new();
}

#[must_use]
pub fn all_actions(solboard: &Board) -> Vec<crate::All> {
    return [
        &huakill_actions(solboard)[..],
        &dragonkill_actions(solboard)[..],
        &goal_move_actions(solboard)[..],
        &debunkerize_actions(solboard)[..],
        &field_move_actions(solboard)[..],
        &bunkerize_actions(solboard)[..],
    ]
    .concat();
}

#[must_use]
pub fn filter_actions(solboard: &Board) -> Vec<crate::All> {
    let action_list = all_actions(solboard);
    let huakill_action = action_list.iter().find(|x| {
        if let crate::All::HuaKill(_) = x {
            return true;
        } else {
            return false;
        }
    });
    if let Option::Some(action) = huakill_action {
        return vec![action.clone()];
    }
    let mut goal_actions = action_list.iter().filter_map(|x| {
        if let crate::All::Goal(x) = x {
            return Option::Some(x);
        } else {
            return Option::None;
        }
    });
    let minimum_goal = solboard
        .goal
        .iter()
        .map(|x| match x {
            Option::None => return 0,
            Option::Some(card) => return card.value,
        })
        .min()
        .unwrap();
    if let Option::Some(minimum_goal_action) = goal_actions
        .by_ref()
        .min_by(|x, y| return x.card.value.cmp(&y.card.value))
    {
        if minimum_goal_action.card.value <= minimum_goal + 1 {
            return vec![crate::All::Goal(minimum_goal_action.clone())];
        }
    }

    return action_list.to_vec();
}
