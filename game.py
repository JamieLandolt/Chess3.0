from pieces import *
import copy

FIFTY_MOVE_RULE_CAP = 99

class Controller:
    def __init__(self, event):
        self.g = Game(self)
        self.h = HelperFunctions(self)
        # I don't think self.event needs to be saved when the game state is saved for simulating moves
        self.event = event
        self.highlighted_squares = []
        self.simulating_check = False

    def c2b(self, coord):
        """Converts chess coords (a1) to board coords (0, 0)"""
        coords = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return (8 - int(coord[1]), coords[coord[0]])

    def b2c(self, coord):
        alpha = 'abcdefgh'
        return alpha[coord[1]] + str(8 - coord[0])

    def remove_highlighted_squares(self):
        for square in self.h.get_legal_moves(self.g.selected_piece):
            if square in self.highlighted_squares:
                self.highlighted_squares.remove(square)
            else:
                raise Exception(f"Tried to but couldn't remove {square} from highlighted squares!")

    def deselect_piece(self):
        self.g.selected_piece = None

    def select_piece(self, square):
        self.g.selected_piece = self.g.positions_to_pieces[square]
        legals = self.h.get_legal_moves(self.g.selected_piece)
        self.highlighted_squares.extend(legals)

    def flip_turn(self):
        self.g.turn = "B" if self.g.turn == "W" else "W"

    def on_click(self, square):
        """When a square is clicked, this function is run with the parameter being the square clicked (e4)"""
        # Game Over
        if self.g.mate:
            return

        # Select a piece if none selected and one was clicked
        if not self.g.selected_piece:
            if self.g.positions_to_pieces.get(square, None):
                self.select_piece(square)
            return

        # Check if piece can move to square
        legals = self.h.get_legal_moves(self.g.selected_piece)
        if square in legals and self.g.turn == self.g.selected_piece.colour:
            # Important that we remove_highlights before moving
            # as it relies on the current position of the selected piece
            self.remove_highlighted_squares()
            self.g.move(self.g.selected_piece, square)
            self.deselect_piece()
            self.flip_turn()
        # Select the clicked piece if it piece can't be taken by the currently selected piece
        elif self.g.positions_to_pieces.get(square, None):
            self.remove_highlighted_squares()
            self.deselect_piece()
            self.select_piece(square)
        else:
            # Deselect piece if invalid square
            self.remove_highlighted_squares()
            self.deselect_piece()
        return

    def save_state(self):
        return copy.deepcopy({
            'positions_to_pieces': self.g.positions_to_pieces,
            'white_attacked_squares': self.g.white_attacked_squares,
            'black_attacked_squares': self.g.black_attacked_squares,
            'selected_piece': self.g.selected_piece,
            'promotion_piece': self.g.promotion_piece,
            'turn': self.g.turn,
            'white_king': self.g.white_king,
            'black_king': self.g.black_king,
            'highlighted_squares': self.highlighted_squares,
            'en_passant': self.h.en_passant,
            'en_passantee': self.h.en_passantee,
            'promotion_letter': self.g.promotion_letter,
            'played_moves': self.g.played_moves,
            'mate': self.g.mate,
            'fifty_move_counter': self.g.fifty_move_counter,
            'position_hashes': self.g.position_hashes
        })

    def restore_state(self, state):
        for key, value in state.items():
            if hasattr(self.g, key):
                setattr(self.g, key, value)
            elif hasattr(self.h, key):
                setattr(self.h, key, value)
            elif hasattr(self, key):
                setattr(self, key, value)

    def in_check_after_move(self, piece, square, snapshot=None):
        """Simulates a single move and reverts the game state back to as if the move was never played.
        The move should not appear on the board."""
        # SAVE GAME STATE BEFORE SIMULATION
        state = self.save_state()

        # PERFORM SIMULATION
        self.simulating_check = True
        self.g.move(piece, square)
        check = self.h.in_check(piece.colour)
        # Save the position in case the caller wants to see what position you evaluated
        snapshot = state
        self.simulating_check = False

        # RESTORE SAVED STATE
        self.restore_state(state)
        return check

    def get_eval_of_pos(self, piece, square, eval_func):
        # SAVE GAME STATE BEFORE SIMULATION
        state = self.save_state()

        # PERFORM SIMULATION
        self.g.move(piece, square)
        evaluation = eval_func(self.g.positions_to_pieces)
        # Might need to .copy() the pos2pieces if bugging
        pos = self.g.positions_to_pieces

        # RESTORE SAVED STATE
        self.restore_state(state)

        return evaluation, pos

    def remove_moves_that_result_in_check(self, moves, piece, snapshot=None):
        original_square = piece.coords
        # Without resetting piece.coords to the original square
        # The piece variable in this function references the pawn that was moved.
        # Then when the state is restored, the reference is kept and it is still on the square
        # That it was moved to
        legals = set()
        for move in moves:
            piece.coords = original_square
            if not self.in_check_after_move(piece, move, snapshot):
                legals.add(move)
            piece.coords = original_square
        return legals

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

    def set_promotion(self, piece):
        self.g.promotion_letter = piece

    def is_checkmate(self):
        return self.g.mate in "WB"


class Game:
    def __init__(self, c: Controller):
        # A reference to the Controller
        self.c = c
        self.initialise_state()

        # TODO: Implement button to select player colours & this should be initially None
        self.player_colours = ["W"]

    def initialise_state(self):
        """Initialises the variables that are needed for a fresh wipe of the game state"""
        # Maps squares to their pieces
        self.positions_to_pieces = {}
        self.played_moves = {}
        self.position_hashes = {}
        self.white_attacked_squares = {"a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3"}
        self.black_attacked_squares = {"a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6"}

        # A reference to the white and black kings
        self.white_king = None
        self.black_king = None
        # The currently selected piece (Legal moves are shown)
        self.selected_piece = None
        # This should be reset to None on promotion
        # Queues up the next promotion to be to this piece
        self.promotion_piece = None
        # The letter of the piece to be promoted to
        self.promotion_letter = None

        # Whose turn it is
        self.turn = "W"
        # Checkmate (W = White Wins, B) or draw (D)
        self.mate = ""
        self.fifty_move_counter = 0

        self.set_up_pieces()

    def set_up_pieces(self):
        """Sets up the original piece mapping of positions to pieces.
        Also stores a reference to each king"""

        # Black Pieces
        self.positions_to_pieces["a8"] = Rook("a8", colour="B")
        self.positions_to_pieces["b8"] = Knight("b8", colour="B")
        self.positions_to_pieces["c8"] = Bishop("c8", colour="B")
        self.positions_to_pieces["d8"] = Queen("d8", colour="B")
        self.positions_to_pieces["e8"] = King("e8", colour="B")
        self.positions_to_pieces["f8"] = Bishop("f8", colour="B")
        self.positions_to_pieces["g8"] = Knight("g8", colour="B")
        self.positions_to_pieces["h8"] = Rook("h8", colour="B")
        self.black_king = self.positions_to_pieces["e8"]

        # White Pieces
        self.positions_to_pieces["a1"] = Rook("a1", colour="W")
        self.positions_to_pieces["b1"] = Knight("b1", colour="W")
        self.positions_to_pieces["c1"] = Bishop("c1", colour="W")
        self.positions_to_pieces["d1"] = Queen("d1", colour="W")
        self.positions_to_pieces["e1"] = King("e1", colour="W")
        self.positions_to_pieces["f1"] = Bishop("f1", colour="W")
        self.positions_to_pieces["g1"] = Knight("g1", colour="W")
        self.positions_to_pieces["h1"] = Rook("h1", colour="W")
        self.white_king = self.positions_to_pieces["e1"]

        # Black Pawns
        alpha = 'abcdefgh'
        for i in range(8):
            square = alpha[i] + "7"
            self.positions_to_pieces[square] = Pawn(square, colour="B")

        # White Pawns
        for i in range(8):
            square = alpha[i] + "2"
            self.positions_to_pieces[square] = Pawn(square, colour="W")

        self.position_hashes[(self.turn, frozenset(self.positions_to_pieces.items()))] = 1

    def remove_en_passant_privileges(self):
        if self.c.h.en_passantee:
            self.c.h.en_passantee.can_be_en_passanted = False
            self.c.h.en_passantee = None

    def provide_en_passant_privileges(self, piece, square):
        en_passant_rank = {"W": "4", "B": "5"}
        if piece.letter == "P":
            if square[1] == en_passant_rank[piece.colour] and piece.coords[1] == "2" if piece.colour == "W" else "7":
                piece.can_be_en_passanted = True
                self.c.h.en_passantee = piece

    def remove_castling_privileges(self, piece):
        if piece.letter in ('R', 'K'):
            piece.castling_rights = False

    def shift_piece(self, piece, square):
        # If capturing reset
        if self.positions_to_pieces.get(square, None):
            self.fifty_move_counter = 0
        self.fifty_move_counter += 1

        # Remove piece from square
        self.positions_to_pieces.pop(piece.coords)
        # Update piece coords
        piece.coords = square
        # Place piece on new square
        self.positions_to_pieces[square] = piece

        if piece.letter == "K":
            match piece.colour:
                case "B":
                    self.black_king = piece
                case "W":
                    self.white_king = piece

    def promote(self, piece):
        # Wait for a promotion piece to be selected
        self.c.event.wait()

        # Create the new piece
        match self.promotion_letter:
            case "Q":
                promotee = Queen(piece.coords, piece.colour)
            case "R":
                # Rook obv can't castle after it is promoted to
                promotee = Rook(piece.coords, piece.colour, castling_rights=False)
            case "B":
                promotee = Bishop(piece.coords, piece.colour)
            case "N":
                promotee = Knight(piece.coords, piece.colour)

        # Replace the old piece
        self.positions_to_pieces[piece.coords] = promotee
        # Reset the promotion piece so it doesn't auto promote next time to the last selected piece
        self.promotion_piece = None

    def move(self, piece, square):
        """Takes a piece and moves it to the new square"""

        self.remove_castling_privileges(piece)

        # If a piece could be en passanted last move, remove its privileges
        self.remove_en_passant_privileges()

        # Check if pawn moved onto correct rank to be en passanted on next move
        self.provide_en_passant_privileges(piece, square)

        # Check if they are castling so we can move the rook
        if piece.letter == "K" and abs(ord(piece.coords[0]) - ord(square[0])) == 2:
            match square[0]:
                case 'c':
                    rook = self.positions_to_pieces["a" + square[1]]
                    self.shift_piece(rook, "d" + square[1])
                case 'g':
                    rook = self.positions_to_pieces["h" + square[1]]
                    self.shift_piece(rook, "f" + square[1])

        # Store the move and move the piece
        self.played_moves[piece.coords] = square
        self.shift_piece(piece, square)

        # Check if promoting, if you think for a sec this 1, 8 condition is fine
        if piece.letter == "P":
            # Reset 50 move rule
            self.fifty_move_counter = 0
            if piece.coords[1] in ("1", "8") and not self.c.simulating_check:
                self.promote(piece)

        # Remove piece from old square when en passanting
        for old_square, new_square in self.c.h.en_passant:
            if new_square == square:
                self.positions_to_pieces.pop(old_square)
                break

        # Reset the list of en passants that can be played
        self.c.h.en_passant = []
        # Update which squares are being attacked by both colours
        self.c.h.get_attacked_squares()

        # Check for checkmate / stalemate
        opp_king = self.white_king if piece.colour == "B" else self.black_king
        attacked_squares = self.white_attacked_squares if piece.colour == "W" else self.black_attacked_squares

        # This stops infinite recursion where legal moves needs legal moves to check legal moves
        # TLDR Don't check for checkmate when we are checking if they are in check
        if self.c.simulating_check:
            return

        # Stalemate + Checkmate below here
        # 50 move rule
        if self.fifty_move_counter > FIFTY_MOVE_RULE_CAP:
            self.mate = "D"

        # Store the position
        pos_hash = ("W" if self.turn == "B" else "B", frozenset(self.positions_to_pieces.items()))
        self.position_hashes[pos_hash] = self.position_hashes.get(pos_hash, 0) + 1

        # 3 Fold Repetition
        if self.position_hashes[pos_hash] > 2:
            self.mate = "D"

        # If a single iteration of this loops occurs it means there is a legal move for the opposite colour
        # Thus, not checkmate or stalemate
        for _ in self.c.h.get_all_legal_moves("W" if piece.colour == "B" else "B"):
            return

        # It must be either checkmate or stalemate at this point
        checkmate = opp_king.coords in attacked_squares
        if checkmate:
            self.mate = piece.colour
        else: # Stalemate
            self.mate = "D"

class HelperFunctions:
    def __init__(self, c: Controller):
        # IF YOU ADD A NEW VARIABLE TO THE STATE, ADD IT TO THE SAVE STATE AND RESTORE STATE FUNCTIONS
        # OTHERWISE YOU RISK IT BEING CORRUPTED WHEN MOVES ARE SIMULATED USING Controller.simulate_move()
        self.c = c
        self.en_passant = []
        self.en_passantee = None

    def get_piece_on(self, square):
        """Returns the piece on the given square, None if there is no piece"""
        return self.c.g.positions_to_pieces[square]

    def square_free(self, square, colour, capture=None, en_passant=False):
        """Returns True iff there is no piece on the square of the same colour given and the square is on the board
        Capture Parameter:
        False -> captures are disabled |
        True -> only captures are allowed |
        None -> captures are allowed but not forced"""
        if not square:
            return False

        # .get is important i think smth to do with pieces off the board
        occupant = self.c.g.positions_to_pieces.get(square, ' ')

        if capture == True:
            can_move = occupant != ' ' and occupant.colour != colour
        elif capture == False:
            can_move = occupant == ' '
        else:
            can_move = occupant == ' ' or occupant.colour != colour

        if en_passant:
            can_move = can_move and occupant != ' ' and occupant.letter == "P" and occupant.can_be_en_passanted

        return can_move and self.square_on_board(square)

    def square_on_board(self, square):
        """Returns True iff the square is on the board (between 'a1' to 'h8')"""
        return square[0] in 'abcdefgh' and square[1] in '12345678'

    def filter_moves(self, piece, legals):
        """Filters out empty squares ('') and those which have a piece on of the same colour (can't capture same
        colour)"""
        return set(filter(lambda x: self.square_free(x, piece.colour), legals))

    def in_check(self, colour):
        return self.c.g.white_king.coords in self.c.g.black_attacked_squares if colour == "W" else (
                self.c.g.black_king.coords in self.c.g.white_attacked_squares
        )

    def get_attacked_squares(self):
        """Constructs a set of every square that is attacked, refreshes automatically upon each move"""
        self.c.g.white_attacked_squares = set()
        self.c.g.black_attacked_squares = set()
        for piece in self.c.g.positions_to_pieces.values():
            if piece.colour == "W":
                self.c.g.white_attacked_squares |= self.get_possible_moves(piece)
            else:
                self.c.g.black_attacked_squares |= self.get_possible_moves(piece)

    def get_all_legal_moves(self, colour, snapshot=None):
        """A generator which produces all legal moves for the given colour.
        The pos argument (if given) gets set to the last position the generator evaluated."""
        # Checking king first saves time sometimes when checking for checkmate
        king = self.c.g.white_king if colour == "W" else self.c.g.black_king
        for move in self.get_legal_moves(king, snapshot):
            yield king, move
        for piece in list(self.c.g.positions_to_pieces.values()).copy():
            if piece != king and piece.colour == colour:
                for move in self.get_legal_moves(piece, snapshot):
                    yield piece, move

    def get_all_possible_moves(self, colour):
        """A generator which produces all possible (not necessarily legal, for that use get_all_legal_moves) moves for the given colour"""
        king = self.c.g.white_king if colour == "W" else self.c.g.black_king
        for move in self.get_possible_moves(king):
            yield king, move
        for piece in self.c.g.positions_to_pieces.values():
            if piece != king and piece.colour == colour:
                for move in self.get_possible_moves(piece):
                    yield piece, move

    def get_pawn_possible_moves(self, piece):
        moves = set()

        # Account for W or B piece colour
        starting_rank = '2' if piece.colour == "W" else '7'
        op = "*" if piece.colour == "W" else '/'

        above_sq = piece.get_square(op, 1)
        if self.square_free(above_sq, piece.colour, capture=False):
            moves.add(above_sq)

            # On second rank (double move)
            if piece.coords[1] == starting_rank:
                above_sq2 = piece.get_square(op, 2) # capture=False -> See self.square_free()
                if self.square_free(above_sq2, piece.colour, capture=False):
                    moves.add(above_sq2)

        # Capture left or right
        if above_sq:
            ur_square = piece.get_square("+", 1, above_sq) # capture=True -> See self.square_free()
            if self.square_free(ur_square, piece.colour, capture=True):
                moves.add(ur_square)
            ul_square = piece.get_square("-", 1, above_sq)
            if self.square_free(ul_square, piece.colour, capture=True):
                moves.add(ul_square)

        # En Passant
        en_passant_offset = {"B": "/", "W": "*"}
        en_passant_rank = {"W": "5", "B": "4"}
        r_square = piece.get_square("+", 1)

        # Only check if it's on the correct rank
        if piece.coords[1] == en_passant_rank[piece.colour]:
            # If opposite coloured pawn that just moved is to the right
            if self.square_free(r_square, piece.colour, capture=True, en_passant=True):
                end_square = piece.get_square(en_passant_offset[piece.colour], 1,  r_square)
                # Encode so self.c.g.move() knows it is en passant and which piece is taken
                self.en_passant.append((r_square, end_square))
                moves.add(end_square)

            l_square = piece.get_square("-", 1)
            if self.square_free(l_square, piece.colour, capture=True, en_passant=True):
                end_square = piece.get_square(en_passant_offset[piece.colour], 1,  l_square)
                self.en_passant.append((l_square, end_square))
                moves.add(end_square)

        return moves

    def get_rook_possible_moves(self, piece):
        moves = set()

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
                moves.add(piece.get_square('*', i))

            if dirs["D"]:
                square = piece.get_square('/', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                if occupant:
                    dirs["D"] = 0
                moves.add(square)

            if dirs["R"]:
                square = piece.get_square('+', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                if occupant:
                    dirs["R"] = 0
                moves.add(square)

            if dirs["L"]:
                square = piece.get_square('-', i)
                occupant = self.c.g.positions_to_pieces.get(square, None)
                if occupant:
                    dirs["L"] = 0
                moves.add(square)

            # All directions blocked -> Stop checking
            if not any(dirs):
                return moves

        return self.filter_moves(piece, moves)

    def get_knight_possible_moves(self, piece):
        moves = set()
        up2 = piece.get_square('*', 2)
        down2 = piece.get_square('/', 2)
        left2 = piece.get_square('-', 2)
        right2 = piece.get_square('+', 2)

        if up2:
            moves.add(piece.get_square('-', 1, up2))
            moves.add(piece.get_square('+', 1, up2))
        if down2:
            moves.add(piece.get_square('-', 1, down2))
            moves.add(piece.get_square('+', 1, down2))
        if left2:
            moves.add(piece.get_square('/', 1, left2))
            moves.add(piece.get_square('*', 1, left2))
        if right2:
            moves.add(piece.get_square('/', 1, right2))
            moves.add(piece.get_square('*', 1, right2))

        return self.filter_moves(piece, moves)

    def get_bishop_possible_moves(self, piece):
        moves = set()
        # Tracks which diagonals have run into a piece / edge of board (can't jump piece or edge of board)
        diags = {"UR": 1, "UL": 1, "DR": 1, "DL": 1}

        for i in range(1, 9):
            up_i = piece.get_square('*', i)
            down_i = piece.get_square('/', i)

            # Stop searching diagonals if all have hit a wall/piece
            if not any(diags.values()):
                return self.filter_moves(piece, moves)

            # if up_i avoids passing in '' as up_i for invalid square (when square not on board)
            if up_i:
                # Check we aren't jumping pieces
                if diags["UR"]:
                    square = piece.get_square('+', i, up_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    # Check if diag ends (piece hit)
                    if occupant:
                        diags["UR"] = 0
                    moves.add(square)
                if diags["UL"]:
                    square = piece.get_square('-', i, up_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    if occupant:
                        diags["UL"] = 0
                    moves.add(square)
            if down_i:
                if diags["DR"]:
                    square = piece.get_square('+', i, down_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    if occupant:
                        diags["DR"] = 0
                    moves.add(square)
                if diags["DL"]:
                    square = piece.get_square('-', i, down_i)
                    occupant = self.c.g.positions_to_pieces.get(square, None)
                    if occupant:
                        diags["DL"] = 0
                    moves.add(square)

        return self.filter_moves(piece, moves)

    def get_queen_possible_moves(self, piece):
        return self.get_bishop_possible_moves(piece).union(self.get_rook_possible_moves(piece))

    def get_king_possible_moves(self, piece):
        moves = set()

        up_1 = piece.get_square('*', 1)
        moves.add(up_1)
        down_1 = piece.get_square('/', 1)
        moves.add(down_1)
        right_1 = piece.get_square('+', 1)
        moves.add(right_1)
        left_1 = piece.get_square('-', 1)
        moves.add(left_1)

        # Diags - if up_1 to avoid error for passing empty str into .get_square()
        if up_1:
            square = piece.get_square('+', 1, up_1)
            moves.add(square)
            square = piece.get_square('-', 1, up_1)
            moves.add(square)
        if down_1:
            square = piece.get_square('+', 1, down_1)
            moves.add(square)
            square = piece.get_square('-', 1, down_1)
            moves.add(square)

        # Castling
        if piece.castling_rights:
            # rook_positions = {"WL": "a1", "WR": "h1", "BL": "a8", "BR": "h8"}
            rook_positions = ["a1", "h1"] if piece.colour == "W" else ["a8", "h8"]

            # To the left of the king 1, 2, 3 squares
            l1 = piece.get_square('-', 1)
            l2 = piece.get_square('-', 2)
            l3 = piece.get_square('-', 3)

            r1 = piece.get_square('+', 1)
            r2 = piece.get_square('+', 2)

            # Pieces on those squares
            pl1 = self.c.g.positions_to_pieces.get(l1, None)
            pl2 = self.c.g.positions_to_pieces.get(l2, None)
            pl3 = self.c.g.positions_to_pieces.get(l3, None)

            pr1 = self.c.g.positions_to_pieces.get(r1, None)
            pr2 = self.c.g.positions_to_pieces.get(r2, None)

            no_pieces_left = not (pl1 or pl2 or pl3)
            no_pieces_right = not (pr1 or pr2)

            attacked_squares = self.c.g.black_attacked_squares if piece.colour == "W" else self.c.g.white_attacked_squares
            no_attacked_squares_left = all(map(lambda x: x not in attacked_squares, (l1, l2, l3)))
            no_attacked_squares_right = all(map(lambda x: x not in attacked_squares, (r1, r2)))

            # Locate each rook and check if it can castle
            for position in rook_positions:
                potential_rook = self.c.g.positions_to_pieces.get(position, None)

                if potential_rook and potential_rook.letter == "R" and potential_rook.castling_rights:
                    # Check for empty and not attacked spaces to the left and right of king
                    no_pieces_blocking = no_pieces_left if position[0] == "a" else no_pieces_right
                    no_attacked_squares = no_attacked_squares_left if position[0] == "a" else no_attacked_squares_right

                    if no_pieces_blocking and no_attacked_squares and not self.in_check(piece.colour):
                        moves.add(l2 if position[0] == "a" else r2)

        return self.filter_moves(piece, moves)

    def get_possible_moves(self, piece):
        match piece.letter:
            case "P":
                return self.get_pawn_possible_moves(piece)
            case "R":
                return self.get_rook_possible_moves(piece)
            case "N":
                return self.get_knight_possible_moves(piece)
            case "B":
                return self.get_bishop_possible_moves(piece)
            case "Q":
                return self.get_queen_possible_moves(piece)
            case "K":
                return self.get_king_possible_moves(piece)

    def get_legal_moves(self, piece, snapshot=None):
        return self.c.remove_moves_that_result_in_check(self.get_possible_moves(piece), piece, snapshot)