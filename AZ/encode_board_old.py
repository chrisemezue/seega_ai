import numpy as np
import os


class SeegaEncoder_Board():
    def __init__(self,gameSize):
        self.width = gameSize
        self.height = gameSize
        self.layers_encode = 4
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
                    board_simulate[i][j] = 1
                    board_tensor[0][i][j][0] =1
                    if step ==0:
                        board_tensor[0][i][j][1] = 0
                    if step ==1:
                        board_tensor[0][i][j][1] = 1
                    if player == 1:
                        board_tensor[0][i][j][2] = 1
                    if player == -1:
                        board_tensor[0][i][j][3] = 1
                elif board[i][j] == 'white':
                    board_simulate[i][j] = -1
                    board_tensor[0][i][j][0] = -1
                    if step ==0:
                        board_tensor[0][i][j][1] = 0
                    if step ==1:
                        board_tensor[0][i][j][1] = 1
                    if player == 1:
                        board_tensor[0][i][j][2] = 1
                    if player == -1:
                        board_tensor[0][i][j][3] = 1
                elif board[i][j] == 'None':
                    board_simulate[i][j] = 0
                    board_tensor[0][i][j][0] = 0
                    if step ==0:
                        board_tensor[0][i][j][1] = 0
                    if step ==1:
                        board_tensor[0][i][j][1] = 1
                    if player == 1:
                        board_tensor[0][i][j][2] = 1
                    if player == -1:
                        board_tensor[0][i][j][3] = 1
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

