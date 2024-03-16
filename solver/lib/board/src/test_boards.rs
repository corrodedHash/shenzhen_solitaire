// This is incredibly shit, as other crates call this macro with _their_ CARGO_MANIFEST_DIR. Ideally we would move
// the boards into the board crate, and use the path of the board crate. But it seems to be really hard to get this done with
// macros, and const variables can't be used by macros, so we're using this hack for now.
#[macro_export]
macro_rules! TEST_BOARD_ROOT {
  () => {
    concat!(env!("CARGO_MANIFEST_DIR"), 
              "/../../aux/boards/")
  }
}

#[macro_export]
macro_rules! load_test_board {
  ( $relpath:expr ) => {
      {
          <$crate::Board as std::str::FromStr>::from_str(
            include_str!(concat!($crate::TEST_BOARD_ROOT!(), 
              $relpath)))
      }
  };
}