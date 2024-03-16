#![warn(
    clippy::all,
    clippy::restriction,
    clippy::pedantic,
    clippy::nursery,
    clippy::cargo
)]
#![allow(clippy::cargo)]
// Style choices
#![allow(
    clippy::missing_docs_in_private_items,
    clippy::needless_return,
    clippy::get_unwrap,
    clippy::indexing_slicing,
    clippy::explicit_iter_loop
)]
// Way too pedantic
#![allow(clippy::integer_arithmetic)]
#![allow(clippy::integer_division)]
// Useless
#![allow(clippy::missing_inline_in_public_items, clippy::missing_const_for_fn)]
// Useful for production
#![allow(
    clippy::use_debug,
    clippy::print_stdout,
    clippy::dbg_macro,
    clippy::panic
)]
// Useful for improving code robustness
#![allow(
    clippy::cast_possible_truncation,
    clippy::cast_possible_wrap,
    clippy::option_unwrap_used,
    clippy::option_expect_used,
    clippy::as_conversions,
    clippy::result_unwrap_used,
    clippy::result_expect_used,
    // clippy::wildcard_enum_match_arm
)]
#![allow(clippy::trivially_copy_pass_by_ref)]
#![allow(dead_code)]

mod cards;
pub use cards::*;
mod fieldposition;
pub use fieldposition::*;
mod positions;
pub use positions::*;
mod board_class;
pub use crate::board_class::*;
pub mod test_boards;

#[cfg(test)]
mod tests;
