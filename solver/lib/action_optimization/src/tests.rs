use crate::{draw_graph, graph_entity::to_graph};
use std::str::FromStr;
#[test]
#[ignore]
pub fn optimize_bunker_loop() {
    use actions::{All, Bunkerize, Goal};
    use board::FieldPosition;
    let numbercard = board::NumberCard {
        suit: board::NumberCardColor::Red,
        value: 1,
    };
    let zhong_card = board::CardType::Number(numbercard.clone());
    let actions = vec![
        All::Bunkerize(Bunkerize {
            bunker_slot_index: 0,
            card: zhong_card.remove_hua(),
            to_bunker: false,
            field_position: FieldPosition::new(2, 0),
        }),
        All::Bunkerize(Bunkerize {
            bunker_slot_index: 2,
            card: zhong_card.remove_hua(),
            to_bunker: true,
            field_position: FieldPosition::new(2, 0),
        }),
        All::Goal(Goal {
            card: numbercard,
            goal_slot_index: 0,
            source: board::PositionNoGoal::Bunker { slot_index: 2 },
        }),
    ];
    let graph = to_graph(&actions);
    draw_graph(&graph, std::path::Path::new("unopt_bunker.svg")).unwrap();
    let graph = crate::optimize::merge_step(graph);
    draw_graph(&graph, std::path::Path::new("opt_bunker.svg")).unwrap();
}

#[test]
pub fn all_boards_correct() -> Result<(), Box<dyn std::error::Error>> {
    for i in 1..19 {
        let action_string =
            std::fs::read_to_string(std::format!("{}/{:02}.json", crate::TEST_ACTION_ROOT!(), i))?;

        let actions: Vec<actions::All> = serde_json::from_str(&action_string)?;

        let board_string = std::fs::read_to_string(std::format!(
            "{}/normal/{:02}.json",
            board::TEST_BOARD_ROOT!(),
            i
        ))?;
        let src_board = board::Board::from_str(&board_string)?;
        let mut board = src_board.clone();
        for action in actions.iter() {
            action.apply(&mut board);
        }
        assert!(board.solved());
        let actions = crate::optimize(&actions);
        let mut board = src_board;
        for (index, action) in actions.into_iter().enumerate() {
            println!("{}", index);
            action.apply(&mut board);
        }
        assert!(board.solved());
    }
    return Result::Ok(());
}
