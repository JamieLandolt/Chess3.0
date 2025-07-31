class Piece():
    def __init__(self, coords, colour):
        self.coords = coords
        self.colour = colour
        self.letter = "X"

    def get_letter(self):
        return f"'{self.letter}'"

    def __deepcopy__(self, memodict={}):
        copy = self.__class__(self.coords, self.colour)
        copy.letter = self.letter
        return copy

    def c2b(self):
        """Converts a piece's chess coords (a1) to board coords (0, 0)"""
        coord = self.coords
        coords = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return 8 - int(coord[1]), coords[coord[0]]

    def __add__(self, other):
        letters = "abcdefgh"
        for i, letter in enumerate(letters):
            if letter == self.coords[0]:
                if i + other > 7:
                    return ''
                self.coords = letters[(i + other)] + self.coords[1]

    def __sub__(self, other):
        letters = "abcdefgh"
        for i, letter in enumerate(letters):
            if letter == self.coords[0]:
                if i - other < 0:
                    return ''
                self.coords = letters[(i - other)] + self.coords[1]

    def __mul__(self, other):
        if int(self.coords[1]) + other > 8:
            return ''
        self.coords = self.coords[0] + str((int(self.coords[1]) + other))

    def __truediv__(self, other):
        if int(self.coords[1]) - other < 1:
            return ''
        self.coords = self.coords[0] + str((int(self.coords[1]) - other))

    def get_square(self, op, offset, square=None):
        if square is None:
            square = self.coords
        match op:
            case '+':
                letters = "abcdefgh"
                for i, letter in enumerate(letters):
                    if letter == square[0]:
                        if i + offset > 7:
                            return ''
                        return letters[(i + offset)] + square[1]
            case '-':
                letters = "abcdefgh"
                for i, letter in enumerate(letters):
                    if letter == square[0]:
                        if i - offset < 0:
                            # Outside board
                            return ''
                        return letters[(i - offset)] + square[1]
            case '*':
                if int(square[1]) + offset > 8:
                    return ''
                return square[0] + str((int(square[1]) + offset))
            case '/':
                if int(square[1]) - offset < 1:
                    return ''
                return square[0] + str((int(square[1]) - offset))

    def __repr__(self):
        return self.letter

class Pawn(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)
        self.letter = "P"
        self.can_be_en_passanted = False

    def __deepcopy__(self, memo={}):
        copy = super().__deepcopy__()
        copy.can_be_en_passanted = self.can_be_en_passanted
        return copy

class Knight(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)
        self.letter = "N"

class Bishop(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)
        self.letter = "B"

class Rook(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)
        self.castling_rights = True
        self.letter = "R"

    def __deepcopy__(self, memo={}):
        copy = super().__deepcopy__()
        copy.castling_rights = self.castling_rights
        return copy


class Queen(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)
        self.letter = "Q"

class King(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)

        self.castling_rights = True
        self.letter = "K"

    def __deepcopy__(self, memodict={}):
        copy = super().__deepcopy__()
        copy.castling_rights = self.castling_rights
        return copy
