from player import Player
from sys import maxsize
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
            if self.playerColor == 'black':
                player = 1
            else:
                player = -1

            nodes = self.createNode(board,3,player,0)
            choice = []
            for i in range(len(nodes)):
                m = []
                m.append(nodes[i])
                choice.append(self.printNode(m, 3, player))
            if player == 1:
                bestChoice = [i for i in range(len(choice)) if choice[i] == (max(choice))]
            if player ==-1:
                bestChoice = [i for i in range(len(choice)) if choice[i] == (min(choice))]

            l=(nodes[bestChoice[random.randint(0, len(bestChoice)-1)]][0])
            return (l[0], l[1], l[2], l[3])
        return -1

    def best_origin_to_move(self,board,all_moving_pieces,player):
        all_captured = []
        for i in all_moving_pieces:
            all_captured.append(self.canCapture(board, i[2], i[3], player))
        max_score_for_move = max(all_captured)

        return [(i[0],i[1],i[2],i[3]) for i in all_moving_pieces if self.canCapture(board,i[2],i[3],player)>=max_score_for_move ]

    def best_score(self,board,all_moving_pieces,player):
        all_captured = []
        for i in all_moving_pieces:
            all_captured.append(self.canCapture(board, i[2], i[3], player))
        max_score_for_move = max(all_captured)

        return max_score_for_move
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
                            board[x][y - 1]= None

                        if adv[1] > y and 0 <= y + 2 < gameSize and self.isPiece(board, x, y + 2) and board[x][
                            y + 2] == color:
                            board[x][y + 1] = None

                    elif adv[1] == y:
                        #vertical
                        if adv[0] < x and 0 <= x - 2 < gameSize and self.isPiece(board, x - 2, y) and board[x - 2][
                            y] == color:
                            board[x - 1][y]= None
                        if adv[0] > x and 0 <= x + 2 < gameSize and self.isPiece(board, x + 2, y) and board[x + 2][
                            y] == color:
                            board[x + 1][y] = None

    def getBestMoves(self,board,player):
        if (player == 1):
            color = 'black'
        else:
            color = 'white'

        moves = []
        origins = self.getMovingPiece(board,color)
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                moves.append((origin[0], origin[1], destination[0], destination[1]))
        best_origins = self.best_origin_to_move(board,moves,player)
        return best_origins

    def getBestScore(self,board,player):
        if (player==1):
            color = 'black'
        else:
            color = 'white'
        moves = []
        origins = self.getMovingPiece(board,color)
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                moves.append((origin[0], origin[1], destination[0], destination[1]))
        return self.best_score(board,moves,player)

    def getMoves(self,board,player):
        if (player==1):
            color = 'black'
        else:
            color = 'white'
        moves = []
        origins = self.getMovingPiece(board,color)
        for origin in origins:
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            for destination in destinations:
                moves.append((origin[0], origin[1], destination[0], destination[1]))
        return moves

    def simulateNewBoard(self,board,old_x,old_y,new_x,new_y,player):
        if (player==1):
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

    def createNode(self,board,depth,player,state):
        if state==0:
            node=[]
            state=1
        if state == 1:
            for move in self.getMoves(board,player):
                newSimuated = self.simulateNewBoard(board, move[0], move[1], move[2], move[3], player)
                if depth >= 0:
                    v=(self.canCapture(board,move[2],move[3],player))*player
                    m=self.createNode(newSimuated,depth-1,(-1*player),0)
                    if player==1:
                        node.append((move,v,m))
                    if player==-1:
                        node.append((move,v,m))

        return node


    def printNode(self,nodes, depth, player):
        if len(nodes) == 0:
            return 0
        if player == 1:
            best = -100
        if player == -1:
            best = 100
        num = 0
        for node in nodes:
            num = num + 1
            val = self.printNode(node[2], depth - 1, -player)
            if player == -1:
                best = min(best, node[1] + val)
            else:
                best = max(best, node[1] + val)
        return best

