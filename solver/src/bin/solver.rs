use std::io::Read;
use std::{path::PathBuf, str::FromStr};
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
#[structopt(
    name = "shenzhen solver",
    about = "Solver for the shenzhen I/O solitaire minigame"
)]
struct Opt {
    /// Input for JSON board, default is stdin
    #[structopt(short, long, parse(from_os_str))]
    input: Option<PathBuf>,

    /// Output for JSON action sequence, default is stdout
    #[structopt(short, long, parse(from_os_str))]
    output: Option<PathBuf>,

    /// Print information about solving
    #[structopt(short, long)]
    verbose: bool,

    /// Optimize result action sequence
    #[structopt(short = "-r", long)]
    optimize: bool,

    /// Prettify JSON output
    #[structopt(short, long)]
    pretty: bool,
}

#[allow(clippy::needless_return)]
pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opts = Opt::from_args();
    let buffer = if let Option::Some(input) = opts.input {
        std::fs::read_to_string(input)?
    } else {
        let mut buffer = String::new();
        std::io::stdin().read_to_string(&mut buffer)?;
        buffer
    };

    let board = board::Board::from_str(&buffer)?;

    let start_time = std::time::Instant::now();
    if opts.verbose {
        eprintln!("Start solving");
    }
    let action_sequence = solving::solve(&board)?;
    if opts.verbose {
        eprintln!(
            "Finished solving in {:.2}s",
            std::time::Instant::now()
                .duration_since(start_time)
                .as_secs_f32()
        );
    }

    if opts.verbose {
        eprintln!("Action count in sequence: {:3}", action_sequence.len());
    }
    let action_sequence = if opts.optimize {
        let optimized_actions = action_optimization::optimize(&action_sequence);
        if opts.verbose {
            eprintln!("Optimized action count: {:3}", optimized_actions.len());
        }
        optimized_actions
    } else {
        action_sequence
    };
    assert!(solving::benchmark::actions_correct(
        &action_sequence,
        board,
        false
    ));

    let serialized_actions = if opts.pretty {
        serde_json::to_string_pretty(&action_sequence)?
    } else {
        serde_json::to_string(&action_sequence)?
    };
    if let Option::Some(output) = opts.output {
        std::fs::write(output, serialized_actions)?;
    } else {
        println!("{}", serialized_actions);
    }
    return Result::Ok(());
}
