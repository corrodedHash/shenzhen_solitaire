"""Contains solver for solitaire"""
from typing import List, Tuple
from .board import Board
from . import board_actions


class SolitaireSolver:
    """Solver for Shenzhen Solitaire"""

    search_board: Board
    stack: List[Tuple[board_actions.Action, int]]
