from .context import shenzhen_solitaire
from shenzhen_solitaire import solver

from .boards import my_board

A = solver.SolitaireSolver(my_board)
B = A.solve()
print(*B, sep='\n')
print(len(B))
