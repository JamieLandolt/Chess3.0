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

    def remove_highlighted_squares(self):
        for square in self.h.get_legal_moves(self.g.selected_piece):
            self.highlighted_squares.remove(square)

    def deselect_piece(self):
        self.g.selected_piece = None

    def select_piece(self, square):
        self.g.selected_piece = self.g.positions_to_pieces[square]
        self.highlighted_squares.extend(self.h.get_legal_moves(self.g.selected_piece))

    def flip_turn(self):
        self.g.turn = "B" if self.g.turn == "W" else "W"

    def on_click(self, square):
        """When a square is clicked, this function is run with the parameter being the square clicked (e4)"""
        print("CHECKING WHETHER TO MOVE")
        if not self.g.selected_piece:
            print("NO PIECE SELECTED")
            if self.g.positions_to_pieces.get(square, None):
                self.select_piece(square)
            return

        # At this point we have selected a piece, then clicked a square to move it to that square
        # If same piece clicked deselect
        if square == self.g.selected_piece:
            print("SAME PIECE CLICKED")
            self.remove_highlighted_squares()
            self.deselect_piece()
            return

        # Check if piece can move to square
        if square in self.h.get_legal_moves(self.g.selected_piece) and self.g.turn == self.g.selected_piece.colour:
            print("MOVING")
            self.remove_highlighted_squares()
            self.g.move(self.g.selected_piece, square)
            self.deselect_piece()
            self.flip_turn()
        else:
            # Deselect piece if invalid square
            print(f"Piece: {self.g.selected_piece} cannot move to square: {square}")
            self.remove_highlighted_squares()
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
        self.set_up_pieces()
        # The currently selected piece (Legal moves are shown)
        self.selected_piece = None
        # Whose turn it is
        self.turn = "W"
        # This controls whether the game is running (Running iff not None)
        # TODO: Implement button to select player colours & this should be initially None
        self.player_colours = ["W"]

    def set_up_pieces(self):
        # Black Pieces
        self.positions_to_pieces["a8"] = Rook("a8", colour="B")
        self.positions_to_pieces["b8"] = Knight("b8", colour="B")
        self.positions_to_pieces["c8"] = Bishop("c8", colour="B")
        self.positions_to_pieces["d8"] = Queen("d8", colour="B")
        self.positions_to_pieces["e8"] = King("e8", colour="B")
        self.positions_to_pieces["f8"] = Bishop("f8", colour="B")
        self.positions_to_pieces["g8"] = Knight("g8", colour="B")
        self.positions_to_pieces["h8"] = Rook("h8", colour="B")

        # White Pieces
        self.positions_to_pieces["a1"] = Rook("a1", colour="W")
        self.positions_to_pieces["b1"] = Knight("b1", colour="W")
        self.positions_to_pieces["c1"] = Bishop("c1", colour="W")
        self.positions_to_pieces["d1"] = Queen("d1", colour="W")
        self.positions_to_pieces["e1"] = King("e1", colour="W")
        self.positions_to_pieces["f1"] = Bishop("f1", colour="W")
        self.positions_to_pieces["g1"] = Knight("g1", colour="W")
        self.positions_to_pieces["h1"] = Rook("h1", colour="W")

        # Black Pawns
        alpha = 'abcdefgh'
        for i in range(8):
            square = alpha[i] + "7"
            self.positions_to_pieces[square] = Pawn(square, colour="B")

        # White Pawns
        for i in range(8):
            square = alpha[i] + "2"
            self.positions_to_pieces[square] = Pawn(square, colour="W")

    def move(self, piece, square):
        """Takes a piece and moves it to the new square"""
        # Remove piece from square
        self.positions_to_pieces.pop(piece.coords)
        # Update piece coords
        piece.coords = square
        # Place piece on new square
        self.positions_to_pieces[square] = piece

class HelperFunctions:
    def __init__(self, c: Controller):
        self.c = c

    def get_piece_on(self, square):
        """Returns the piece on the given square, None if there is no piece"""
        return self.c.g.positions_to_pieces[square]

    def square_free(self, square, colour, capture=None):
        """Returns True iff there is no piece on the square of the same colour given and the square is on the board
        Capture Parameter:
        False -> captures are disabled |
        True -> only captures are allowed |
        None -> captures are allowed but not forced"""
        # .get is important i think smth to do with pieces off the board
        if not square:
            return False
        occupant = self.c.g.positions_to_pieces.get(square, ' ')
        if capture == True:
            can_move = occupant != ' ' and occupant.colour != colour
        elif capture == False:
            can_move = occupant == ' '
        else:
            can_move = occupant == ' ' or occupant.colour != colour
        return can_move and self.square_on_board(square)

    def square_on_board(self, square):
        """Returns True iff the square is on the board (between 'a1' to 'h8')"""
        return square[0] in 'abcdefgh' and square[1] in '12345678'

    def filter_moves(self, piece, legals):
        """Filters out empty squares ('') and those which have a piece on of the same colour (can't capture same colour)"""
        return set(filter(lambda x: self.square_free(x, piece.colour), legals))


    def get_pawn_legal_moves(self, piece):
        legals = set()
        # TODO: Captures, En Passant

        # Account for W or B piece colour
        starting_rank = '2' if piece.colour == "W" else '7'
        op = "*" if piece.colour == "W" else '/'

        above_sq = piece.get_square(op, 1)
        if self.square_free(above_sq, piece.colour, capture=False):
            legals.add(above_sq)

            # On second rank (double move)
            if piece.coords[1] == starting_rank:
                above_sq2 = piece.get_square(op, 2) # capture=False -> See self.square_free()
                if self.square_free(above_sq2, piece.colour, capture=False):
                    legals.add(above_sq2)

        # Capture left or right
        ur_square = piece.get_square("+", 1, above_sq) # capture=True -> See self.square_free()
        if self.square_free(ur_square, piece.colour, capture=True):
            legals.add(ur_square)
        ul_square = piece.get_square("-", 1, above_sq)
        if self.square_free(ul_square, piece.colour, capture=True):
            legals.add(ul_square)



        return legals

    def get_rook_legal_moves(self, piece):
        legals = set()

        # Tracks which directions are blocked
        dirs = {"U": 1, "R": 1, "D": 1, "L": 1}

        for i in range(1, 9):
            # Check we haven't run into a piece beforehand
            if dirs["U"]:
                square = piece.get_square('*', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                # If we run into a piece ensure we don't check further than it
                if occupant:
                    dirs["U"] = 0
                legals.add(piece.get_square('*', i))

            if dirs["D"]:
                square = piece.get_square('/', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                if occupant:
                    dirs["D"] = 0
                legals.add(square)

            if dirs["R"]:
                square = piece.get_square('+', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                if occupant:
                    dirs["R"] = 0
                legals.add(square)

            if dirs["L"]:
                square = piece.get_square('-', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                if occupant:
                    dirs["L"] = 0
                legals.add(square)

            # All directions blocked -> Stop checking
            if not any(dirs):
                return legals

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
                return self.filter_moves(piece, legals)

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
        # TODO: Castles, Checks

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