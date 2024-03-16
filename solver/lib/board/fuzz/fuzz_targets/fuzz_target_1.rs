#![no_main]
use libfuzzer_sys::fuzz_target;

use board::{Board, CardType};
use enum_iterator::IntoEnumIterator;
use rand::seq::SliceRandom;

struct RandomBytes<'a> {
    data: &'a [u8],
    index: usize,
}

impl<'a> rand::RngCore for RandomBytes<'a> {
    fn next_u32(&mut self) -> u32 {
        if let Option::Some(x) = self.data.get(self.index..self.index + 4) {
            self.index += 4;
            return (u32::from(x[3]) << 24)
                | (u32::from(x[2]) << 16)
                | (u32::from(x[1]) << 8)
                | u32::from(x[0]);
        } else {
            self.index = self.data.len();
            return 0;
        }
    }
    fn next_u64(&mut self) -> u64 {
        return u64::from(self.next_u32()) << 32 | u64::from(self.next_u32());
    }
    fn fill_bytes(&mut self, dest: &mut [u8]) {
        if (self.index >= self.data.len()) || (dest.len() > self.data.len() - self.index) {
            for cell in dest.iter_mut() {
                *cell = 0;
            }
        }
        if dest.len() < self.data.len() - self.index {
            dest.clone_from_slice(&self.data[self.index..self.index + dest.len()]);
            self.index += dest.len()
        }
    }
    fn try_fill_bytes(&mut self, dest: &mut [u8]) -> Result<(), rand::Error> {
        self.fill_bytes(dest);
        return Result::Ok(());
    }
}

fn correct_board_permutation(data: &[u8]) -> Board {
    if let Option::Some(remove_info) = data.get(0..2) {
        let remove_info: u16 = u16::from(remove_info[1]) << 8 | u16::from(remove_info[0]);
        let mut result = Board::default();
        let mut whole_vec = Vec::<CardType>::new();
        if remove_info & 1 == 1 {
            result.hua_set = true;
        } else {
            whole_vec.push(CardType::Hua);
            result.hua_set = false;
        }
        for (index, card) in (1_u8..).zip(board::SpecialCardType::into_enum_iter()) {
            if remove_info & (1 << index) == 0 {
                result.bunker[usize::from(index - 1)] =
                    board::BunkerSlot::Blocked(Option::Some(card.clone()));
            } else {
                whole_vec.push(CardType::Special(card.clone()));
                whole_vec.push(CardType::Special(card.clone()));
                whole_vec.push(CardType::Special(card.clone()));
                whole_vec.push(CardType::Special(card.clone()));
                result.bunker[usize::from(index - 1)] = board::BunkerSlot::Empty;
            }
        }
        for (index, suit) in (4_u8..)
            .step_by(4)
            .zip(board::NumberCardColor::into_enum_iter())
        {
            let value = (((remove_info >> index) & 0b1111) % 10) as u8;
            let slot_index = usize::from((index - 4) / 4);
            if value == 0 {
                result.goal[slot_index] = Option::None;
            } else {
                result.goal[slot_index] = Option::Some(board::NumberCard {
                    value,
                    suit: suit.clone(),
                });
            }
            for value in (value + 1)..10 {
                whole_vec.push(board::CardType::Number(board::NumberCard {
                    value,
                    suit: suit.clone(),
                }));
            }
        }
        whole_vec.shuffle(&mut RandomBytes { data, index: 2 });
        for ((index_start, index_end), slot) in (0..)
            .step_by(8)
            .zip((8..).step_by(8))
            .zip(result.field.iter_mut())
        {
            if let Option::Some(tasty_slice) = whole_vec.get(index_start..index_end) {
                slot.extend_from_slice(tasty_slice);
            } else if let Option::Some(tasty_slice) = whole_vec.get(index_start..) {
                slot.extend_from_slice(tasty_slice);
                break;
            } else {
                break;
            }
        }
        return result;
    } else {
        return Board::default();
    }
}

fuzz_target!(|data: &[u8]| {
    if data.len() == 0 {
        return;
    }
    let x = correct_board_permutation(&data[1..]);
    assert_eq!(x.check(), Result::Ok(()));
    if let Option::Some(action) = board::possibilities::all_actions(&x).choose(&mut RandomBytes {
        data: &data[0..1],
        index: 0,
    }) {
        let mut action_board = x.clone();
        action.apply(&mut action_board);
        assert_ne!(action_board, x);
        action.undo(&mut action_board);
        assert_eq!(action_board, x);
    }
});
