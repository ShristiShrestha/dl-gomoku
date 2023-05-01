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
        output_board = model.predict(input_board)
        return output_board

    def get_move(self, _board, _player):
        board = _board[0] - _board[1]
        model_output = self.predict(board)
        max_index = np.argmax(model_output)
        row_index = max_index // 11  # 11 is the square root of 121, the size of the output vector
        col_index = max_index % 11
        return row_index, col_index
