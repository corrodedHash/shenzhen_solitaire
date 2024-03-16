#![allow(clippy::needless_return)]

use std::{io::Read, path::PathBuf};
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
#[structopt(
    name = "shenzhen opt",
    about = "Optimizer for solutions to the shenzhen I/O solitaire minigame"
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

    /// Draw dependency graph in 'dot' format instead of actions instead of optimizing
    #[structopt(short, long)]
    graph: bool,

    /// Prettify JSON output
    #[structopt(short, long)]
    pretty: bool,
}

fn optimize(
    actions: &[actions::All],
    verbose: bool,
) -> Result<String, Box<dyn std::error::Error>> {
    if verbose {
        eprintln!("Starting optimization at {} actions", actions.len());
    }
    let start_time = std::time::Instant::now();
    let optimized_actions = action_optimization::optimize(&actions);

    if verbose {
        eprintln!(
            "Optimized to {} actions in {:.2} seconds",
            optimized_actions.len(),
            start_time.elapsed().as_secs_f32()
        );
    }
    let serialized_actions = serde_json::to_string(&optimized_actions)?;
    
    return Result::Ok(serialized_actions);
}

fn graph(actions: &[actions::All]) -> Result<String, Box<dyn std::error::Error>> {
    let graph_actions = action_optimization::dot_actions(actions);
    return Result::Ok(graph_actions);
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opts = Opt::from_args();
    let buffer = if let Option::Some(input) = opts.input {
        std::fs::read_to_string(input)?
    } else {
        let mut buffer = String::new();
        std::io::stdin().read_to_string(&mut buffer)?;
        buffer
    };
    let action_sequence: Vec<actions::All> = serde_json::from_str(&buffer)?;

    let output = if opts.graph {
        graph(&action_sequence)?
    } else {
        optimize(&action_sequence, opts.verbose)?
    };
    if let Option::Some(output_file) = opts.output {
        std::fs::write(output_file, output)?;
    } else {
        println!("{}", output);
    }

    return Result::Ok(());
}
