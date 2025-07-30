from pieces import *

class Controller:
    def __init__(self):
        self.g = Game(self)
        self.h = HelperFunctions(self)
        self.highlighted_squares = []

    def c2b(self, coord):
        """Converts chess coords (a1) to board coords (0, 0)"""
        coords = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return (8 - int(coord[1]), coords[coord[0]])

    def b2c(self, coord):
        alpha = 'abcdefgh'
        return alpha[coord[1]] + str(8 - coord[0])

    def deselect_piece(self):
        for square in self.h.get_legal_moves(self.g.selected_piece):
            self.highlighted_squares.remove(square)
        self.g.selected_piece = None

    def select_piece(self, square):
        self.g.selected_piece = self.g.positions_to_pieces[square]
        self.highlighted_squares.extend(self.h.get_legal_moves(self.g.selected_piece))

    def on_click(self, square):
        """When a square is clicked, this function is run with the parameter being the square clicked (e4)"""
        if not self.g.selected_piece:
            if self.g.positions_to_pieces.get(square, None):
                self.select_piece(square)
            return

        # At this point we have selected a piece, then clicked a square to move it to that square
        # If same piece clicked deselect
        if square == self.g.selected_piece:
            self.deselect_piece()
            return

        # Check if piece can move to square
        if square in self.h.get_legal_moves(self.g.selected_piece) and self.g.turn in self.g.player_colours:
            self.g.move(self.g.selected_piece, square)
            self.deselect_piece()
        else:
            # Deselect piece if invalid square
            self.deselect_piece()
        return

    def set_player_colours(self, option):
        match option:
            case 0:
                self.g.player_colours = ["W"]
            case 1:
                self.g.player_colours = ["B"]
            case 2:
                self.g.player_colours = ["W", "B"]
            case 3:
                self.g.player_colours = []


class Game:
    def __init__(self, c: Controller):
        # A reference to the Controller
        self.c = c
        # Maps squares to their pieces
        self.positions_to_pieces = {}
        # The currently selected piece (Legal moves are shown)
        self.selected_piece = None
        # Whose turn it is
        self.turn = "W"
        # This controls whether the game is running (Running iff not None)
        # TODO: Implement button to select player colours & this should be initially None
        self.player_colours = ["W"]

    def generate_board(self):
        self.board = [[' '] * 8 for _ in range(8)]

        # Black Pieces
        self.board[0][0] = Rook("a8", colour="B")
        self.board[0][1] = Knight("b8", colour="B")
        self.board[0][2] = Bishop("c8", colour="B")
        self.board[0][3] = Queen("d8", colour="B")
        self.board[0][4] = King("e8", colour="B")
        self.board[0][5] = Bishop("f8", colour="B")
        self.board[0][6] = Knight("g8", colour="B")
        self.board[0][7] = Rook("h8", colour="B")

        # White Pieces
        self.board[7][0] = Rook("a1", colour="W")
        self.board[7][1] = Knight("b1", colour="W")
        self.board[7][2] = Bishop("c1", colour="W")
        self.board[7][3] = Queen("d1", colour="W")
        self.board[7][4] = King("e1", colour="W")
        self.board[7][5] = Bishop("f1", colour="W")
        self.board[7][6] = Knight("g1", colour="W")
        self.board[7][7] = Rook("h1", colour="W")

        # Black Pawns
        alpha = 'abcdefgh'
        for i in range(8):
            self.board[1][i] = Pawn(alpha[i] + "7", colour="B")

        # White Pawns
        for i in range(8):
            self.board[6][i] = Pawn(alpha[i] + "2", colour="W")

        # Generate piece to square and square to piece mappings
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece != ' ':
                    square = self.c.b2c((i, j))
                    self.positions_to_pieces[square] = piece

        return self.board

    def move(self, piece, square):
        """Takes a piece and moves it to the new square"""
        piece.coords = square
        self.positions_to_pieces[piece] = None
        self.positions_to_pieces[square] = piece
        board_coords = piece.c2b()
        self.board[board_coords[0]][board_coords[1]] = piece


class HelperFunctions:
    def __init__(self, c: Controller):
        self.c = c

    def get_piece_on(self, square):
        """Returns the piece on the given square, None if there is no piece"""
        return self.c.g.positions_to_pieces[square]

    def square_free(self, square, colour):
        """Returns True iff there is no piece on the square of the same colour given and the square is on the board"""
        # .get is important i think smth to do with pieces off the board
        occupant = self.c.g.positions_to_pieces.get(square, ' ')
        return (occupant == ' ' or occupant.colour != colour) and self.square_on_board(square)

    def square_on_board(self, square):
        """Returns True iff the square is on the board (between 'a1' to 'h8')"""
        return square[0] in 'abcdefgh' and square[1] in '12345678'

    def filter_moves(self, piece, legals):
        """Filters out empty squares ('') and those which have a piece on of the same colour (can't capture same colour)"""
        return set(filter(lambda x: x and self.square_free(x, piece.colour), legals))


    def get_pawn_legal_moves(self, piece):
        legals = set()

        # Account for W or B piece colour
        starting_rank = '2' if piece.colour == "W" else '7'
        op = "*" if piece.colour == "W" else '/'

        above_sq = piece.get_square(op, 1)
        if self.square_free(above_sq, piece.colour):
            legals.add(above_sq)

            # On second rank (double move)
            if piece.coords[1] == starting_rank:
                above_sq2 = piece.get_square(op, 2)
                if self.square_free(above_sq2, piece.colour):
                    legals.add(above_sq2)

        return legals

    def get_rook_legal_moves(self, piece):
        legals = set()

        for i in range(1, 9):
            legals.add(piece.get_square('*', i))
            legals.add(piece.get_square('/', i))
            legals.add(piece.get_square('+', i))
            legals.add(piece.get_square('-', i))

        return self.filter_moves(piece, legals)

    def get_knight_legal_moves(self, piece):
        legals = set()
        up2 = piece.get_square('*', 2)
        down2 = piece.get_square('/', 2)
        left2 = piece.get_square('-', 2)
        right2 = piece.get_square('+', 2)

        if up2:
            legals.add(piece.get_square('-', 1, up2))
            legals.add(piece.get_square('+', 1, up2))
        if down2:
            legals.add(piece.get_square('-', 1, down2))
            legals.add(piece.get_square('+', 1, down2))
        if left2:
            legals.add(piece.get_square('/', 1, left2))
            legals.add(piece.get_square('*', 1, left2))
        if right2:
            legals.add(piece.get_square('/', 1, right2))
            legals.add(piece.get_square('*', 1, right2))

        return self.filter_moves(piece, legals)

    def get_bishop_legal_moves(self, piece):
        legals = set()
        # Tracks which diagonals have run into a piece / edge of board (can't jump piece or edge of board)
        diags = {"UR": 1, "UL": 1, "DR": 1, "DL": 1}

        for i in range(1, 9):
            up_i = piece.get_square('*', i)
            down_i = piece.get_square('/', i)

            # Stop searching diagonals if all have hit a wall/piece
            if not any(diags.values()):
                return set(filter(lambda x: x and self.square_free(x, piece.colour), legals))

            # if up_i avoids passing in '' as up_i for invalid square (when square not on board)
            if up_i:
                # Check we aren't jumping pieces
                if diags["UR"]:
                    square = piece.get_square('+', i, up_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    # Check if diag ends (piece hit)
                    if occupant:
                        diags["UR"] = 0
                    legals.add(square)
                if diags["UL"]:
                    square = piece.get_square('-', i, up_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    if occupant:
                        diags["UL"] = 0
                    legals.add(square)
            if down_i:
                if diags["DR"]:
                    square = piece.get_square('+', i, down_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    if occupant:
                        diags["DR"] = 0
                    legals.add(square)
                if diags["DL"]:
                    square = piece.get_square('-', i, down_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    if occupant:
                        diags["DL"] = 0
                    legals.add(square)

        return self.filter_moves(piece, legals)

    def get_queen_legal_moves(self, piece):
        return self.get_bishop_legal_moves(piece).union(self.get_rook_legal_moves(piece))

    def get_king_legal_moves(self, piece):
        legals = set()

        up_1 = piece.get_square('*', 1)
        legals.add(up_1)
        down_1 = piece.get_square('/', 1)
        legals.add(down_1)
        right_1 = piece.get_square('+', 1)
        legals.add(right_1)
        left_1 = piece.get_square('-', 1)
        legals.add(left_1)

        # Diags - if up_1 to avoid error for passing empty str into .get_square()
        if up_1:
            square = piece.get_square('+', 1, up_1)
            legals.add(square)
            square = piece.get_square('-', 1, up_1)
            legals.add(square)
        if down_1:
            square = piece.get_square('+', 1, down_1)
            legals.add(square)
            square = piece.get_square('-', 1, down_1)
            legals.add(square)

        return self.filter_moves(piece, legals)

    def get_legal_moves(self, piece):
        match piece.letter:
            case "P":
                return self.get_pawn_legal_moves(piece)
            case "R":
                return self.get_rook_legal_moves(piece)
            case "N":
                return self.get_knight_legal_moves(piece)
            case "B":
                return self.get_bishop_legal_moves(piece)
            case "Q":
                return self.get_queen_legal_moves(piece)
            case "K":
                return self.get_king_legal_moves(piece)


def main():
    c = Controller()

if __name__ == "__main__":
    main()