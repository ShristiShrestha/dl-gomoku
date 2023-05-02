import numpy as np, requests, h5py, os
import tensorflow as tf
from tensorflow.keras.callbacks import ReduceLROnPlateau


class MyPlayer:
    def __init__(self, _id, _model_path=None):
        self.dir_files = None
        self.history = None
        self.train_X = None
        self.train_Y = None
        self.train_Y_moves = None
        self.cnn_model = None  # create model (untrained)
        # load trained model from remote location
        self.trained_model_path = "https://lsumail2-my.sharepoint.com/:u:/g/personal/sshre35_lsu_edu/EX5Dq0UPv-VNvzGFfqxbwmQBXgXQfjQ1YqnvHCpthtnMDQ?download=1"
        self.model_path = _model_path  # load trained model from local dir
        self.model = None  # keras model loaded from local dir or remote location
        self.id = _id  # player id assigned by the game
        self.board_size = 11  # board size default to 11
        # load model from local dir or remote dir
        self.load_model()

    def load_npy_filenames(self, _folder):
        _dir = os.getcwd()
        files = os.listdir(os.path.join(_dir, _folder))
        print("training data files: ", len(files), files[0])
        # 0 index is basically empty board initialization
        # return an array of board data from each file
        self.dir_files = [os.path.join(_dir, _folder, filename) for filename in files if ".npy" in filename]

    @staticmethod
    def separate_train_x_y(_data, _dir):
        # index 0 is basically all-zeros board
        index = 1
        train_x = None
        train_y = None
        data_size = len(_data)
        if data_size >= 3:  # and index < (data_size - 1)
            train_x = np.array(_data[index:data_size - 1])
            train_y = np.array(_data[index + 1:])
        if len(train_x) != len(train_y):
            print("diff train x: ", train_x.shape, "\t train y: ", train_y.shape)
        return train_x, train_y

    @staticmethod
    def get_new_move_pos(_current_state, _next_state, show_log=False):
        # Compare the two board states element-wise
        is_different = not np.array_equal(_current_state, _next_state)

        if is_different:
            # Find the position where the state has changed
            changed_pos = np.where(_next_state != _current_state)
            pos_x, pos_y = changed_pos[0][0], changed_pos[1][0]
            if show_log:
                print("changed position: ", pos_x, pos_y)
                print(changed_pos)
                print(_current_state[pos_x])
                print(_next_state[pos_x])

            # changed pos tuple: (array([10]), array([8]), array([0]))
            return pos_x, pos_y

        return -1, -1

    def prepare_dataset(self, _dir):
        self.load_npy_filenames(_dir)
        training_current_states = np.empty((0, 2, self.board_size, self.board_size))
        training_next_states = np.empty((0, 2, self.board_size, self.board_size))
        for file in self.dir_files:
            data = np.load(file)
            train_x, train_y = self.separate_train_x_y(data, _dir)
            training_current_states = np.append(training_current_states, train_x, axis=0)
            training_next_states = np.append(training_next_states, train_y, axis=0)

        X = training_current_states.reshape((len(training_current_states), 11, 11, 2))
        Y = training_next_states.reshape((len(training_next_states), 11, 11, 2))

        self.train_Y_moves = np.zeros((Y.shape[0], 121))
        for i in range(len(X)):
            x = X[i]
            y = Y[i]
            pos_x, pos_y = self.get_new_move_pos(x, y)
            valid_pos_vals = pos_x != -1 and pos_y != -1
            valid_pos = pos_x * 11 + pos_y
            self.train_Y_moves[i][valid_pos] = 1 if valid_pos_vals else 0
        self.train_X = training_current_states

    def load_model(self):
        if self.trained_model_path is None:
            self.model = tf.keras.models.load_model(self.model_path)
        else:
            self.model = self.load_trained_model()

    def load_trained_model(self):
        _filename = self.trained_model_path
        print("loading trained model from ", _filename)
        tmp_file_name = "shristi_gomoku_model.h5"
        response = requests.get(_filename)
        response.raise_for_status()
        with open(tmp_file_name, 'wb') as f:
            f.write(response.content)

        # load model from a saved model file and return the model
        # Load the model from the saved .h5 file
        model_file = h5py.File(os.path.join(os.getcwd(), tmp_file_name), 'r')
        model = tf.keras.models.load_model(model_file)
        return model

    def create_model(self):
        input_shape = (self.board_size, self.board_size, 2)
        output_shape = self.board_size * self.board_size
        cnn_model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same', input_shape=input_shape),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(output_shape, activation='softmax')
        ])
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
        cnn_model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
        self.cnn_model = cnn_model

    # whenever validation loss stops improving in n consecutive epochs,
    # it reduces the learning rate by lr
    # the learning rate can be reduced to min_lr at best
    @staticmethod
    def get_lr(lr_factor=0.01, consecutive_epochs=3, min_lr=0.000000000000001):
        return ReduceLROnPlateau(monitor='val_loss', factor=lr_factor, patience=consecutive_epochs, min_lr=min_lr,
                                 mode='min')

    def train_model(self):
        if self.cnn_model is not None and self.train_X and self.train_Y_moves:
            lr_callback = self.get_lr()
            self.history = self.cnn_model.fit(self.train_X, self.train_Y_moves,
                                              epochs=50, batch_size=64, verbose=1,
                                              validation_split=0.2,
                                              callbacks=[lr_callback])

    def predict(self, input_board):
        model = self.model
        board = input_board.reshape(self.board_size, self.board_size, 2)
        output_board = model.predict(np.array([board]))
        return output_board

    def get_move(self, _board, _player):
        model_output = self.predict(_board)[0]
        sorted_index = np.argsort(model_output, kind='quicksort')[::-1]
        board = _board[0] - _board[1]
        count = 0
        while count < len(sorted_index):
            max_index = sorted_index[count]
            row_index = max_index // self.board_size
            col_index = max_index % self.board_size
            board_pos_val = board[row_index][col_index]
            if board_pos_val == 0:
                return row_index, col_index
            count += 1
        return -1, -1
