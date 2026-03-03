from fasthtml.common import *
from game import Controller
from engine import Engine
import threading

app, rt = fast_app(live=True)

def css(piece_css):
    return Style("""
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            overflow-x: hidden; /* Prevents horizontal scroll */
        }
        body {
            background-image: url('background_images/background.png');
            background-repeat: repeat-x;
            background-position-x: 300px;
            background-size: 150vh auto;

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
            margin: 20px 20px;
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
        .main-container {
            display: flex;
            justify-content: center;
        }
        .right-side-container h2 {
            color: #717b57;
            width: fit-content;
            border-radius: 5px;
        }
        .promotion-button {
            background-color: #717b57;
            border: solid 1px black;
            border-radius: 5px;
        }
        .promotion-container {
            border: solid 5px black;
            border-radius: 5px;
            background-color: black;
            opacity: 90%;
            display: flex;
            justify-content: center;
            flex-direction: column;
        }
        .board-container {
            margin-top: 0px;
        }
        .moves-display {
            margin-top: 20px;
            border: solid 5px black;
            border-radius: 5px;
            background-color: black;
            opacity: 90%;
            color: #FFFFFF;
            display: flex;
            justify-content: center;
        }
        .turn-msg {
            margin-top: 20px;
            border: solid 5px black;
            border-radius: 5px;
            background-color: black;
            opacity: 90%;
            display: flex;
            justify-content: center;
        }
        .turn-msg h2 {
            margin: 0; /* Remove default margins */
        }
        .piece-msg {
            margin-top: 20px;
            border: solid 5px black;
            border-radius: 5px;
            background-color: black;
            opacity: 90%;
            display: flex;
            justify-content: center;
        }
        .piece-msg h2 {
            margin: 0; /* Remove default margins */
        }
        .eval-msg {
            margin-top: 20px;
            border: solid 5px black;
            border-radius: 5px;
            background-color: black;
            opacity: 90%;
            color: #FFFFFF;
            display: flex;
            justify-content: center;
        }
        .eval-msg h2 {
            margin: 0; /* Remove default margins */
        }
        """ + ''.join(piece_css))

def get_pieces(positions_to_pieces):
    pieces = []
    piece_css = []
    images = {"WR": "pieces/WRook.png", "BR": "pieces/BRook.png", "WN": "pieces/WKnight.png",
              "BN": "pieces/BKnight.png", "WB": "pieces/WBishop.png", "BB": "pieces/BBishop.png",
              "WQ": "pieces/WQueen.png", "BQ": "pieces/BQueen.png", "WK": "pieces/WKing.png", "BK": "pieces/BKing.png",
              "WP": "pieces/WPawn.png", "BP": "pieces/BPawn.png"}

    for square, piece in positions_to_pieces.items():
        file, rank = c.c2b(square)
        pieces.append(Img(src=images[piece.colour + piece.get_letter()[1]], cls=f"piece{file}{rank}"))
        col, row = piece.c2b()
        piece_css.append(".piece" + str(file) + str(rank) + """ {
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


def render_board():
    """Helper function to render the board - used by both routes"""
    pieces, piece_css = get_pieces(c.g.positions_to_pieces)
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
    # Re-render text
    moves_html = get_moves_html()
    turn_html = get_turn_html()
    piece_html = get_selected_piece_html(chess_notation)
    eval_html = get_eval_html()

    # Return both the updated CSS and the board HTML
    return css_style, board_html, moves_html, turn_html, piece_html, eval_html

def get_promotion_button_html():
    return Div(
        H2("Promotion Options"),
        Button(
            "Queen",
            cls="promotion-button",
            hx_post=f"/promotion/Queen",
        ),
        Button(
            "Rook",
            cls="promotion-button",
            hx_post=f"/promotion/Rook",
        ),
        Button(
            "Bishop",
            cls="promotion-button",
            hx_post=f"/promotion/Bishop",
        ),
        Button(
            "Knight",
            cls="promotion-button",
            hx_post=f"/promotion/Knight",
        ),
        cls="promotion-container"
    )

def get_moves_html():
    # num moves we can fit in the display
    n = 20
    # TODO: Implement previously played moves
    # Might want to store the piece (if not pawn) that made the move too (in played_moves in c.move())
    # for prev, new in c.g.played_moves.items()[-n:]:
    #     pass

    return Div(
        H2("Played Moves"),
        cls="moves-display",
        id="moves-display",
        hx_swap_oob="true",
    )

@app.post('/promotion/Queen')
def promote_to_queen():
    c.set_promotion("Q")
    event.set()
    return "Queen"

@app.post('/promotion/Rook')
def promote_to_rook():
    c.set_promotion("R")
    event.set()
    return "Rook"

@app.post('/promotion/Bishop')
def promote_to_bishop():
    c.set_promotion("B")
    event.set()
    return "Bishop"

@app.post('/promotion/Knight')
def promote_to_knight():
    c.set_promotion("K")
    event.set()
    return "Knight"

def get_turn_html():
    colour = "White" if c.g.turn == "W" else "Black"
    # Could be checkmate or stalemate
    mate = "White Wins!" if c.g.mate == "W" else "Black Wins!" if c.g.mate == "B" else "Draw!"
    return Div(
        # Checkmate msg here
        H2(f"{colour} to move" if not c.g.mate else mate),
        cls="turn-msg",
        id="turn-display",
        hx_swap_oob="true",
    )

def get_selected_piece_html(coords=""):
    pieces = {"K": "King", "Q": "Queen", "B": "Bishop", "N": "Knight", "R": "Rook", "P": "Pawn"}
    piece = pieces[c.g.selected_piece.letter] if c.g.selected_piece else ""
    return Div(
        H2(f"{piece} ({coords})" if piece else "No Piece Selected"),
        cls="piece-msg",
        id="piece-display",
        hx_swap_oob="true",
    )

def get_eval_html():
    evaluation = round(engine.calculate_eval(), 2)
    evaluation = str(evaluation) if evaluation <= 0 else "+" + str(evaluation)
    return Div(
        H2(f"Eval: {evaluation}"),
        cls="eval-msg",
        id="eval-display",
        hx_swap_oob="true",
    )

@rt('/')
def get():
    global c
    global event
    global engine

    # Could add a condition to not create event when two AIs play each other
    event = threading.Event()
    c = Controller(event)
    engine = Engine(c)

    css_style, board_html = render_board()
    button_html = get_promotion_button_html()
    moves_html = get_moves_html()
    turn_html = get_turn_html()
    piece_html = get_selected_piece_html()
    eval_html = get_eval_html()

    return Titled("Chess",
                  css_style,
                  Div(
                      Div(
                          board_html,
                          cls="board-container",
                          id="board-area"  # This is what gets replaced
                      ),
                      Div(
                          button_html,
                            turn_html,
                            piece_html,
                            eval_html,
                            moves_html,
                          cls="right-side-container"
                      ),
                  cls="main-container"),
                  cls="title",
                  )

serve()