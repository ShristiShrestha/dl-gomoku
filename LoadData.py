from GlobalVars import PLAY_WITH_MYSELF, BOARD_SIZE
import numpy as np, os


class LoadData:

    def __init__(self, _dir, _board_size):
        self.dir = _dir
        self.board_size = _board_size
        self.dir_files = []

    # @param data: one game data
    # of size (turns, 2, BOARD_SIZE, BOARD_SIZE)
    #  turns max value is 121
    @staticmethod
    def separate_train_x_y(_data, _dir):
        # index 0 is basically all-zeros board
        index = 1
        train_x = []
        train_y = []
        offset_inc = 1

        # when you played with random player, only consider your moves
        # index 0: initial zeros all board values
        # index 1: board state after the first player (random) make the move
        # index 2: board state after the second player (me) make the move

        while len(_data) >= 3 and index < (len(_data) - 1):
            train_x.append(_data[index])
            train_y.append(_data[index + offset_inc])
            index += offset_inc

        return np.array(train_x), np.array(train_y)

    # @returns an array of .npy files
    def load_npy_filenames(self):
        _dir = os.getcwd()
        _folder = self.dir
        files = os.listdir(os.path.join(_dir, _folder))
        print("training data files: ", len(files), files[0])
        # print sample test file
        test_file = os.path.join(_dir, _folder, files[0])
        print("load training data sample from file: ", test_file)
        board_states = np.load(test_file)
        print(board_states[0], board_states.shape)
        # return an array of board data from each file
        self.dir_files = [os.path.join(_dir, _folder, filename) for filename in files]

    def load_data(self):
        _folder = self.dir
        self.load_npy_filenames()
        # batch size, 2, BOARD_SIZE, BOARD_SIZE
        # each state consists of 2 arrays (each array of size BOARD_SIZE*BOARD_SIZE)
        # here each array basically represents the board state
        # from the perspective of the corresponding player
        # 0 means either opposite or empty
        # 1 means that player's piece placed at that position
        training_current_states = np.empty((0, 2, BOARD_SIZE, BOARD_SIZE))
        training_next_states = np.empty((0, 2, BOARD_SIZE, BOARD_SIZE))
        for file in self.dir_files:
            # (turns, 2, BOARD_SIZE, BOARD_SIZE) turns max value is 121
            data = np.load(file)
            train_x, train_y = self.separate_train_x_y(data, _folder)
            training_current_states = np.append(training_current_states, train_x, axis=0)
            training_next_states = np.append(training_next_states, train_y, axis=0)
        print("training current states: ", training_current_states.shape)
        print("training next states: ", training_next_states.shape)
        return training_current_states, training_next_states
