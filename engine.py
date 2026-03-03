from game import Controller

PIECE_VALUES = {"P": 1, "N": 3, "B": 3.05, "R": 5, "Q": 9}

class ArrayTree:
    def __init__(self):
        self.values = []  # Node values
        self.parent_indices = []  # Parent index for each node
        self.first_child = []  # Index of first child
        self.next_sibling = []  # Index of next sibling

    def add_node(self, value, parent_idx=None):
        idx = len(self.values)
        self.values.append(value)
        self.parent_indices.append(parent_idx)
        self.first_child.append(None)
        self.next_sibling.append(None)

        if parent_idx is not None:
            # Link as child
            if self.first_child[parent_idx] is None:
                self.first_child[parent_idx] = idx
            else:
                # Find last sibling
                sibling = self.first_child[parent_idx]
                while self.next_sibling[sibling] is not None:
                    sibling = self.next_sibling[sibling]
                self.next_sibling[sibling] = idx

        return idx

    def get_children(self, parent_idx):
        children = []
        child_idx = self.first_child[parent_idx]
        while child_idx is not None:
            children.append(child_idx)
            child_idx = self.next_sibling[child_idx]
        return children


# Very memory efficient, cache-friendly

class Engine:
    def __init__(self, c):
        self.c = c

    def calculate_eval(self, pos=None):
        """Given a mapping of pieces to positions, evaluates the position"""
        if not pos:
            pos = self.c.g.positions_to_pieces
        evaluation = 0
        evaluation += self.count_material(pos)
        return evaluation

    def count_material(self, positions_to_pieces):
        evaluation = 0
        for piece in positions_to_pieces.values():
            if piece.letter != "K":
                match piece.colour:
                    case "W":
                        evaluation += PIECE_VALUES[piece.letter]
                    case "B":
                        evaluation -= PIECE_VALUES[piece.letter]
        return evaluation
    def eval_to_depth_n(self, state, depth=1):
        pass

    # def eval_to_depth_n(self, state, depth=1, alpha, beta, maximisingPlayer):
    #     # Initial Call: alphabeta(origin, depth, −∞, +∞, TRUE)
    #     if depth == 0 or self.c.is_checkmate():
    #         return self.calculate_eval(self.c.g.positions_to_pieces)
    #
    #     evals = {}
    #     positions = {}
    #     snapshot = None
    #     # snapshot points to a dict of the game state after playing the move
    #     for piece, square in self.c.h.get_all_legal_moves(self.c.g.turn, snapshot):
    #         evals[(piece, square)] = self.c.get_eval_of_pos(piece, square, self.calculate_eval)
    #
    #     if maximisingPlayer:
    #         eval = float("-inf")
    #
    #         for piece, square in self.c.h.get_all_legal_moves(self.c.g.turn, snapshot):
    #             eval = max(eval, self.eval_to_depth_n(child_node, depth-1, alpha, beta, False))
    #             if eval >= beta:
    #                 break
    #             alpha = max(alpha, eval)
    #         return eval
    #     else:
    #         eval = float("inf")
    #
    #         for piece, square in self.c.h.get_all_legal_moves(self.c.g.turn, snapshot):
    #             eval = min(eval, self.eval_to_depth_n(child_node, depth-1, alpha, beta, True))
    #             if eval >= alpha:
    #                 break
    #             beta = min(beta, eval)
    #         return eval




    # def eval_to_depth_n(self, node, depth=1):
    #     pass
