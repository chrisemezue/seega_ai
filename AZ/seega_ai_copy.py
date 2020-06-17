from player import Player
from sys import maxsize
# from board import Board
from seega_agent import SeegaAgent
from experience_collector import Experience_Collector
from keras import models
from keras.models import load_model
import random
import importlib
import numpy as np
import h5py
import importlib
from keras import Sequential
from keras import layers
from keras.layers import Dense
from encode_board import SeegaEncoder_Board
import os.path
from dlgo import kerasutil
import pickle
class IA(Player):
    # Team modify this
    name = "SeegaAI"

    def __init__(self, position, gameSize):
        Player.__init__(self, position, gameSize)
        self.encoder = self.get_encoder_by_name('SeegaEncoder_Board',gameSize)
        self.model = load_model('seega_model.h5')
        self.num_encoded_layers = 4
        self.row = gameSize
        self.col = gameSize
        self.player_to_color = {1: 'black', -1: 'white'}
        self.color_to_player = {'black': 1, 'white': -1}

        agent_dir = 'agent/default_agent/agent_8.hdf5'

        '''
        # Create the game agents
        if os.path.exists(black_agent_dir) != True or os.path.exists(white_agent_dir) != True:
            self.encoder = SeegaEncoder_Board(gameSize)
            input_shape = (self.encoder.board_height(), self.encoder.board_width(), self.encoder.layers_encode)
            model = Sequential()
            model.add(layers.Conv2D(100, (2, 2), padding='same', data_format="channels_last", input_shape=input_shape))
            # model.add(BatchNormalization())
            # model.add(layers.MaxPooling2D((2, 2)))
            # model.add(layers.Conv2D(100, (2, 2), padding='same', activation='relu'))
            # model.add(layers.MaxPooling2D((1, )))
            model.add(layers.Conv2D(128, (2, 2), padding='same', activation='relu'))
            # model.add(BatchNormalization())
            # model.add(layers.MaxPooling2D((2, 2)))
            model.add(layers.Conv2D(256, (2, 2), activation='relu'))
            model.add(layers.Conv2D(512, (2, 2), activation='relu'))
            # model.add(BatchNormalization())
            # model.add(layers.MaxPooling2D((2, 2)))
            model.add(layers.Flatten())
            # model.add(layers.Dropout(0.5))
            # model.add(layers.Dense(100, activation='relu'))
            # model.add(BatchNormalization())
            # model.add(layers.Dropout(0.2))
            model.add(layers.Dense(self.encoder.num_moves(), activation='sigmoid'))
            model.add(layers.Dense(self.encoder.num_moves(), activation='softmax'))

            self.agent_white = SeegaAgent(model, self.encoder)
            self.agent_black = SeegaAgent(model, self.encoder)
            # Save agent players
            self.agent_white.serialize(white_agent_dir)
            self.agent_black.serialize(black_agent_dir)
        else:
            self.agent_white = self.load_policy_agent(h5file_dir=white_agent_dir)
            self.agent_black = self.load_policy_agent(h5file_dir=black_agent_dir)

        '''

        self.collector_white = Experience_Collector()
        self.collector_black = Experience_Collector()

        self.agent_white = self.load_policy_agent(h5file_dir=agent_dir)
        self.agent_black = self.load_policy_agent(h5file_dir=agent_dir)

        self.agent_black.set_collector(self.collector_black)
        self.agent_white.set_collector(self.collector_white)





    def load_agent(self,white_agent_dir,black_agent_dir):
        print("---USING NEW MODEL----")
        self.agent_white = self.load_policy_agent(h5file_dir=white_agent_dir)
        self.agent_black = self.load_policy_agent(h5file_dir=black_agent_dir)

        self.collector_white = Experience_Collector()
        self.collector_black = Experience_Collector()

        self.agent_black.set_collector(self.collector_black)
        self.agent_white.set_collector(self.collector_white)


    def load_policy_agent(self,h5file_dir):
        h5file = h5py.File(h5file_dir, 'r')
        model = kerasutil.load_model_from_hdf5_group(h5file['model'])
        encoder_name = h5file['encoder'].attrs['name']
        board_width = h5file['encoder'].attrs['board_width']
        board_height = h5file['encoder'].attrs['board_height']
        encoder = self.get_encoder_by_name(encoder_name,board_height)
        return SeegaAgent(model,encoder)

    def get_encoder_by_name(self, name, board_size):
        module = importlib.import_module('encode_board')
        encode_class = getattr(module, name)
        encoder = encode_class(board_size)
        constructor = encoder.create(board_size)
        return constructor
    def prepare_experience_data(self,experience, board_width,board_height):
        """This takes the experience buffer"""
        experience_size = experience.actions.shape[0]
        target_vectors = np.zeros((experience_size,self.encoder.num_moves))
        for i in range(experience_size):
            action = experience.actions[1]
            reward = experience.rewards[1]
            target_vectors[i][action] = reward
        return target_vectors

    def get_agent_collector(self,player):
        if player =='black':
            return self.collector_black
        if player =='white':
            return self.collector_white

    def get_agent(self, player):
        if player == 'black':
            return self.agent_black
        if player == 'white':
            return self.agent_white

    # Rewrite the abstract method
    def play(self, dethToCover, board, step):
        if step == 0:
            a, b = self.playRandom(board, step)
            return a, b
        elif step == 1:
            a, b, c, d = self.playRandom(board, step)
            return a, b, c, d

    def playOld(self, board, step):  # OldPlay
        if (step == 0):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if (self.canPlayHere(board, step, i, j)):
                        return (i, j)
        if (step == 1):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if (self.canPlayHere(board, step, i, j)):
                        if board[i][j] == self.playerColor:
                            if len(self.getRealsMoves(board, i, j)) > 0:
                                print("ici", i, j, self.getRealsMoves(board, i, j)[0])
                                (c, d) = self.getRealsMoves(board, i, j)[0]
                                return (i, j, c, d)
        return -1

    def playRandom(self, board, step):

        #Start the game episode
        #self.collector_black.begin_episode()
        #self.collector_white.begin_episode()
        if (step == 0):
            if self.playerColor == 'black':
                player = 1

                game_state = {'board':board,'player':player,'step':step}
                move = self.agent_black.select_move(game_state)

            if self.playerColor == 'white':
                player = -1

                game_state = {'board': board, 'player': player, 'step': step}
                move = self.agent_white.select_move(game_state)
                print("MOVE FROM STEP 0: {}".format(move))




        if (step == 1):

            if self.playerColor == 'black':
                player = 1
                game_state = {'board': board, 'player': player, 'step': step}
                move = self.agent_black.select_move(game_state)

            if self.playerColor == 'white':
                player = -1

                game_state = {'board': board, 'player': player, 'step': step}
                move = self.agent_white.select_move(game_state)
                print("MOVE FROM STEP 1: {}".format(move))

        #Record the game state and move that was made
        return move
    def get_encoder_by_name(self, name, board_size):
        module = importlib.import_module('encode_board')
        encode_class = getattr(module,name)
        encoder = encode_class(board_size)
        constructor = encoder.create(board_size)
        return constructor
    def violate_rules(self, board, player, row, col, step):
        # If moves is empty, it means there are no valid players there
        # If the point predicted is empty or not
        if step == 0:
            if self.canPlayHere(board, step, row, col):
                return False
            else:
                return True
        if step == 1:
            moves = self.get_moves_from_point(board, player, row, col)
            if moves == []:
                return True
            else:
                return False
    def clip_probability(self,original_prob):
        #This is to make sure that the probabilities from the model don't go pushed all the way to 0 or 1
        min_p = 1e-5
        max_p = 1-min_p
        clipped_probs = np.clip(original_prob,min_p,max_p)
        clipped_probs = clipped_probs / np.sum(clipped_probs)
        return clipped_probs
    def get_moves_from_point(self, board, player, row, col):
        origins = self.getMovingPiece(board, self.player_to_color[player])
        print(origins)
        moving = []
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                # print(destination[0],destination[1],row,col)
                if destination[0] == row and destination[1] == col:
                    moving.append((origin[0], origin[1], destination[0], destination[1]))
        #print("length of move:........................", len(moving))
        return moving

    def isEmpty(self, board, x, y):
        print(board[x][y])
        if board[x][y] == 'None':
            return True
        else:
            return False

    def best_origin_to_move(self, board, all_moving_pieces, player):
        all_captured = []
        for i in all_moving_pieces:
            all_captured.append(self.canCapture(board, i[2], i[3], player))
        max_score_for_move = max(all_captured)

        return [(i[0], i[1], i[2], i[3]) for i in all_moving_pieces if
                self.canCapture(board, i[2], i[3], player) >= max_score_for_move]

    def best_score(self, board, all_moving_pieces, player):
        all_captured = []
        for i in all_moving_pieces:
            all_captured.append(self.canCapture(board, i[2], i[3], player))
        max_score_for_move = max(all_captured)

        return max_score_for_move

    def canCapture(self, board, x, y, player):

        gameSize = len(board)
        advNeighbours = []
        num = 0
        if (player == 1):
            color = 'black'
        else:
            color = 'white'
        for i in self.getPossibleMoves(x, y):
            if self.isPiece(board, i[0], i[1]) and board[i[0]][i[1]] != color:
                advNeighbours.append(i)
        if (len(advNeighbours) > 0):
            for adv in advNeighbours:
                if adv[0] != gameSize // 2 or adv[1] != gameSize // 2:
                    if (adv[0] == x):
                        print("Horizontal")

                        if adv[1] < y and 0 <= y - 2 < gameSize and self.isPiece(board, x, y - 2) and board[x][
                            y - 2] == color:
                            print("ok1")
                            num = num + 1

                        if adv[1] > y and 0 <= y + 2 < gameSize and self.isPiece(board, x, y + 2) and board[x][
                            y + 2] == color:
                            print("ok2")
                            num = num + 1

                    elif adv[1] == y:
                        print("vertical")
                        if adv[0] < x and 0 <= x - 2 < gameSize and self.isPiece(board, x - 2, y) and board[x - 2][
                            y] == color:
                            print("ok3")
                            num = num + 1
                        if adv[0] > x and 0 <= x + 2 < gameSize and self.isPiece(board, x + 2, y) and board[x + 2][
                            y] == color:
                            print("ok4")
                            num = num + 1

        return num

    def canCaptureBlank(self, board, x, y, player):

        gameSize = len(board)
        advNeighbours = []
        if (player == 1):
            color = 'black'
        else:
            color = 'white'
        for i in self.getPossibleMoves(x, y):
            if self.isPiece(board, i[0], i[1]) and board[i[0]][i[1]] != color:
                advNeighbours.append(i)
        if (len(advNeighbours) > 0):
            for adv in advNeighbours:
                if adv[0] != gameSize // 2 or adv[1] != gameSize // 2:
                    if (adv[0] == x):

                        if adv[1] < y and 0 <= y - 2 < gameSize and self.isPiece(board, x, y - 2) and board[x][
                            y - 2] == color:
                            board[x][y - 1] = None

                        if adv[1] > y and 0 <= y + 2 < gameSize and self.isPiece(board, x, y + 2) and board[x][
                            y + 2] == color:
                            board[x][y + 1] = None

                    elif adv[1] == y:
                        # vertical
                        if adv[0] < x and 0 <= x - 2 < gameSize and self.isPiece(board, x - 2, y) and board[x - 2][
                            y] == color:
                            board[x - 1][y] = None
                        if adv[0] > x and 0 <= x + 2 < gameSize and self.isPiece(board, x + 2, y) and board[x + 2][
                            y] == color:
                            board[x + 1][y] = None

    def getBestMoves(self, board, player):
        if (player == 1):
            color = 'black'
        else:
            color = 'white'

        moves = []
        origins = self.getMovingPiece(board, color)
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                moves.append((origin[0], origin[1], destination[0], destination[1]))
        best_origins = self.best_origin_to_move(board, moves, player)
        return best_origins

    def getBestScore(self, board, player):
        if (player == 1):
            color = 'black'
        else:
            color = 'white'
        moves = []
        origins = self.getMovingPiece(board, color)
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                moves.append((origin[0], origin[1], destination[0], destination[1]))
        return self.best_score(board, moves, player)

    def getMoves(self, board, player):
        if (player == 1):
            color = 'black'
        else:
            color = 'white'
        moves = []
        origins = self.getMovingPiece(board, color)
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                newBoard = self.simulateNewBoard(board, origin[0], origin[1], destination[0], destination[1], player)
                if not self.isStuck(newBoard, (-1 * player)):
                    moves.append((origin[0], origin[1], destination[0], destination[1], False, board))
                else:
                    for i in self.get_all_unstucking_moves(newBoard, player):
                        moves.append((i[0], i[1], i[2], i[3], i[4], i[5]))
        return moves

    def simulateNewBoard(self, board, old_x, old_y, new_x, new_y, player):
        if (player == 1):
            color = 'black'
        else:
            color = 'white'
        new_board = [[None for j in range(self.gameSize)] for i in range(self.gameSize)]

        for i in range(len(board)):
            for j in range(len(board)):
                new_board[i][j] = board[i][j]

        new_board[old_x][old_y] = None
        new_board[new_x][new_y] = color
        self.canCaptureBlank(new_board, new_x, new_y, player)
        return new_board

    def createNode(self, board, depth, player, state):
        if state == 0:
            node = []
            state = 1
        if state == 1:
            for move in self.getMoves(board, player):
                newSimuated = self.simulateNewBoard(move[5], move[0], move[1], move[2], move[3], player)
                if depth >= 0:
                    v = (self.canCapture(move[5], move[2], move[3], player)) * player
                    m = self.createNode(newSimuated, depth - 1, (-1 * player), 0)
                    if player == 1:
                        node.append((move, v, m))
                    if player == -1:
                        node.append((move, v, m))

        return node

    def sumNodes(self, nodes, depth, player, som, alpha, beta):
        if len(nodes) == 0:
            nodes.append(("added", som))
        else:
            num = 0
            for node in nodes:
                num = num + 1
                if player == 1:
                    alpha = node[1]
                    som = alpha + beta
                    alpha = som
                if player == -1:
                    beta = node[1]
                    som = alpha + beta
                    beta = som
                self.sumNodes(node[2], depth - 1, -player, som, alpha, beta)

    def printNode(self, nodes, depth, player, alpha, beta):
        if player == 1:
            best = -100
        if player == -1:
            best = 100
        num = 0
        for node in nodes:
            num = num + 1
            if depth == 0 or node[2][0][0] == "added":
                if player == 1:
                    best = max(best, node[2][0][1])

                if player == -1:
                    best = min(best, node[2][0][1])

            else:
                if player == -1:
                    val = self.printNode(node[2], depth - 1, -player, alpha, beta)

                    best = min(best, val)
                    beta = min(beta, best)
                    if alpha >= beta:
                        return beta
                else:
                    val = self.printNode(node[2], depth - 1, -player, alpha, beta)
                    best = max(best, val)
                    alpha = max(alpha, best)
                    if alpha >= beta:
                        return alpha
        return best

    def isStuck(self, board, player):
        if player == 1:
            color = 'black'
        if player == -1:
            color = 'white'
        if not self.getMovingPiece(board, color):
            return True
        return False

    def get_all_unstucking_moves(self, board, player):
        if player == 1:
            color = "black"
            adv_playerColor = "white"
        if player == -1:
            color = "white"
            adv_playerColor = "black"

        my_moves = self.getMovingPiece(board, color)
        unstucking_moves = list()

        for move in my_moves:
            if adv_playerColor in self.get_neighbours(board, move[0], move[1]):
                for i in self.getRealsMoves(board, move[0], move[1]):
                    unstucking_moves.append((move[0], move[1], i[0], i[1], True, board))
        return unstucking_moves

    def getMovingPiece(self, board, color):
        i, j = -1, -1
        movingPieces = list()
        for el in board:
            i += 1
            for p in el:
                j += 1
                if self.pieceCanMove(board, (i, j), color):
                    movingPieces.append((i, j))
            j = -1

        return movingPieces

    def pieceCanMove(self, board, origin, color):
        if board[origin[0]][origin[1]] is not None and board[origin[0]][origin[1]] == color and len(
                self.getRealsMoves(board, origin[0], origin[1])) > 0:
            return True
        return False

    def isPiece(self, board, x, y):
        if board[x][y] == None:
            return False
        return True

    def get_neighbours(self, board, x, y):
        possibles_neighbours = self.getPossibleMoves(x, y)
        neighbours = list()

        for coord in possibles_neighbours:
            if 0 <= coord[0] < self.gameSize and 0 <= coord[1] < self.gameSize:
                neighbours.append(board[coord[0]][coord[1]])
            return neighbours

    def is_valid_move(self,move,board,player):

        """Move here is gonna be in rows and column"""

        if len(move)==2:
            if board[move[0]][move[1]] is None:
                return True
            else:
                return False

        if len(move) ==4:
            if (move[2],move[3]) in self.getRealsMoves(board,move[0],move[1]) and board[move[0]][move[1]] == self.player_to_color[player]:
                return True
            else:
                return False

    def getPossibleMoves(self, x, y):
        return [(x + a[0], y + a[1]) for a in
                [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if ((0 <= x + a[0] < self.row) and (0 <= y + a[1] < self.row))]

    def getRealsMoves(self,board, x, y):
        moves = []
        for i in self.getPossibleMoves(x,y):
            if board[i[0]][i[1]] is None:
                moves.append(i)
        return moves
