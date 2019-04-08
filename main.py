"""Main module"""
from typing import List, Tuple
import board
import board_actions


class SolitaireSolver:
    """Solver for Shenzhen Solitaire"""
    search_board: board.Board
    stack: List[Tuple[board_actions.Action, int]]
