# Chess
Third time creating chess, this time the UI actually looks a bit nicer and all rules (even the very niche) are implemented.

*E.g. Can't castle over a checked square. Can't move a pinned piece. En Passant...*

<img width="1440" height="813" alt="Screenshot 2026-03-04 at 9 14 13 am" src="https://github.com/user-attachments/assets/434c0f1a-a301-417b-9755-628056b9280d" />

## Tech Stack
### Python
- FastHTML for website

*Decided to keep it simple rather than overcomplicate it unnecessarily.*

## Project Structure
### main.py

As there is no main function needed to run the FastHTML app, main.py handles the UI and calls game.py and engine.py.

### game.py
- Controller class handles saving and reverting the game state for easy illegal move detection and interactions between user and game *(user highlights a square or clicks a piece)*
- Game class handles game logic *(board setup, promotion, moving)*
- HelperFunctions class handles QOL functions *(checks for pieces on squares, getters for legal moves/attacked squares/possible piece moves)*

### pieces.py
- Holds piece classes and efficiently creates them through inheritance.
- Implements \_\_deepcopy\_\_ methods for easy saving/reverting game state
- Redefines +,-,*,/ operators for easy movement of piece. *To move a piece up 2 squares and to the right 1 square, simply do piece \* 2 + 1.* 

### engine.py
- Holds engine logic *(evaluate positions, count material, store tree of future possible moves)*
  
## Engine
*Currently partially implemented*

### Current Functionality
- Calculates eval based off piece value. *E.g. If white took black's knight the eval would be +3.0 as the knight is worth 3 points.*

### Future Implementation Plan
- Traverse the tree of future positions and run the engine's evaluation function on each position.
- Use minimax with alpha-beta pruning and iterative deepening to choose what the engine thinks is the best move.
- Use heuristics based on piece positions to tweak engine evaluation.
