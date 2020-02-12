"""Contains solver for solitaire"""
import typing
from typing import Iterator, List, Optional
import time
from dataclasses import dataclass
from ..board import Board
from . import board_actions
from .board_actions import DragonKillAction, GoalAction, HuaKillAction, MoveAction
from .board_possibilities import possible_actions


@dataclass
class ActionStackFrame:
    iterator: Iterator[board_actions.Action]
    action: Optional[board_actions.Action]
    state: int

    def next(self) -> Optional[board_actions.Action]:
        """Get next iteration of top action iterator"""
        try:
            self.action = next(self.iterator)
        except StopIteration:
            return None
        return self.action


class ActionStack:
    """Stack of chosen actions on the board"""

    def __init__(self) -> None:
        self.frames: List[ActionStackFrame] = []

    def push(self, board: Board) -> None:
        """Append another board state to stack"""
        self.frames.append(
            ActionStackFrame(
                iterator=iter(possible_actions(board)),
                action=None,
                state=board.state_identifier,
            )
        )

    @property
    def top(self) -> ActionStackFrame:
        """Get next iteration of top action iterator"""
        return self.frames[-1]

    def pop(self) -> None:
        """Pop one action from stack"""
        self.frames.pop()

    def __len__(self) -> int:
        return len(self.frames)


def solve(
    board: Board, *, timeout: Optional[float] = None, verbose: bool = False
) -> Iterator[List[board_actions.Action]]:
    """Solve a solitaire puzzle"""
    state_set = {board.state_identifier}
    stack = ActionStack()
    stack.push(board)

    def _limit_stack_size(stack_size: int) -> None:
        if len(stack) == stack_size:
            stack.pop()
            assert stack.top.action is not None
            stack.top.action.undo(board)
            assert board.state_identifier in state_set

    def _backtrack_action() -> None:
        stack.pop()
        assert stack.top.action is not None
        stack.top.action.undo(board)
        assert board.state_identifier in state_set

    def _skip_loop_move(action: board_actions.Action) -> bool:
        if not isinstance(action, MoveAction):
            return False
        for frame in stack.frames[-2::-1]:
            if not isinstance(frame.action, MoveAction):
                continue
            if frame.action.cards == action.cards:
                return True
        return False

    iter_start = time.time()
    count = 0
    while stack:

        count += 1
        if count > 5000:
            count = 0
            if verbose:
                print(f"{time.time() - iter_start} {len(stack)} {board.goal}")
            if timeout is not None and time.time() - iter_start > timeout:
                return

        # _limit_stack_size(80)

        assert board.state_identifier == stack.top.state
        action = stack.top.next()

        if action is None:
            _backtrack_action()
            continue

        if _skip_loop_move(action):
            continue

        action.apply(board)

        if board.solved():
            assert all(x.action is not None for x in stack.frames)
            yield [typing.cast(board_actions.Action, x.action) for x in stack.frames]
            iter_start = time.time()
            action.undo(board)
            assert board.state_identifier in state_set
            continue

        if board.state_identifier in state_set:
            action.undo(board)
            assert board.state_identifier in state_set
            continue

        state_set.add(board.state_identifier)
        stack.push(board)
