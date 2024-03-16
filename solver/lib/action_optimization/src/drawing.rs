use super::graph_entity::{to_graph, ActionGraph, RelationType};
use std::{
    path::Path,
    process::{Command, Stdio},
};

#[must_use]
pub fn dot_actions(actions: &[actions::All]) -> String {
    return dot_actiongraph(&to_graph(actions));
}

#[must_use]
fn dot_actiongraph(graph: &ActionGraph) -> String {
    let edge_attr = |relation_type: &RelationType| {
        let edge_style = match relation_type {
            RelationType::Move => "bold",
            RelationType::Unblock
            | RelationType::Clear
            | RelationType::Socket
            | RelationType::Goal => "solid",
        };
        let edge_color = match relation_type {
            RelationType::Move => "black",
            RelationType::Unblock => "green",
            RelationType::Clear => "grey",
            RelationType::Socket => "red",
            RelationType::Goal => "blue",
        };
        return format!("style=\"{}\" color=\"{}\"", edge_style, edge_color);
    };
    let node_attr = |action: &actions::All| {
        let node_color = match action {
            actions::All::Bunkerize(_) | actions::All::Move(_) => "white",
            actions::All::DragonKill(_) => "silver",
            actions::All::Goal(_) => "blue",
            actions::All::HuaKill(_) => "gold",
        };
        return format!(
            r#"style="filled" fillcolor="{}" label="{}" shape="rect""#,
            node_color,
            action.to_string().replace(r#"""#, r#"\""#)
        );
    };
    let dot_rep = petgraph::dot::Dot::with_attr_getters(
        &graph,
        &[
            petgraph::dot::Config::EdgeNoLabel,
            petgraph::dot::Config::NodeNoLabel,
        ],
        &|_mygraph, myedge| return edge_attr(myedge.weight()),
        &|_mygraph, (_index, action)| {
            return node_attr(action);
        },
    )
    .to_string();
    return dot_rep;
}

pub fn draw_graph(graph: &ActionGraph, path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    //! # Errors
    //! File write error
    let input = dot_actiongraph(graph);
    let mut child = Command::new("dot")
        .args(&["-Tsvg", "-o", path.to_string_lossy().as_ref()])
        .stdin(Stdio::piped())
        .stderr(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()?;

    std::io::Write::write_all(
        child
            .stdin
            .as_mut()
            .ok_or("Child process stdin has not been captured!")?,
        input.as_bytes(),
    )?;

    let output = child.wait_with_output()?;
    if !output.status.success() {
        println!(
            "Dot failed\n{}\n{}",
            std::str::from_utf8(&output.stdout).unwrap(),
            std::str::from_utf8(&output.stderr).unwrap()
        );
        // No idea how to return a custom error here
    }
    return Result::Ok(());
}

pub fn draw_actions(
    actions: &[actions::All],
    path: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    //! # Errors
    //! File write error
    let graph = to_graph(actions);
    return draw_graph(&graph, path);
}
