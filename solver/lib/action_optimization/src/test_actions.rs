// This is incredibly shit, as other crates call this macro with _their_ CARGO_MANIFEST_DIR. Ideally we would move
// the boards into the board crate, and use the path of the board crate. But it seems to be really hard to get this done with
// macros, and const variables can't be used by macros, so we're using this hack for now.
#[macro_export]
macro_rules! TEST_ACTION_ROOT {
  () => {
    concat!(env!("CARGO_MANIFEST_DIR"), 
              "/../../aux/actions/")
  }
}

#[macro_export]
macro_rules! load_test_action {
  ( $relpath:expr ) => {
      {
        return serde_json::from_str::<Vec<actions::All>>(include_str!(concat!($crate::TEST_ACTION_ROOT!(), 
        $relpath)));
      }
  };
}