# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time

import numpy as np

from StrategyPlayer import StrategyPlayer
from gamegui import GameGUI, GUIPlayer  # do not import gamegui if you don't have pygame or not on local machine.

BOARD_SIZE = 11
PLAY_WITH_RANDOM = "training data/channels/random/"
PLAY_WITH_MYSELF = "training data/channels/myself/"
PLAY_WITH_STRATEGY = "training data/channels/strategy/"


def check_winner(L):
    N = len(L)
    if N < 5:
        return False
    else:
        s = np.sum(L[:5])
        if s == 5:
            return True
        if N > 5:
            for i in range(N - 5):
                s = s - L[i] + L[i + 5]
                if s == 5:
                    return True
        return False


class Board:
    def __init__(self, sz):
        self.sz = sz
        # per player board state: 3D (2, board size, board size)
        self.pbs = np.zeros((2, sz, sz), dtype=int)

    def add_move(self, p, x, y):
        self.pbs[p, x, y] = 1

        xd, xu = min(x, 4), min(self.sz - 1 - x, 4)
        yl, yr = min(y, 4), min(self.sz - 1 - y, 4)
        fs0, fs1 = min(xd, yl), min(xu, yr)
        bs0, bs1 = min(xu, yl), min(xd, yr)

        if check_winner(self.pbs[p, (x - xd):(x + xu + 1), y]) or check_winner(self.pbs[p, x, (y - yl):(y + yr + 1)]):
            return True
        elif check_winner(self.pbs[p, np.arange((x - fs0), (x + fs1 + 1)), np.arange((y - fs0), (y + fs1 + 1))]):
            return True
        elif check_winner(self.pbs[p, np.arange((x + bs0), (x - bs1 - 1), -1), np.arange((y - bs0), (y + bs1 + 1))]):
            return True
        else:
            return False


class Gomoku:
    def __init__(self, board_sz=11, gui=False):
        self.board_sz = board_sz
        self.board = Board(board_sz)
        self.number = np.zeros((board_sz, board_sz), dtype=int)
        self.k = 1  # step number
        self.result = 0
        self.states = np.zeros((board_sz * board_sz, 2, board_sz, board_sz))
        self.state_counter = 0
        print("----initializing zeros states: ", self.states.shape, "--------")
        if gui:
            self.gui = GameGUI(board_sz)
        else:
            self.gui = None

    def reset(self):
        self.board.pbs.fill(0)
        self.number.fill(0)
        self.k = 1
        self.result = 0

    def copy(self):  # copy the game, not the UI
        g = Gomoku(self.board_sz)
        g.board.pbs = np.copy(self.board.pbs)
        g.number = np.copy(self.number)
        g.k = self.k
        g.result = self.result
        return g

    def draw(self):
        print("---- drawing board --------")
        # 11 by 11 where
        # -1 is player 2, (black)
        # 1 is player 1 (white)
        # 0 is empty place
        if self.state_counter < (self.board_sz * self.board_sz):
            # current_board = self.board.pbs[0, :, :] - self.board.pbs[1, :, :]
            self.states[self.state_counter] = np.array([self.board.pbs[0, :, :], self.board.pbs[1, :, :]])
            self.state_counter += 1
            print("Adding current board at ", self.state_counter - 1, "\n", self.states[self.state_counter-1])
        if self.gui:
            self.gui._draw_background()
            self.gui._draw_chessman(self.board.pbs[0, :, :] - self.board.pbs[1, :, :], self.number)

    # execute a move
    def execute_move(self, p, x, y):
        nobody_made_move = np.sum(self.board.pbs[:, x, y]) == 0
        if nobody_made_move is False:
            print("blunder is picking x y:\n p: ", self.board.pbs[p, x, y], "\nall board value at xy",
                  self.board.pbs[:, x, y], "\nnobody made moves: ", nobody_made_move)
        assert nobody_made_move

        win = self.board.add_move(p, x, y)
        self.number[x][y] = self.k
        self.k += 1
        return win

    # main loop
    def play(self, p1, p2, output_dir=PLAY_WITH_MYSELF, sleep=1):
        players = {0: p1, 1: p2}
        pi = 0
        self.draw()
        while True:
            player_value = 1 if pi == 0 else -1
            x, y = players[pi].get_move(self.board.pbs, player_value)
            if x < 0:
                print("player ", pi, player_value, " returning invalid position: ", x, y)
                break
            win = self.execute_move(pi, x, y)
            self.draw()
            time.sleep(sleep)

            if win:
                self.result = 1 - 2 * pi
                now = datetime.datetime.now()
                rand = np.random.choice(100000)
                filename = output_dir + "board_" + str(rand) + now.strftime("%m_%d_%Y_%H_%M_%S") + ".npy"
                print("-----won-----", pi, "\n----state counter: ", self.state_counter,
                      "\n----saving to file ", filename)
                np.save(filename, self.states[:self.state_counter])
                break
            if np.sum(self.board.pbs) == self.board_sz * self.board_sz:
                break

            pi = (pi + 1) % 2
            time.sleep(sleep)


class RandomPlayer:
    def __init__(self, id):
        self.id = id

    def get_move(self, board, player):
        print("get move random player: ", player)
        b = (board[0, :, :] + board[1, :, :]) - 1
        ix, jx = np.nonzero(b)
        idx = [i for i in zip(ix, jx)]
        return idx[np.random.choice(len(idx))]


def load_sample_game_data(_folder=PLAY_WITH_RANDOM):
    _dir = os.getcwd()
    files = os.listdir(os.path.join(_dir, _folder))
    print("training data files: ", files)
    # print sample test file
    test_file = os.path.join(_dir, _folder, files[0])
    print("load training data sample from file: ", test_file)
    board_states = np.load(test_file)
    print(board_states[0], board_states.shape)
    return [os.path.join(_dir, _folder, filename) for filename in files]


def separate_train_x_y(_data, _dir):
    index = 1
    train_x = []
    train_y = []
    offset_inc = 1 if _dir == PLAY_WITH_MYSELF else 2

    # when both players are me, then consider the moves and
    # current state for both player

    # when played with random player, only consider your moves
    # index 0: initial zeros all board values
    # index 1: board state after the first player (random) make the move
    # index 2: board state after the second player (me) make the move

    while len(_data) >= 3 and index < (len(_data) - 1):
        train_x.append(_data[index])
        train_y.append(_data[index + offset_inc])
        index += offset_inc

    return np.array(train_x), np.array(train_y)


def load_data(_folder=PLAY_WITH_MYSELF):
    files = load_sample_game_data(_folder)
    # batch size, BOARD_SIZE, BOARD_SIZE
    training_current_states = np.empty((0, BOARD_SIZE, BOARD_SIZE))
    training_next_states = np.empty((0, BOARD_SIZE, BOARD_SIZE))
    for file in files:
        data = np.load(file)  # (sum_play_count, BOARD_SIZE, BOARD_SIZE)
        train_x, train_y = separate_train_x_y(data, _folder)
        training_current_states = np.append(training_current_states, train_x, axis=0)
        training_next_states = np.append(training_next_states, train_y, axis=0)
    print("training current states: ", training_current_states.shape)
    print("training next states: ", training_next_states.shape)
    return training_current_states, training_next_states


def play_both_gui():
    max_games = 1000
    while max_games > 0:
        g = Gomoku(11, True)
        p1 = StrategyPlayer(0, g.gui, g.board.pbs)  # GUIPlayer(0, g.gui)
        p2 = StrategyPlayer(1, g.gui, g.board.pbs)
        g.play(p1, p2, PLAY_WITH_STRATEGY, 0)
        g.gui.draw_result(g.result)
        max_games -= 1
        g.gui.wait_to_exit(force_quit=True)


def play_cmd():
    if len(sys.argv) > 1:
        # A user plays game with a random player
        g = Gomoku(11, True)

        p1 = RandomPlayer(0)
        p2 = GUIPlayer(1, g.gui)
        print('start GUI game, close window to exit.')
        g.play(p1, p2)

        g.gui.draw_result(g.result)
        g.gui.wait_to_exit()

    else:
        # Two random player play 100 rounds of non-GUI game
        g = Gomoku()
        p1 = RandomPlayer(0)
        p2 = RandomPlayer(1)
        for i in range(1000):
            g.play(p1, p2)
            print(i, g.result)
            g.reset()


if __name__ == "__main__":
    play_both_gui()
    # play_cmd()
