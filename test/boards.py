from .context import shenzhen_solitaire
from shenzhen_solitaire.board import NumberCard, SpecialCard, Board

my_board: Board = Board()
my_board.field[0] = [
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Black, 8),
    SpecialCard.Bai,
    NumberCard(NumberCard.Suit.Black, 7),
    SpecialCard.Zhong,
]

my_board.field[1] = [
    NumberCard(NumberCard.Suit.Red, 9),
    SpecialCard.Zhong,
    SpecialCard.Zhong,
    NumberCard(NumberCard.Suit.Black, 4),
    NumberCard(NumberCard.Suit.Black, 3),
]

my_board.field[2] = [
    SpecialCard.Hua,
    NumberCard(NumberCard.Suit.Red, 1),
    NumberCard(NumberCard.Suit.Red, 4),
    NumberCard(NumberCard.Suit.Green, 1),
    NumberCard(NumberCard.Suit.Red, 6),
]

my_board.field[3] = [
    SpecialCard.Bai,
    SpecialCard.Zhong,
    NumberCard(NumberCard.Suit.Red, 3),
    NumberCard(NumberCard.Suit.Red, 7),
    NumberCard(NumberCard.Suit.Green, 6),
]

my_board.field[4] = [
    NumberCard(NumberCard.Suit.Green, 7),
    NumberCard(NumberCard.Suit.Green, 4),
    NumberCard(NumberCard.Suit.Red, 5),
    NumberCard(NumberCard.Suit.Green, 5),
    NumberCard(NumberCard.Suit.Black, 6),
]

my_board.field[5] = [
    NumberCard(NumberCard.Suit.Green, 3),
    SpecialCard.Bai,
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Black, 2),
    NumberCard(NumberCard.Suit.Black, 5),
]

my_board.field[6] = [
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Green, 9),
    NumberCard(NumberCard.Suit.Green, 2),
    NumberCard(NumberCard.Suit.Black, 9),
    NumberCard(NumberCard.Suit.Red, 8),
]

my_board.field[7] = [
    SpecialCard.Bai,
    NumberCard(NumberCard.Suit.Red, 2),
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Black, 1),
    NumberCard(NumberCard.Suit.Green, 8),
]
