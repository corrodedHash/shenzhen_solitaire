"""Contains solver for solitaire"""
from typing import List, Tuple, Iterator, Set, Optional
from .board import Board
from . import board_actions
from .board_possibilities import possible_actions


class ActionStack:
    iterator_stack: List[Iterator[board_actions.Action]]
    action_stack: List[Optional[board_actions.Action]]
    index_stack: List[int]

    def __init__(self) -> None:
        self.iterator_stack = []
        self.index_stack = []
        self.action_stack = []

    def push(self, board: Board) -> None:
        self.iterator_stack.append(possible_actions(board))
        self.action_stack.append(None)
        self.index_stack.append(0)

    def get(self) -> Optional[board_actions.Action]:
        try:
            self.action_stack[-1] = next(self.iterator_stack[-1])
        except StopIteration:
            return None
        self.index_stack[-1] += 1
        return self.action_stack[-1]

    def pop(self) -> None:
        self.action_stack.pop()
        self.iterator_stack.pop()
        self.index_stack.pop()

    def __len__(self) -> int:
        return len(self.index_stack)


class SolitaireSolver:
    """Solver for Shenzhen Solitaire"""

    search_board: Board
    stack: ActionStack
    state_set: Set[int]

    def __init__(self, board: Board) -> None:
        self.search_board = board
        self.state_set = {board.state_identifier}
        self.stack = ActionStack()
        self.stack.push(self.search_board)

    def solve(self) -> List[board_actions.Action]:
        applied = True
        action = None
        while self.stack:
            last_action = action
            action = self.stack.get()
            if not action:
                if last_action and applied:
                    last_action.undo(self.search_board)
                    assert (self.search_board.state_identifier
                            in self.state_set)
                self.stack.pop()
                continue
            action.apply(self.search_board)
            print(f"Applying {str(action)}")
            applied = True
            if self.search_board.state_identifier in self.state_set:
                action.undo(self.search_board)
                applied = False
                assert self.search_board.state_identifier in self.state_set
                continue
            self.state_set.add(self.search_board.state_identifier)
            self.stack.push(self.search_board)

        return self.stack.action_stack
