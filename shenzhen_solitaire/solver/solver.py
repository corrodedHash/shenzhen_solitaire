"""Contains solver for solitaire"""
import typing
from typing import Iterator, List, Optional

from ..board import Board
from . import board_actions
from .board_actions import (DragonKillAction, GoalAction, HuaKillAction,
                            MoveAction)
from .board_possibilities import possible_actions


class ActionStack:
    """Stack of chosen actions on the board"""

    iterator_stack: List[Iterator[board_actions.Action]]
    action_stack: List[Optional[board_actions.Action]]
    index_stack: List[int]
    state_stack: List[int]

    def __init__(self) -> None:
        self.iterator_stack = []
        self.index_stack = []
        self.action_stack = []
        self.state_stack = []

    def push(self, board: Board) -> None:
        """Append another board state to stack"""
        self.iterator_stack.append(possible_actions(board))
        self.action_stack.append(None)
        self.index_stack.append(0)
        self.state_stack.append(board.state_identifier)

    def get(self) -> Optional[board_actions.Action]:
        """Get next iteration of top action iterator"""
        try:
            self.action_stack[-1] = next(self.iterator_stack[-1])
        except StopIteration:
            return None
        self.index_stack[-1] += 1
        return self.action_stack[-1]

    def pop(self) -> None:
        """Pop one action from stack"""
        self.action_stack.pop()
        self.iterator_stack.pop()
        self.index_stack.pop()
        self.state_stack.pop()

    def __len__(self) -> int:
        return len(self.index_stack)


def solve(board: Board) -> Iterator[List[board_actions.Action]]:
    """Solve a solitaire puzzle"""
    state_set = {board.state_identifier}
    stack = ActionStack()
    stack.push(board)

    def _limit_stack_size(stack_size: int) -> None:
        if len(stack) == stack_size:
            stack.pop()
            assert stack.action_stack[-1] is not None
            stack.action_stack[-1].undo(board)
            assert board.state_identifier in state_set

    def _backtrack_action() -> None:
        stack.pop()
        assert stack.action_stack[-1] is not None
        stack.action_stack[-1].undo(board)
        assert board.state_identifier in state_set

    def _skip_loop_move(action: board_actions.Action) -> bool:
        if isinstance(action, MoveAction):
            for prev_action in stack.action_stack[-2::-1]:
                if isinstance(prev_action, MoveAction):
                    if prev_action.cards == action.cards:
                        return True
        return False

    count = 0
    while stack:
        count += 1
        if count > 5000:
            count = 0
            print(f"{len(stack)} {board.goal}")

        # _limit_stack_size(80)

        assert board.state_identifier == stack.state_stack[-1]
        action = stack.get()

        if not action:
            _backtrack_action()
            continue

        if _skip_loop_move(action):
            continue

        action.apply(board)

        if board.solved():
            yield stack.action_stack
            stack.action_stack[-1].undo(board)
            while isinstance(
                stack.action_stack[-1], (GoalAction, HuaKillAction, DragonKillAction)
            ):
                stack.pop()
                stack.action_stack[-1].undo(board)
            continue

        if board.state_identifier in state_set:
            action.undo(board)
            assert board.state_identifier in state_set
            continue

        state_set.add(board.state_identifier)
        stack.push(board)
