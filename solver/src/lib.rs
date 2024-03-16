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
  // clippy::result_unwrap_used,
  // clippy::wildcard_enum_match_arm
)]
#![allow(clippy::trivially_copy_pass_by_ref)]
#![allow(dead_code)]

#[test]
#[ignore]
fn struct_size_printer() {
  macro_rules! print_size{
    ($x:ty) => {
      println!("{:30} {:3} {:3}", std::stringify!($x), std::mem::size_of::<$x>(), std::mem::align_of::<$x>());
    }
  }
  print_size!(board::Board);
  print_size!(board::BoardEqHash);
  print_size!(actions::All);
  print_size!(actions::DragonKill);
  print_size!(actions::Move);
  print_size!(actions::Bunkerize);
  print_size!(actions::Goal);
  print_size!(actions::HuaKill);
  print_size!(board::FieldPosition);
  print_size!(board::PositionNoGoal);
  print_size!(board::CardType);
}
