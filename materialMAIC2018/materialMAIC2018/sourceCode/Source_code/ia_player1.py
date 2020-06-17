from player import Player
# from board import Board
import random
class IA(Player):

    #Team modify this
    name = "Alpha Zero"
    def __init__(self,position, gameSize):
        Player.__init__(self,position, gameSize)

    #Rewrite the abstract method
    def play(self, dethToCover, board, step):
        if step == 0:
            a, b = self.playRandom(board,step)
            return a, b
        elif step == 1:
            a, b, c, d = self.playRandom(board, step)
            return a, b, c, d

    def playOld(self, board,step): #OldPlay
        if(step==0):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if(self.canPlayHere(board,step,i,j)):
                        return (i,j)
        if(step==1):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if(self.canPlayHere(board,step,i,j)):
                        if board[i][j] == self.playerColor:
                            if len(self.getRealsMoves(board,i,j))>0:
                                print("ici",i,j,self.getRealsMoves(board,i,j)[0])
                                (c,d)=self.getRealsMoves(board,i,j)[0]
                                return (i,j,c,d)
        return -1

    def best_origin_to_move(self,board,all_moving_pieces,color):
        all_captured = []
        for i in all_moving_pieces:
            all_captured.append(self.canCapture(board, i[2], i[3], color))
        max_score_for_move = max(all_captured)
        if max_score_for_move==0:
            random_move=all_moving_pieces[random.randint(0,len(all_moving_pieces)-1)]
            return [(random_move[0],random_move[1],random_move[2],random_move[3])]
        else:
            return [(i[0],i[1],i[2],i[3]) for i in all_moving_pieces if self.canCapture(board,i[2],i[3],color)>=max_score_for_move ]

    def playRandom(self, board,step):
        playable=[]
        if(step==0):

            if self.canPlayHere(board,step,1,2):
                playable.append((1,2))
            else:
                if self.canPlayHere(board,step,2,1):
                    playable.append((2, 1))
                else:
                    if self.canPlayHere(board,step,3,2):
                        playable.append((3, 2))
                    else:
                        if self.canPlayHere(board,step,2,3):
                            playable.append((2, 3))
                        else:
                            if self.canPlayHere(board, step, 0, 2):
                                playable.append((0, 2))
                            else:
                                if self.canPlayHere(board, step, 2, 0):
                                    playable.append((2, 0))
                                else:
                                    if self.canPlayHere(board, step, 2, 4):
                                        playable.append((2, 4))
                                    else:
                                        if self.canPlayHere(board, step, 4, 2):
                                            playable.append((4, 2))
                                        else:
                                            for i in range(self.gameSize):
                                                for j in range(self.gameSize):
                                                    if self.canPlayHere(board,step,i,j):
                                                        playable.append((i,j))
            choix=playable[random.randint(0, len(playable)-1)]
            return choix[0],choix[1]
        if(step==1):
            moves = []

            origins = self.getMovingPiece(board, self.playerColor)
            for origin in origins:
                destinations = self.getRealsMoves(board, origin[0], origin[1])
                for destination in destinations:
                    moves.append((origin[0], origin[1], destination[0], destination[1]))
            best_origins = self.best_origin_to_move(board,moves,self.playerColor)
            l = best_origins[random.randint(0, len(best_origins) - 1)]
            return (l[0], l[1], l[2], l[3])

        return -1

    def canCapture(self, board, x, y, color):

        gameSize = len(board)
        advNeighbours = []
        num=0
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
                            num=num+1

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
