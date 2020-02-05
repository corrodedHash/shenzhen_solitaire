"""Contains an example board to run tests on"""
from shenzhen_solitaire.board import NumberCard, SpecialCard, Board

Suit = NumberCard.Suit

TEST_BOARD = Board()
TEST_BOARD.field[0] = [
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Black, 8),
    SpecialCard.Bai,
    NumberCard(NumberCard.Suit.Black, 7),
    SpecialCard.Zhong,
]

TEST_BOARD.field[1] = [
    NumberCard(NumberCard.Suit.Red, 9),
    SpecialCard.Zhong,
    SpecialCard.Zhong,
    NumberCard(NumberCard.Suit.Black, 4),
    NumberCard(NumberCard.Suit.Black, 3),
]

TEST_BOARD.field[2] = [
    SpecialCard.Hua,
    NumberCard(NumberCard.Suit.Red, 1),
    NumberCard(NumberCard.Suit.Red, 4),
    NumberCard(NumberCard.Suit.Green, 1),
    NumberCard(NumberCard.Suit.Red, 6),
]

TEST_BOARD.field[3] = [
    SpecialCard.Bai,
    SpecialCard.Zhong,
    NumberCard(NumberCard.Suit.Red, 3),
    NumberCard(NumberCard.Suit.Red, 7),
    NumberCard(NumberCard.Suit.Green, 6),
]

TEST_BOARD.field[4] = [
    NumberCard(NumberCard.Suit.Green, 7),
    NumberCard(NumberCard.Suit.Green, 4),
    NumberCard(NumberCard.Suit.Red, 5),
    NumberCard(NumberCard.Suit.Green, 5),
    NumberCard(NumberCard.Suit.Black, 6),
]

TEST_BOARD.field[5] = [
    NumberCard(NumberCard.Suit.Green, 3),
    SpecialCard.Bai,
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Black, 2),
    NumberCard(NumberCard.Suit.Black, 5),
]

TEST_BOARD.field[6] = [
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Green, 9),
    NumberCard(NumberCard.Suit.Green, 2),
    NumberCard(NumberCard.Suit.Black, 9),
    NumberCard(NumberCard.Suit.Red, 8),
]

TEST_BOARD.field[7] = [
    SpecialCard.Bai,
    NumberCard(NumberCard.Suit.Red, 2),
    SpecialCard.Fa,
    NumberCard(NumberCard.Suit.Black, 1),
    NumberCard(NumberCard.Suit.Green, 8),
]

B20190809172206_1 = Board()
B20190809172206_1.field[0] = [
    NumberCard(Suit.Green, 6),
    NumberCard(Suit.Green, 5),
    NumberCard(Suit.Red, 4),
    NumberCard(Suit.Green, 4),
    SpecialCard.Fa,
]

B20190809172206_1.field[1] = [
    NumberCard(Suit.Black, 8),
    NumberCard(Suit.Black, 6),
    SpecialCard.Zhong,
    NumberCard(Suit.Black, 9),
    NumberCard(Suit.Green, 7),
]

B20190809172206_1.field[2] = [
    SpecialCard.Zhong,
    NumberCard(Suit.Black, 4),
    NumberCard(Suit.Green, 2),
    SpecialCard.Bai,
    SpecialCard.Zhong,
]
B20190809172206_1.field[3] = [
    NumberCard(Suit.Green, 1),
    NumberCard(Suit.Green, 3),
    NumberCard(Suit.Black, 5),
    SpecialCard.Fa,
    SpecialCard.Fa,
]
B20190809172206_1.field[4] = [
    NumberCard(Suit.Red, 8),
    SpecialCard.Zhong,
    NumberCard(Suit.Red, 7),
]
B20190809172206_1.field[5] = [
    SpecialCard.Fa,
    SpecialCard.Bai,
    NumberCard(Suit.Red, 2),
    SpecialCard.Hua,
    SpecialCard.Bai,
]
B20190809172206_1.field[6] = [
    NumberCard(Suit.Black, 2),
    NumberCard(Suit.Green, 8),
    NumberCard(Suit.Black, 7),
    SpecialCard.Bai,
    NumberCard(Suit.Red, 9),
]

B20190809172206_1.field[7] = [
    NumberCard(Suit.Red, 3),
    NumberCard(Suit.Black, 3),
    NumberCard(Suit.Green, 9),
    NumberCard(Suit.Red, 5),
    NumberCard(Suit.Red, 6),
]
