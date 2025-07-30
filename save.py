from fasthtml.common import *
from game import Controller

app, rt = fast_app(live=True)


def css(piece_css):
    return Style("""
        body {
            background-image: url('background_images/background.png');
            background-repeat: repeat-x;
            background-position-x: 300px;
            background-size: 150vh auto;
            min-height: 100vh;
        }
        h1 {
            text-align: center;
            color: white;
            font-size: 2.8em;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 10px;
            margin: 0 auto 20px auto;
            border-radius: 10px;
            max-width: 600px;
        }        
        .board-container {
            position: relative;
            width: 48%;
            margin: 0 auto;
            aspect-ratio: 1;
        }
        .board-img {
            width: 100%;
            height: 100%;
            display: block;
            z-index: 1;
        }
        .board {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-template-rows: repeat(8, 1fr);
            z-index: 2;
        }
        .square {
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .square:hover {
            background-color: rgba(255, 255, 0, 0.3);
        }
        .square.selected {
            background-color: rgba(0, 255, 0, 0.5);
        }
        .square img {
            width: 80%;
            height: 80%;
            object-fit: contain;
            pointer-events: none; /* Prevents piece from blocking click */
        }
        #clicked-info {
            text-align: center;
            color: white;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 10px;
            margin: 20px auto;
            border-radius: 5px;
            max-width: 400px;
        }
        """ + ''.join(piece_css))


def get_board_with_pieces(board):
    images = {"WR": "pieces/WRook.png", "BR": "pieces/BRook.png", "WN": "pieces/WKnight.png",
              "BN": "pieces/BKnight.png", "WB": "pieces/WBishop.png", "BB": "pieces/BBishop.png",
              "WQ": "pieces/WQueen.png", "BQ": "pieces/BQueen.png", "WK": "pieces/WKing.png", "BK": "pieces/BKing.png",
              "WP": "pieces/WPawn.png", "BP": "pieces/BPawn.png"}

    squares = []
    piece_css = []

    for row in range(8):
        for col in range(8):
            # Get piece at this position (if any)
            piece = board[row][col] if board[row][col] != ' ' else None

            # Create square with optional piece
            square_content = []
            if piece:
                square_content.append(
                    Img(src=images[piece.colour + piece.get_letter()[1]],
                        cls=f"piece{row}{col}")
                )

            # Create clickable square
            square = Div(
                *square_content,
                cls=f"square",
                id=f"sq-{row}-{col}",
                hx_post=f"/square_clicked/{row}/{col}",
                hx_target="#clicked-info",
                hx_swap="innerHTML"
            )
            squares.append(square)

    return squares, piece_css


# Route to handle square clicks
@rt('/square_clicked/{row}/{col}')
def square_clicked(row: int, col: int):
    # Convert to chess notation
    files = 'abcdefgh'
    ranks = '87654321'  # Rank 8 is row 0, rank 1 is row 7

    chess_notation = f"{files[col]}{ranks[row]}"

    return f"Clicked: Row {row}, Col {col} = Square {chess_notation}"


@rt('/')
def get():
    c = Controller()
    board = c.generate_board()
    squares, piece_css = get_board_with_pieces(board)

    return Titled("BigJam's Chess Engine",
                  css(piece_css),
                  Div(
                      Img(src="background_images/board.png", cls="board-img"),
                      Div(
                          *squares,
                          cls="board",
                      ),
                      cls="board-container",
                  ),
                  Div(id="clicked-info",
                      children="Click a square to see coordinates"),
                  cls="title",
                  )


serve()