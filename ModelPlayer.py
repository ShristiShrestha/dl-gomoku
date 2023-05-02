import numpy as np
import tensorflow as tf


class ModelPlayer:
    def __init__(self, model_path, _id, _gui):
        self.model_path = model_path
        self.model = None
        self.id = _id
        self.gui = _gui

        self.load_model()

    def load_model(self):
        self.model = tf.keras.models.load_model(self.model_path)

    def predict(self, input_board):
        model = self.model
        board = input_board.reshape(11, 11, 2)
        output_board = model.predict(np.array([board]))
        return output_board

    def get_move(self, _board, _player):
        model_output = self.predict(_board)[0]
        sorted_index = np.argsort(model_output, kind='quicksort')[::-1]
        board = _board[0] - _board[1]
        count = 0
        while count < len(sorted_index):
            max_index = sorted_index[count]
            row_index = max_index // 11  # 11 is the square root of 121, the size of the output vector
            col_index = max_index % 11
            board_pos_val = board[row_index][col_index]
            if board_pos_val == 0:
                return row_index, col_index
            count += 1
        return -1, -1
