use super::solve;

#[must_use]
pub fn actions_correct(actions: &[actions::All], mut board: board::Board, verbose: bool) -> bool {
    for (index, action) in actions.iter().enumerate() {
        if verbose {
            println!("Action #{:3}: {}", index, action);
        }
        action.apply(&mut board);
    }
    return board.solved();
}
fn run_test(board: board::Board) -> (f32, usize) {
    use std::io::Write;
    std::io::stdout().flush().expect("Flushing did not work");
    assert_eq!(board.check(), Result::Ok(()));
    let start_time = std::time::Instant::now();
    let result = solve(&board);
    let result_time = start_time.elapsed().as_secs_f32();
    assert!(!result.is_err());
    let mut result_length: usize = 0;
    if let Result::Ok(actions) = result {
        assert!(actions_correct(&actions, board, false));
        result_length = actions.len();
    }
    return (result_time, result_length);
}
fn run_all_tests(
    dirname: &std::path::Path,
    exclude: &[&str],
) -> Result<(), Box<dyn std::error::Error>> {
    for board_json in std::fs::read_dir(dirname)? {
        let board_json = board_json?;
        if exclude.contains(
            &board_json
                .path()
                .as_path()
                .file_name()
                .unwrap()
                .to_str()
                .unwrap(),
        ) {
            continue;
        }
        let x = board::Board::from_file(&board_json.path())?;
        print!(
            "> {:<20} ",
            board_json.path().file_stem().unwrap().to_string_lossy(),
        );
        let (time, length) = run_test(x);
        println!("{:.02} {:3}", time, length);
    }
    return Result::Ok(());
}

#[test]
#[ignore]
pub fn possible() -> Result<(), Box<dyn std::error::Error>> {
    //! # Errors
    let whole_board_dir: std::path::PathBuf = [board::TEST_BOARD_ROOT!(), "normal"].iter().collect();
    println!("{:?}", whole_board_dir);
    return run_all_tests(&whole_board_dir, &[]);
}