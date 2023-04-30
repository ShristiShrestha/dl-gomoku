import random

import numpy as np

CHECK_FOR_THREATS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1)]


class StrategyPlayer:
    def __init__(self, _id, gui=None, _board=None):
        self.id = _id
        self.gui = gui

        if _board is not None:
            board = _board[0] - _board[1]
            self.board_width = len(board[0])
            self.board_length = len(board)

    # a threat is potential win for the current player
    # and a loss for the opposite player
    def get_move(self, _board, player):
        print("get move strategy player: ", player)

        board = _board[0] - _board[1]

        # Check if a winning move is available
        for i in range(self.board_length):
            for j in range(self.board_width):
                if board[i][j] == 0:
                    board[i][j] = player
                    if self.is_win(board, i, j, player):
                        print("found winning position for player: ", i, j, player)
                        return i, j
                    board[i][j] = 0

        #  Check if the opponent is threatening to win
        max_threats = self.detect_opponent_threat_from_opponent(board, player)
        opponent_threat_levels = max_threats.keys()
        if len(opponent_threat_levels) > 0:
            max_threat_level = max(opponent_threat_levels)
            max_threat_level_pos = max_threats[max_threat_level][0]
            print("opponent threat levels: ", max_threats, max_threat_level_pos)

            return max_threat_level_pos  # tuple (x, y) empty position if filled by opponent (opponent wins)

        # no threats by the opponent, we attack now
        # Check for double threats to the opponent
        for i in range(self.board_length):
            for j in range(self.board_width):
                # if the place is empty
                # place the piece and check
                # whether this move imposes any threat
                # to the opponent
                if board[i][j] == 0:
                    board[i][j] = player
                    if self.impose_double_threat_to_opponent(board, player):
                        return i, j
                    else:
                        board[i][j] = 0

        # Check for single threats to the opponent
        for i in range(self.board_length):
            for j in range(self.board_width):
                # if the place is empty
                # place the piece and check
                # whether this move imposes any threat
                # to the opponent
                if board[i][j] == 0:
                    board[i][j] = player
                    if self.impose_single_threat_to_opponent(board, player):
                        return i, j
                    else:
                        board[i][j] = 0

        # No threats found, so choose a random move
        max_count = 121
        while True and max_count > 0:
            row = random.randint(0, self.board_length - 1)
            col = random.randint(0, self.board_width - 1)
            if board[row][col] == 0:
                return row, col
            max_count -= 1
        return -1, -1  # when nth is left

    def impose_single_threat_to_opponent(self, board, player):
        for i in range(self.board_length):
            for j in range(self.board_width):
                if board[i][j] == player:
                    for di, dj in CHECK_FOR_THREATS:
                        if self.detect_threat_to_opponent(board, i, j, di, dj, player):
                            print("imposes single threat: ", i, j, di, dj, player)
                            return True
        return False

    def impose_double_threat_to_opponent(self, board, player):
        for i in range(self.board_length):
            for j in range(self.board_width):
                if board[i][j] == player:
                    for di1, dj1 in CHECK_FOR_THREATS:
                        for di2, dj2 in CHECK_FOR_THREATS:
                            if (di1, dj1) != (di2, dj2) and self.detect_threat_to_opponent(board, i, j, di1, dj1,
                                                                                           player) \
                                    and self.detect_threat_to_opponent(board, i, j, di2, dj2, player):
                                print("imposes double threat: ", i, j, di1, dj1, player)
                                return True
        return False

    # checked: threats imposed by the opponent
    def detect_opponent_threat_from_opponent(self, board, player):
        opponent = -player
        max_threat_positions = {}

        for i in range(self.board_length):
            for j in range(self.board_width):
                # if the player has piece at i,j position
                # check if that position's neighbor places are threatened
                # opponent is 1 move away from winning when placed opposite piece
                # at the neighbour places
                if board[i][j] == player:
                    for di, dj in CHECK_FOR_THREATS:
                        # here di, dj represents direction from reference point i,j
                        # detect consecutive opponent in the neighbour positions from i,j
                        # x_pos, y_pos indicates
                        opponent_is_threat, x_pos, y_pos, threat_level = self.is_opponent_threat(board, i, j, di, dj,
                                                                                                 opponent)
                        if opponent_is_threat and x_pos is not None and y_pos is not None:
                            if threat_level in max_threat_positions:
                                max_threat_positions[threat_level].append((x_pos, y_pos))
                            else:
                                max_threat_positions[threat_level] = [(x_pos, y_pos)]

        return max_threat_positions

    # imposing threat on the opponent
    def detect_threat_to_opponent(self, board, i, j, di, dj, player):
        n = self.board_length
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
                offset_clear = (self.board_length > (x - di) >= 0) and (self.board_length > (x + di) >= 0) and (
                        self.board_length > (y - dj) >= 0) and (self.board_length > (y + dj) >= 0)

                # If we encounter an empty space, check if there are no more than two empty spaces in a row
                if offset_clear and 0 == board[x + di][y + dj] == board[x - di][y - dj]:
                    return False
            else:
                # This should not happen, but just in case...
                raise ValueError("Invalid board value: {}".format(board[x][y]))
        return count == 3

    # Check if the opponent has a threat in the given direction.
    # i, j -- player's current piece
    # di, dj - neighbour places of player's current piece (direction from i,j)
    # opponent - value in the board for opponent's piece
    def is_opponent_threat(self, board, i, j, di, dj, opponent):
        n = self.board_length
        m = self.board_width

        # check if the next four positions in the given direction have the opponent's piece
        # if the board contains piece that does not belong to opponent (belongs to current player)
        # then there is no threat from the opponent
        opponent_pieces = []  # stores indices where opponent pieces are placed consecutively
        last_opponent_pos = ()
        last_detected_opponent_k = None
        for k in range(1, 5):
            x = i + k * di
            y = j + k * dj
            # if invalid positions and no opponent pieces in the neighbour positions
            # if (x < 0 or x >= n or y < 0 or y >= m) and len(opponent_pieces) < 1:
            #     return False, None, None, None
            # if opponent exists at the neighboring position of the current player's piece (i,j)
            # di, dj is extended to 4 places
            # for example: di, dj = (0,5) then x is 0 and y ranges from (6,7,8,9)
            k_last_opponent_pos = last_opponent_pos and opponent_pieces and (
                    last_opponent_pos[0] == opponent_pieces[-1][0]) and (
                                          last_opponent_pos[1] == opponent_pieces[-1][1])
            if self.is_valid(x, y) and board[x][y] == opponent and (
                    len(last_opponent_pos) == 0 or len(opponent_pieces) == 0 or k_last_opponent_pos):
                opponent_pieces.append((x, y))
                last_opponent_pos = (x, y)
                last_detected_opponent_k = k

        # check if the opponent can win by placing a piece at the end of the threat
        x = i + 5 * di
        y = j + 5 * dj
        if 0 <= x < n and m > y >= 0 == board[x][y]:
            board[x][y] = opponent
            if self.is_win(board, x, y, opponent):
                board[x][y] = 0
                return True, x, y, 5  # max level
            board[x][y] = 0

        # if no max level threat by the opponent,
        # return if lower level threats for position i,j
        # in the direction di, dj
        # level (1,2,3,4) -> consecutive opponent pieces
        # in given the direction from i,j
        if opponent_pieces and last_detected_opponent_k is not None:
            x = i + (last_detected_opponent_k + 1) * di
            y = j + (last_detected_opponent_k + 1) * dj
            if self.is_valid(x, y) and board[x][y] == 0:
                return True, x, y, len(opponent_pieces)
        return False, None, None, None

    def is_win(self, board, i, j, player):
        count = 0
        board_size = self.board_length

        # Check vertical line
        for k in range(max(0, j - 4), min(board_size, j + 5)):
            if board[i][k] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

        # Check horizontal line
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

    def is_valid(self, x, y):
        return (0 <= x < self.board_width) and (0 <= y < self.board_length)
