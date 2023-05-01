import random

import numpy as np

CHECK_FOR_THREATS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


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
        max_threats = self.detect_threat_from_opponent(board, player)
        opponent_threat_levels = max_threats.keys()
        if len(opponent_threat_levels) > 0:
            max_threat_level = max(opponent_threat_levels)
            max_threat_level_pos = max_threats[max_threat_level][-1]
            if max_threat_level > 2:
                print("opponent threat levels: ", max_threats, max_threat_level_pos)
                return max_threat_level_pos

        # no threats by the opponent, we attack now
        # find the places where the player has placed
        # max sequential pieces and continue building on sequence
        imposed_threats = self.detect_threat_to_opponent(board, player)
        imposed_threat_levels = imposed_threats.keys()
        if len(imposed_threat_levels) > 0:
            max_imposed_threat_level = max(imposed_threat_levels)
            max_imposed_threat_pos = imposed_threats[max_imposed_threat_level][-1]
            print("imposed threat to opponent: ", imposed_threats, max_imposed_threat_pos)
            return max_imposed_threat_pos

        # No threats found, so choose a random move
        max_count = 121
        while True and max_count > 0:
            row = random.randint(0, self.board_length - 1)
            col = random.randint(0, self.board_width - 1)
            if board[row][col] == 0:
                return row, col
            max_count -= 1
        return -1, -1  # when nth is left

    # threats imposed by the opponent
    # check for every position in the board
    # for every position: check every direction
    def detect_threat_from_opponent(self, board, player):
        opponent = -player
        threat_positions = {}

        for i in range(self.board_length):
            for j in range(self.board_width):
                # if the player has piece at i,j position
                # check if that position's neighbor places are threatened
                # opponent is 1 move away from winning when placed opposite piece
                # at the neighbour places
                for di, dj in CHECK_FOR_THREATS:
                    # here di, dj represents direction from reference point i,j
                    # detect consecutive opponent in the neighbour positions from i,j
                    # x_pos, y_pos indicates
                    opponent_is_threat, x_pos, y_pos, threat_level = self.is_a_threat(board, i, j, di, dj, opponent)
                    if opponent_is_threat and x_pos is not None and y_pos is not None:
                        if threat_level in threat_positions and (x_pos, y_pos) not in threat_positions[threat_level]:
                            threat_positions[threat_level].append((x_pos, y_pos))
                        else:
                            threat_positions[threat_level] = [(x_pos, y_pos)]

        return threat_positions

    # Check if the opponent has a threat in the given direction.
    # i, j -- player's current piece
    # di, dj - neighbour places of player's current piece (direction from i,j)
    # opponent - value in the board for opponent's piece
    def is_a_threat(self, board, i, j, di, dj, player, max_k=5):
        n = self.board_length
        m = self.board_width

        # check if the next four positions in the given direction have the opponent's piece
        # if the board contains piece that does not belong to opponent (belongs to current player)
        # then there is no threat from the opponent
        opponent_pieces = []  # stores indices where opponent pieces are placed consecutively
        last_opponent_pos = ()
        last_detected_opponent_k = None
        for k in range(1, max_k):
            x = i + k * di
            y = j + k * dj
            # if invalid positions and no opponent pieces in the neighbour positions
            # if (x < 0 or x >= n or y < 0 or y >= m) and len(opponent_pieces) < 1:
            #     return False, None, None, None
            # if opponent exists at the neighboring position of the current player's piece (i,j)
            # di, dj is extended to 4 places
            # for example: di, dj = (0,5) then x is 0 and y ranges from (6,7,8,9)
            k_last_opponent_pos = len(last_opponent_pos) > 0 and len(opponent_pieces) > 0 and (
                    last_opponent_pos[0] == opponent_pieces[-1][0]) and (
                                          last_opponent_pos[1] == opponent_pieces[-1][1])
            if self.is_valid(x, y) and board[x][y] == player and (
                    len(last_opponent_pos) == 0 or len(opponent_pieces) == 0 or k_last_opponent_pos):
                opponent_pieces.append((x, y))
                last_opponent_pos = (x, y)
                last_detected_opponent_k = k

        # check if the opponent can win by placing a piece at the end of the threat
        x = i + max_k * di
        y = j + max_k * dj
        if 0 <= x < n and m > y >= 0 == board[x][y]:
            board[x][y] = player
            if self.is_win(board, x, y, player):
                board[x][y] = 0
                return True, x, y, 5
            board[x][y] = 0

        # if no max level threat by the opponent,
        # return if lower level threats for position i,j
        # in the direction di, dj
        # level (1,2,3,4) -> consecutive opponent pieces
        # in given the direction from i,j
        if opponent_pieces and last_detected_opponent_k is not None:
            x = i + ((last_detected_opponent_k + 1) * di)
            y = j + ((last_detected_opponent_k + 1) * dj)
            if self.is_valid(x, y) and board[x][y] == 0:
                print("reference: ", i, j)
                print("longest player sequence: player: ", player, "\nplaced_pieces: ", opponent_pieces)
                return True, x, y, len(opponent_pieces)
        return False, None, None, None

    # imposing threat to the opponent
    # check for every position where the player has placed the piece
    # for every placed piece position: check every direction
    def detect_threat_to_opponent(self, board, player):
        imposed_threat_positions = {}

        for i in range(self.board_length):
            for j in range(self.board_width):
                # if the player has piece at i,j position
                # check if that position's neighbor places threaten the opponent
                # i.e. if the player is crowded around this position
                # find the neighbour where the max sequence is made
                if board[i][j] == player:
                    for di, dj in CHECK_FOR_THREATS:
                        # here di, dj represents direction from reference point i,j
                        # detect consecutive player's piece in the neighbour positions from i,j
                        # x_pos, y_pos indicates the next safe position for the player
                        # that maximizes the player's chances of winning
                        is_imposed_threat, x_pos, y_pos, imposed_threat_level = self.is_a_threat(board, i, j, di, dj,
                                                                                                 player)
                        if is_imposed_threat and x_pos is not None and y_pos is not None:
                            if imposed_threat_level in imposed_threat_positions:
                                imposed_threat_positions[imposed_threat_level].append((x_pos, y_pos))
                            else:
                                imposed_threat_positions[imposed_threat_level] = [(x_pos, y_pos)]
        return imposed_threat_positions

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
