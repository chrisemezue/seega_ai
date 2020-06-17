import numpy as np

class Game_State():

    def __init__(self, board, player, step):
        #self.model = model
        #self.encoder = encoder
        self.board = board
        self.gameSize = 5
        self.player = player
        self.step = step
        self.player_to_color = {1: 'black', -1: 'white'}
        self.color_to_player = {'black': 1, 'white': -1}

    """
    game_state is a dictionary that contains:ff
    board
    player
    step
    """

    """
    It will have details about the board for the player, the move, and the board for the next_move.
    """

    def board(self):
        return self.board
    def player(self):
        return self.player

    def is_valid_move(self,move,board,player,step):

        """Move here is gonna be in rows and column"""
        if step == 0:
            if len(move)==2:
                if board[move[0]][move[1]] is None:
                    return True
                else:
                    return False
            else:
                return False
        if step ==1:
            if len(move) == 2:
                return False
            elif len(move) == 4:
                if (move[2],move[3]) in self.getRealsMoves(board,move[0],move[1]):
                    if board[move[0]][move[1]] == self.player_to_color[player]:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
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

    def getPossibleMoves(self, x, y):
        return [(x + a[0], y + a[1]) for a in
                [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if ((0 <= x + a[0] < self.gameSize) and (0 <= y + a[1] < self.gameSize))]

    def getRealsMoves(self,board, x, y):
        moves = []
        for i in self.getPossibleMoves(x,y):
            if board[i[0]][i[1]] is None:
                moves.append(i)
        return moves