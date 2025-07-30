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
            display: block;
            margin: 20px auto;
            aspect-ratio: 1;
        }
        .board-img {
            width: 100%;
            z-index: 0;
        }
        .board {
            position: absolute;
            top: 0;
            left: 0;
        }
        .image-container {
            position: relative;
            width: 300px;
            height: 200px;
        }
        .overlay {
            position: absolute;
            top: 20px;
            left: 30px;
            z-index: 2;
        }
        .board {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;  /* 8 columns */
            grid-template-rows: 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;     /* 8 rows */
            width: 100%;
            height: 100%;
        }
        /* Click handling squares - invisible overlay */
        .click-square {
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .click-square:hover {
            background-color: rgba(255, 255, 0, 0.3);
        }
        .click-square.selected {
            background-color: rgba(0, 255, 0, 0.5);
        }
        /* Info display */
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


def get_pieces(board):
    images = {"WR": "pieces/WRook.png", "BR": "pieces/BRook.png", "WN": "pieces/WKnight.png",
              "BN": "pieces/BKnight.png", "WB": "pieces/WBishop.png", "BB": "pieces/BBishop.png",
              "WQ": "pieces/WQueen.png", "BQ": "pieces/BQueen.png", "WK": "pieces/WKing.png", "BK": "pieces/BKing.png",
              "WP": "pieces/WPawn.png", "BP": "pieces/BPawn.png"}
    pieces = []
    piece_css = []
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece == ' ':
                continue
            pieces.append(Img(src=images[piece.colour + piece.get_letter()[1]], cls=f"piece{i}{j}"))
            col, row = piece.c2b()
            piece_css.append(".piece" + str(i) + str(j) + """ {
                grid-column: """ + str(row + 1) + """;
                grid-row: """ + str(col + 1) + """;
                justify-self: center;
                align-self: center;
                z-index: 10;
                pointer-events: none; /* Let clicks pass through to squares below */
            }
            """)
    return pieces, piece_css


def get_click_squares(highlighted_positions):
    """Create invisible clickable squares that overlay the entire grid"""
    squares = []
    for row in range(8):
        for col in range(8):
            # Convert to chess notation for display
            files = 'abcdefgh'
            ranks = '87654321'  # Row 0 = rank 8, Row 7 = rank 1
            chess_notation = f"{files[col]}{ranks[row]}"
            highlight = "background-color: rgba(255, 0, 0, 0.3);" if (row, col) in highlighted_positions else ""

            square = Div(
                cls="click-square",
                id=f"sq-{row}-{col}",
                hx_post=f"/square_clicked/{row}/{col}",
                hx_target="#board-area",  # Target the entire board area
                hx_swap="innerHTML",  # Replace the board content
                style=f"grid-column: {col + 1}; grid-row: {row + 1};" + highlight
            )
            squares.append(square)
    return squares


def render_board(board=None):
    """Helper function to render the board - used by both routes"""
    # Initially
    if board is None:
        board = c.g.generate_board()

    pieces, piece_css = get_pieces(board)
    click_squares = get_click_squares(set(map(c.c2b, c.highlighted_squares)))

    return (
        css(piece_css),
        Div(
            Img(src="background_images/board.png", cls="board-img"),
            Div(
                *click_squares,  # Invisible click layer (bottom)
                *pieces,  # Visible pieces (top)
                cls="board",
            ),
        )
    )


# Route to handle square clicks - NOW RETURNS THE UPDATED BOARD
@rt('/square_clicked/{row}/{col}')
def square_clicked(row: int, col: int):
    files = 'abcdefgh'
    ranks = '87654321'
    chess_notation = f"{files[col]}{ranks[row]}"
    c.on_click(chess_notation)

    # Re-render the board with updated highlights
    css_style, board_html = render_board()

    # Return both the updated CSS and the board HTML
    return css_style, board_html


@rt('/')
def get():
    global c
    c = Controller()

    css_style, board_html = render_board()

    return Titled("BigJam's Chess Engine",
                  css_style,
                  Div(
                      board_html,
                      cls="board-container",
                      id="board-area"  # This is what gets replaced
                  ),
                  cls="title",
                  )


serve()