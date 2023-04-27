Gomoku Game
---

Whoever align their five pieces first, **vertically, horizontally or diagonally, wins** the game.

# How to play the game
- Clone the repo, and change the directory to the repo.
- Install the dependencies (use virtualenv): `pip3 install -r requirements.txt`
- Run the main.py file: `python3 main.py`

# Game environment
- It consists of a board with **11 * 11 (121) positions** by default.
- Each player, turn by turn, place their piece (black or white) on the available places. 
- The player, who places their pieces **vertically, horizontally or diagonally first**, wins the game.

# Preparation of training data
- A training data contains two states of the board: before making the move and after making the move.
  - Before making the move means the current state of the board on which the player has to make the decision.
  - After making the move means the next state of the board after the player has made the move.
- Play the game yourself in which the opponent could be
  - Random player - who places their pieces randomly on the board
  - Myself - I play for both sides
  
# Neural Network

### 1. Convolutional Neural Network
  - The model detects the edges (points connecting where the pieces are placed) and generates the new edges as output.
  - Provide the training dataset where each data point is a tuple: (current_board_state, next_board_state).
    - current_board_state: 11*11 matrix with values -1, 0 and 1. 
      - 1 and -1 indicate the pieces placed by the two players.
      - 0 indicates the empty places.
    - next_board_state: 11*11 matrix with values -1, 0 and 1 (as explained above).
  - The model, when provided with the current_board_state, should predict the next_board_state.

### 2. Reinforcement Learning
    - Train the model by rewarding when the player is closer to winning and punishing when the player is closer to losing.
    

