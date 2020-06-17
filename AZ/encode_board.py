import numpy as np
import os


class SeegaEncoder_Board():
    def __init__(self,gameSize):
        self.width = gameSize
        self.gameSize = gameSize
        self.height = gameSize
        self.layers_encode = 9
        self.point_to_index  ={1:(0,0,0,1),2:(0,0,1,0),3:(0,1,0,0),4:(0,1,0,2),5:(0,1,1,1),6:(0,2,0,1),7:(0,2,0,3),8:(0,2,1,2),9:(0,3,0,2),10:(0,3,0,4),11:(0,3,1,3),12:(0,4,0,3),13:(0,4,1,4),14:(1,0,0,0),15:(1,0,2,0),
                 16:(1,0,1,1),17:(1,1,0,1),18:(1,1,1,0),19:(1,1,2,1),20:(1,1,1,2),21:(1,2,0,2),22:(1,2,1,1),23:(1,2,2,2),24:(1,2,1,3),25:(1,3,0,3),26:(1,3,1,2),27:(1,3,1,4),28:(1,3,2,3),29:(2,0,1,0),30:(2,0,3,0),
                 31:(2,0,2,1),32:(2,1,2,0),33:(2,1,1,1),34:(2,1,3,1),35:(2,1,2,2),36:(2,2,2,1),37:(2,2,1,2),38:(2,2,2,3),39:(2,2,3,2),40:(2,3,2,2),41:(2,3,1,3),42:(2,3,3,3),43:(2,3,2,4),44:(2,4,2,3),45:(2,4,1,4),
                 46:(2,4,3,4),47:(1,4,1,3),48:(1,4,0,4),49:(1,4,2,4),50:(3,0,2,0),51:(3,0,3,1),52:(3,0,4,0),53:(3,1,3,0),54:(3,1,2,1),55:(3,1,4,1),56:(3,1,3,2),57:(3,2,3,1),58:(3,2,2,2),59:(3,2,4,2),60:(3,2,3,3),
                 61:(3,3,3,2),62:(3,3,2,3),63:(3,3,3,4),64:(3,3,4,3),65:(3,4,3,3),66:(3,4,2,4),67:(3,4,4,4),68:(4,0,3,0),69:(4,0,4,1),70:(4,1,3,1),71:(4,1,4,0),72:(4,1,4,2),73:(4,2,4,1),74:(4,2,4,3),75:(4,2,3,2),
                 76:(4,3,4,2),77:(4,3,3,3),78:(4,3,4,4),79:(4,4,4,3),80:(4,4,3,4), 81:(0,0),82:(0,1),83:(0,2),84:(0,3),85:(0,4),86:(1,0),87:(1,1),88:(1,2),89:(1,3),90:(1,4),91:(2,0),92:(2,1),93:(2,2),94:(2,3),95:(2,4),
                 96:(3,0),97:(3,1),98:(3,2),99:(3,3),100:(3,4),101:(4,0),102:(4,1),103:(4,2),104:(4,3),105:(4,4)}
        self.point_index = []
        self.point = []
        for item in self.point_to_index.items():
            self.point_index.append(item[0] - 1)
            self.point.append(item[1])
        self.number_of_moves = len(self.point_to_index)
        self.player_to_color = {1: 'black', -1: 'white'}
        self.color_to_player = {'black': 1, 'white': -1}
    def name(self):
        return "SeegaEncoder_Board"
    def encoded_layers(self):
        return self.layers_encode
    def board_width(self):
        return self.width
    def board_height(self):
        return self.height
    def num_moves(self):
        return self.number_of_moves
    def board_encode(self,board,player,step):
        '''

        :param board:
        :param player:
        :param step:
        :return:

        BLACK player = 1
        WHITE player = -1
        None = 0
        '''
        board_cols = self.width
        board_rows = self.height
        board_simulate =self.simulate_board(board)
        print("Making encoding for {} layers".format(self.layers_encode))
        num_classes = board_cols * board_rows
       # board_tensor = np.zeros((self.layers_encode,board_rows,board_cols))
        board_tensor = np.zeros((1,board_rows, board_cols,self.layers_encode))
        base_plane ={1:1,-1:-1}
        #encoding the board
        for i in range(board_rows):
            for j in range(board_cols):
                if board[i][j] == 'black':
                    board_tensor[0][i][j][7] = 1
                    player = 1
                    board_simulate[i][j] = 1
                    board_tensor[0][i][j][0] =1 #0 layer
                    if step ==0:
                        board_tensor[0][i][j][4] = 0
                    if step ==1:
                        board_tensor[0][i][j][4] = 1
                        num=0
                        opponent_capture = 0
                        for moves in self.getRealsMoves(board, i, j):
                            if (i,j,moves[0],moves[1]) in self.point:
                                newSimuated = self.simulateNewBoard(board, i, j,moves[0],moves[1],player)
                                num = self.canCapture(board, moves[0],moves[1], player) + num
                                opponent_capture = self.canCapture(newSimuated, i, j, player * -1) + opponent_capture
                        board_tensor[0][i][j][5] = num
                        board_tensor[0][i][j][6] = opponent_capture
                    if player == 1: #black player's turn
                        board_tensor[0][i][j][3] = 1
                    if player == -1: #white player's turn
                        board_tensor[0][i][j][3] = 0
                elif board[i][j] == 'white':
                    board_tensor[0][i][j][7] = 1
                    player = -1
                    board_simulate[i][j] = -1
                    board_tensor[0][i][j][1] = 1
                    if step ==0:
                        board_tensor[0][i][j][4] = 0
                    if step ==1:
                        board_tensor[0][i][j][4] = 1
                        num = 0
                        opponent_capture = 0
                        for moves in self.getRealsMoves(board, i, j):
                            if (i, j, moves[0], moves[1]) in self.point:
                                newSimuated = self.simulateNewBoard(board, i, j, moves[0], moves[1], player)
                                num = self.canCapture(board, moves[0], moves[1], player) + num
                                opponent_capture = self.canCapture(newSimuated, i, j, player * -1) + opponent_capture
                        board_tensor[0][i][j][5] = num
                        board_tensor[0][i][j][6] = opponent_capture
                    if player == 1:
                        board_tensor[0][i][j][3] = 1
                    if player == -1:
                        board_tensor[0][i][j][3] = 0
                elif board[i][j] == 'None':
                    board_tensor[0][i][j][8] = 1
                    board_simulate[i][j] = 0
                    board_tensor[0][i][j][2] = 1
                    if step ==0:
                        board_tensor[0][i][j][4] = 0
                    if step ==1:
                        board_tensor[0][i][j][5] = self.canCapture(board, i,j, player)
                        board_tensor[0][i][j][6] = self.canCapture(board, i, j, player*-1)
                        board_tensor[0][i][j][4] = 1
                    if player == 1:
                        board_tensor[0][i][j][3] = 1
                    if player == -1:
                        board_tensor[0][i][j][3] = 0
        return board_tensor


    def simulate_board(self,board):
        s_b =  np.copy(board)
        board_cols = s_b.shape[0]
        board_rows = s_b.shape[1]
        for i in range(board_rows):
         for j in range(board_cols):
             s_b[i][j] = board[i][j]
        return s_b

    def decode_point_index(self,index):
        #row = index // self.width
        #col = index % self.width
        return self.point[index]
    def encode_index(self,row,column):
        if (row,column) in self.point:
            return self.point.index((row,column))
        else:
            print("Wrong (row,column) index. Cannot find it in our action space!")



    def save_data(self,board_tensor,label):
        if os.path.exists('seega_board.npy') and os.path.exists('seega_board_move_point.npy')  :
            data = np.load("seega_board.npy")
            print("DATA_SHAPE:-----------------------{}".format(data.shape))
            #assert data.shape == (self.layers_encode,self.height,self.width)
            np.save('seega_board.npy', np.concatenate((data,board_tensor),axis=0))
            point_data=np.load("seega_board_move_point.npy")
            print("POINT_SHAPE:-----------------------{}".format(point_data.shape))
            np.save('seega_board_move_point.npy', np.concatenate((point_data,np.asarray([label])),axis=0))
        else:
            print("Creating Numpy file for saving seega moves")
            np.save('seega_board.npy',board_tensor)
            label=[label]
            label = np.asarray(label)
            print("siza of label: {}".format(label.shape))
            np.save('seega_board_move_point.npy', label)
    def create(self,board_size):
        return SeegaEncoder_Board(board_size)

    def canPlayHere(self, board, step, x, y,player):
        if step == 0:
            if x == self.gameSize // 2 and y == self.gameSize // 2:
                return False
            if board[x][y] is None:
                return True
            return False
        if step == 1:
            if board[x][y] is not None:
                if board[x][y] == self.player_to_color[player]:

                    return True
                else:
                    self.origin = None
                return False
            elif board[x][y] is None:
                if self.origin is not None:
                    return True
                return False


    def getPossibleMoves(self, x, y):
        return [(x + a[0], y + a[1]) for a in
                [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if ((0 <= x + a[0] < self.gameSize) and (0 <= y + a[1] < self.gameSize))]


    def getRealsMoves(self, board, x, y):
        moves = []
        for i in self.getPossibleMoves(x, y):
            if board[i[0]][i[1]] is None:
                moves.append(i)
        return moves


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


    def getPlayerPiece(self, board,player):
        playerPieces = []
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if board[i][j] is not None and board[i][j] == self.player_to_color[player]:
                    playerPieces.append((i, j))
        return playerPieces


    def pieceCanMove(self, board, origin, color):
        if board[origin[0]][origin[1]] is not None and board[origin[0]][origin[1]] == color and len(
                self.getRealsMoves(board, origin[0], origin[1])) > 0:
            return True
        return False


    def isPiece(self, board, x, y):
        if board[x][y] == None:
            return False
        return True

    def canCapture(self,board,x,y,player):

        gameSize = len(board)
        advNeighbours = []
        num=0
        if (player==1):
            color='black'
        else:
            color='white'
        for i in self.getPossibleMoves(x, y):
            if self.isPiece(board, i[0], i[1]) and board[i[0]][i[1]] != color:
                advNeighbours.append(i)
        if (len(advNeighbours) > 0):
            for adv in advNeighbours:
                if adv[0] != gameSize // 2 or adv[1] != gameSize // 2:
                    if (adv[0] == x):
                        #print("Horizontal")

                        if adv[1] < y and 0 <= y - 2 < gameSize and self.isPiece(board, x, y - 2) and board[x][
                            y - 2] == color:
                            #print("ok1")
                            num=num+1

                        if adv[1] > y and 0 <= y + 2 < gameSize and self.isPiece(board, x, y + 2) and board[x][
                            y + 2] == color:
                            #print("ok2")
                            num = num + 1

                    elif adv[1] == y:
                        #print("vertical")
                        if adv[0] < x and 0 <= x - 2 < gameSize and self.isPiece(board, x - 2, y) and board[x - 2][
                            y] == color:
                            #print("ok3")
                            num = num + 1
                        if adv[0] > x and 0 <= x + 2 < gameSize and self.isPiece(board, x + 2, y) and board[x + 2][
                            y] == color:
                            #print("ok4")
                            num = num + 1

        return num

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
        #self.canCaptureBlank(new_board, new_x, new_y, player)
        return new_board

