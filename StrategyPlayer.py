import random

CHECK_FOR_THREATS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1)]


class StrategyPlayer:
    def __init__(self, _id, gui=None):
        self.id = _id
        self.gui = gui

    # a threat is potential win for the current player
    # and a loss for the opposite player
    def get_move(self, _board, player):
        print("get move strategy player: ", player)

        board = _board[0] - _board[1]

        # Check if a winning move is available
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    board[i][j] = player
                    if self.is_win(board, i, j, player):
                        return i, j
                    board[i][j] = 0

        #  Check if the opponent is threatening to win
        max_opponent_threat_level, max_threat_positions = self.detect_opponent_threat(board, player)
        if max_opponent_threat_level > 0 and len(max_threat_positions) > 0:
            print("max opponent threat level", max_opponent_threat_level, max_threat_positions[0])
            return max_threat_positions[0]  # tuple (x, y) empty position if filled by opponent (opponent wins)

        # no threats by the opponent, we attack now
        # Check for double threats to the opponent
        for i in range(len(board)):
            for j in range(len(board[0])):
                # if the place is empty
                # place the piece and check
                # whether this move imposes any threat
                # to the opponent
                if board[i][j] == 0:
                    board[i][j] = player
                    if self.is_double_threat(board, player):
                        return i, j
                    else:
                        board[i][j] = 0

        # Check for single threats to the opponent
        for i in range(len(board)):
            for j in range(len(board[0])):
                # if the place is empty
                # place the piece and check
                # whether this move imposes any threat
                # to the opponent
                if board[i][j] == 0:
                    board[i][j] = player
                    if self.is_single_threat(board, player):
                        return i, j
                    else:
                        board[i][j] = 0

        # No threats found, so choose a random move
        max_count = 121
        while True and max_count > 0:
            row = random.randint(0, len(board) - 1)
            col = random.randint(0, len(board[0]) - 1)
            if board[row][col] == 0:
                return row, col
            max_count -= 1
        return -1, -1  # when nth is left

    def is_single_threat(self, board, player):
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == player:
                    for di, dj in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                        if self.detect_threat_to_opponent(board, i, j, di, dj, player):
                            print("imposes single threat: ", i, j, di, dj, player)
                            return True
        return False

    def is_double_threat(self, board, player):
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == player:
                    for di1, dj1 in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                        for di2, dj2 in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                            if (di1, dj1) != (di2, dj2) and self.detect_threat_to_opponent(board, i, j, di1, dj1,
                                                                                           player) \
                                    and self.detect_threat_to_opponent(board, i, j, di2, dj2, player):
                                print("imposes double threat: ", i, j, di1, dj1, player)
                                return True
        return False

    # checked: threats imposed by the opponent
    def detect_opponent_threat(self, board, player):
        opponent = -player
        max_opponent_threat_level = 0
        max_threat_positions = []

        for i in range(len(board)):
            for j in range(len(board[0])):
                # check if the player with piece at i, j
                # is threatened by the opponent (opponent is 1 move away from winning)
                if board[i][j] == player:
                    for di, dj in CHECK_FOR_THREATS:
                        opponent_is_threat, x_pos, y_pos = self.is_opponent_threat(board, i, j, di, dj, opponent)
                        if opponent_is_threat and x_pos is not None and y_pos is not None:
                            max_opponent_threat_level += 1
                            max_threat_positions.append((x_pos, y_pos))

        return max_opponent_threat_level, max_threat_positions

    # imposing threat on the opponent
    def detect_threat_to_opponent(self, board, i, j, di, dj, player):
        n = len(board)
        count = 0
        for k in range(1, 4):
            x = i + k * di
            y = j + k * dj
            # If we encounter an opponent stone or go out of bounds, stop checking
            if x < 0 or x >= n or y < 0 or y >= n or board[x][y] == -player:
                return False
            elif board[x][y] == player:
                count += 1
            elif board[x][y] == 0:
                offset_clear = (len(board) > (x - di) >= 0) and (len(board) > (x + di) >= 0) and (
                        len(board) > (y - dj) >= 0) and (len(board) > (y + dj) >= 0)

                # If we encounter an empty space, check if there are no more than two empty spaces in a row
                if offset_clear and 0 == board[x + di][y + dj] == board[x - di][y - dj]:
                    return False
            else:
                # This should not happen, but just in case...
                raise ValueError("Invalid board value: {}".format(board[x][y]))
        return count == 3

    # Check if the opponent has a threat in the given direction.
    def is_opponent_threat(self, board, i, j, di, dj, opponent):
        n = len(board)
        m = len(board[0])

        # check if the next four positions in the given direction have the opponent's piece
        # if the board contains piece that does not belong to opponent (belongs to current player)
        opponent_pieces = 0
        for k in range(1, 5):
            x = i + k * di
            y = j + k * dj
            if x < 0 or x >= n or y < 0 or y >= m or board[x][y] != opponent:
                return False, None, None

        # check if the opponent can win by placing a piece at the end of the threat
        x = i + 5 * di
        y = j + 5 * dj
        if 0 <= x < n and m > y >= 0 == board[x][y]:
            board[x][y] = opponent
            if self.is_win(board, x, y, opponent):
                board[x][y] = 0
                return True, x, y
            board[x][y] = 0

        return False, None, None

    def is_win(self, board, i, j, player):
        count = 0
        board_size = len(board)

        # Check horizontal line
        for k in range(max(0, j - 4), min(board_size, j + 5)):
            if board[i][k] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

        # Check vertical line
        count = 0
        for k in range(max(0, i - 4), min(board_size, i + 5)):
            if board[k][j] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

        # Check diagonal line (bottom-left to top-right)
        count = 0
        for k in range(-4, 5):
            x, y = i + k, j + k
            if x < 0 or x >= board_size or y < 0 or y >= board_size:
                continue
            if board[x][y] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

        # Check diagonal line (top-left to bottom-right)
        count = 0
        for k in range(-4, 5):
            x, y = i + k, j - k
            if x < 0 or x >= board_size or y < 0 or y >= board_size:
                continue
            if board[x][y] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

        # No winning line found
        return False

    def is_valid_move(self, board, x, y):
        board_len = len(board)
        if board_len > x >= 0 and board_len > y >= 0:
            return True
        return False

    # Returns the level of threat to the player when placed item on i, j on the board.
    def get_threat_level(self, board, i, j, player):
        opponent = -player
        threat_level = 0
        for di, dj in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            if self.is_opponent_threat(board, i, j, di, dj, opponent):
                threat_level += 2
            elif self.is_opponent_threat(board, i, j, di, dj, opponent):
                threat_level += 1
        return threat_level
