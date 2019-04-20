"""Contains solver for solitaire"""
from typing import List, Tuple, Iterator, Set, Optional
from .board import Board
from . import board_actions
from .board_possibilities import possible_actions


class ActionStack:
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
        self.iterator_stack.append(possible_actions(board))
        self.action_stack.append(None)
        self.index_stack.append(0)
        self.state_stack.append(board.state_identifier)

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
        self.state_stack.pop()

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

    def solve(self) -> Iterator[List[board_actions.Action]]:
        while self.stack:

            assert (self.search_board.state_identifier ==
                    self.stack.state_stack[-1])
            action = self.stack.get()

            if not action:
                self.stack.pop()
                self.stack.action_stack[-1].undo(self.search_board)
                assert (self.search_board.state_identifier
                        in self.state_set)
                continue

            action.apply(self.search_board)

            if self.search_board.solved():
                yield self.stack.action_stack

            if self.search_board.state_identifier in self.state_set:
                action.undo(self.search_board)
                assert self.search_board.state_identifier in self.state_set
                continue

            self.state_set.add(self.search_board.state_identifier)
            self.stack.push(self.search_board)

        return self.stack.action_stack
