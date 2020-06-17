# Created by HaroldKS at 21/08/2018
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from panel import Panel
from piece import Piece
from util import Trace
from seega_agent import SeegaAgent
import numpy as np
from player import Player
import time
from experience_collector import Experience_Collector
from experience_buffer import Experience_Buffer
from encode_board import SeegaEncoder_Board
import argparse
import h5py
from keras import Sequential
from keras import layers
from keras.layers import Dense
import os.path
from dlgo import kerasutil
import importlib
import pickle
import shutil

# Maybe Here have to delete inheritance from QWidget. Have to see that

number_of_games = 0
num_of_moves = 0
num_train = 0


class RulesGame:
    def __init__(self):
        self.step = 0
        self.i = 0
        self.seedOnBoard = 0
        self.nSeedPutOnStep0 = 0
        self.origin = None
        self.color = ["black", "white"]
        self.no_win = 0
        self.white_capture = []
        self.black_capture = []
        self.white_placed = 0
        self.black_placed = 0

        # super(GameWindow, self).__init__(parent)

    def canPlayHere(self, x, y):
        if (self.step == 0):
            if ((x == gameSize // 2 and y == gameSize // 2)):
                return False
            if ((game.board.squares[x][y].isPiece()) == False):
                return True
            return False
        if (self.step == 1):
            if game.board.squares[x][y].isPiece():
                if game.board.currentPlayer == game.board.squares[x][y].piece.getPlayer():
                    self.origin = (x, y)
                    return True
                else:
                    self.origin = None
                return False
            elif not game.board.squares[x][y].isPiece():
                if self.origin is not None:
                    return True
                return False

    def getPossibleMoves(self, x, y):
        return [(x + a[0], y + a[1]) for a in
                [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if ((0 <= x + a[0] < gameSize) and (0 <= y + a[1] < gameSize))]

    def getRealsMoves(self, x, y):
        moves = []
        for i in self.getPossibleMoves(x, y):
            if not game.board.squares[i[0]][i[1]].isPiece():
                # game.board.squares[i[0]][i[1]].setBackgroundColor("green")
                moves.append(i)
        return moves

    def getMovingPiece(self, color):
        i, j = -1, -1
        movingPieces = list()
        for el in game.board.squares:
            i += 1
            for p in el:
                j += 1
                if self.pieceCanMove((i, j), color):
                    movingPieces.append((i, j))
            j = -1
        return movingPieces

    def getPlayerPiece(self, player):
        playerPieces = []
        for i in range(gameSize):
            for j in range(gameSize):
                if game.board.squares[i][j].isPiece() and game.board.squares[i][j].piece.getColor() == game.board.color[
                    player]:
                    playerPieces.append((i, j))
        return playerPieces

    def hasCaptured(self, x, y, color):
        advNeighbours = []
        captured = []
        for i in self.getPossibleMoves(x, y):
            if game.board.squares[i[0]][i[1]].isPiece() and game.board.squares[i[0]][i[1]].piece.getColor() != color:
                advNeighbours.append(i)
        if (len(advNeighbours) > 0):
            for adv in advNeighbours:
                if adv[0] != gameSize // 2 or adv[1] != gameSize // 2:
                    if (adv[0] == x):
                        # print("Horizontal")
                        if adv[1] < y and 0 <= y - 2 < gameSize and game.board.squares[x][y - 2].isPiece() and \
                                game.board.squares[x][y - 2].piece.getColor() == game.board.squares[x][
                            y].piece.getColor():
                            # print("ok1")
                            captured.append((x, y - 1))
                        if adv[1] > y and 0 <= y + 2 < gameSize and game.board.squares[x][y + 2].isPiece() and \
                                game.board.squares[x][y + 2].piece.getColor() == game.board.squares[x][
                            y].piece.getColor():
                            # print("ok2")
                            captured.append((x, y + 1))

                    elif adv[1] == y:
                        # print("vertical")
                        if adv[0] < x and 0 <= x - 2 < gameSize and game.board.squares[x - 2][y].isPiece() and \
                                game.board.squares[x - 2][y].piece.getColor() == game.board.squares[x][
                            y].piece.getColor():
                            # print("ok3")
                            captured.append((x - 1, y))
                        if adv[0] > x and 0 <= x + 2 < gameSize and game.board.squares[x + 2][y].isPiece() and \
                                game.board.squares[x + 2][y].piece.getColor() == game.board.squares[x][
                            y].piece.getColor():
                            # print("ok4")
                            captured.append((x + 1, y))
        return captured

    def pieceCanMove(self, origin, color):
        if game.board.squares[origin[0]][origin[1]].isPiece() and game.board.squares[origin[0]][
            origin[1]].piece.getColor() == color and len(self.getRealsMoves(origin[0], origin[1])) > 0:
            return True
        return False

    def isStuck(self, color):

        if not self.getMovingPiece(color):
            return True
        return False

    def get_all_unstucking_moves(self, board, color, adv_color):
        my_moves = self.getMovingPiece(color)
        unstucking_moves = list()
        for move in my_moves:
            if adv_color in self.get_neighbours(board, move[0], move[1]):
                unstucking_moves.append(move)
        return unstucking_moves

    def get_neighbours(self, board, x, y):
        possibles_neighbours = self.getPossibleMoves(x, y)
        neighbours = list()
        for coord in possibles_neighbours:
            if 0 < coord[0] < 5 and 0 < coord[1] < 5:
                neighbours.append(board[coord[0]][coord[1]])
        return neighbours

    def play(self, x, y):
        global number_of_games
        if game.gameOneGoing:
            if (self.step == 0):
                if (self.canPlayHere(x, y) == True):
                    if (game.board.currentPlayer == 0):
                        game.board.squares[x][y].setPiece(Piece(0, "black"))
                        game.trace.add_action(game.board.currentPlayer, (x, y), self.step, game.board.getListBoard(),
                                              game.board.score)
                        self.black_placed += 1
                        self.seedOnBoard = self.seedOnBoard + 1
                        self.nSeedPutOnStep0 += 1
                        if (self.nSeedPutOnStep0 == 2):
                            game.board.currentPlayer = (game.board.currentPlayer + 1) % 2
                            self.nSeedPutOnStep0 = 0
                    elif (game.board.currentPlayer == 1):
                        game.board.squares[x][y].setPiece(Piece(1, "white"))
                        game.trace.add_action(game.board.currentPlayer, (x, y), self.step, game.board.getListBoard(),
                                              game.board.score)
                        self.white_placed += 1
                        self.seedOnBoard = self.seedOnBoard + 1
                        self.nSeedPutOnStep0 += 1
                        if (self.nSeedPutOnStep0 == 2):
                            game.board.currentPlayer = (game.board.currentPlayer + 1) % 2
                            self.nSeedPutOnStep0 = 0
                    game.panel.updateCurrentPlayer()
                putLim = game.board.gameSize * game.board.gameSize - 1
                if (self.seedOnBoard == putLim):
                    self.step = (self.step + 1) % 2
                    game.board.currentPlayer = (game.board.currentPlayer + 1) % 2
                    game.panel.updateCurrentPlayer()

                if self.seedOnBoard == putLim and self.isStuck(self.color[game.board.currentPlayer]):
                    game.board.currentPlayer = (game.board.currentPlayer + 1) % 2
                    game.panel.updateCurrentPlayer()


            elif (self.step == 1):
                if game.board.currentPlayer == 0:  # black player

                    if (self.canPlayHere(x, y)):
                        # print(self.isStuck((self.color[game.board.currentPlayer])), self.color[game.board.currentPlayer])
                        game.board.setDefaultColors()
                        # game.board.squares[x][y].setBackgroundColor("blue")
                        moves = self.getRealsMoves(x, y)
                        # print("Actual move",(x,y), "Possible Moves",moves, "Origin", self.origin)
                        if self.origin is not None and (x, y) in self.getRealsMoves(self.origin[0], self.origin[1]):
                            self.move(self.origin, (x, y), game.board.currentPlayer)
                            score = game.board.score
                            game.trace.add_action(game.board.currentPlayer, (self.origin, (x, y)), self.step,
                                                  game.board.getListBoard(), score)
                            game.board.setDefaultColors()
                            # print("Here")
                            tempOrigin = self.origin
                            self.origin = None
                            captured = self.hasCaptured(x, y, self.color[game.board.currentPlayer])
                            self.black_capture.append(len(captured))
                            # print(captured)
                            if (len(captured) > 0):
                                self.no_win = 0
                                for pos in captured:
                                    game.board.squares[pos[0]][pos[1]].removePiece()
                                    game.board.score[game.board.currentPlayer] += 1
                            else:
                                self.no_win += 1
                            # print("Joueur 0", game.board.score[game.board.currentPlayer])
                            game.panel.updateScore(game.board.score)

                            if self.checkForEnd():
                                winner = None
                                if game.board.score[game.board.currentPlayer] > game.board.score[
                                    (game.board.currentPlayer + 1) % 2]:
                                    winner = game.board.currentPlayer

                                    score = game.board.score
                                    game.save_winner_to_collector(winner, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed, score)

                                    s = str(number_of_games) + ':' + str(
                                        winner) + ':' + str(score) + ':' + 'Total no_moves: {}'.format(num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    # game.trace.winner = winner
                                    number_of_games += 1

                                    # game.newGame()
                                    # end = QMessageBox.information(game, "End",
                                    #                             f"{game.panel.playersName[game.board.currentPlayer]} Win")

                                elif game.board.score[game.board.currentPlayer] == game.board.score[
                                    (game.board.currentPlayer + 1) % 2]:
                                    winner = 2

                                    score = game.board.score
                                    game.save_winner_to_collector(winner, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed, score)
                                    s = str(number_of_games) + ':' + str(
                                        winner) + ':' + str(
                                        score) + ':' + "No winner. Barrier case." + ':' + 'Total no_moves: {}'.format(
                                        num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    # game.newGame()

                                # end = QMessageBox.information(game, "End", "No winner. Barrier case.")
                                # game.newGame()
                                else:
                                    winner = (game.board.currentPlayer + 1) % 2
                                    score = game.board.score
                                    game.save_winner_to_collector(winner, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed, score)

                                    s = str(number_of_games) + ':' + str(
                                        winner) + ':' + str(score) + ':' + 'Total no_moves: {}'.format(num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    # game.newGame()

                                    # end = QMessageBox.information(game, "End",
                                    #                             f"{game.panel.playersName[(game.board.currentPlayer + 1)%2]} Win")

                                # score = game.board.score
                                # game.trace.winner = winner
                                # game.trace.add_action(game.board.currentPlayer, (tempOrigin, (x, y)), self.step,
                                #                    game.board.getListBoard(), score)
                                # game.board.setDefaultColors()
                                # game.saveGame()
                                game.gameOneGoing = False
                            else:
                                if self.isStuck((self.color[((game.board.currentPlayer) + 1) % 2])):
                                    game.setStatusTip("Player is stuck")
                                    game.save_winner_to_collector(10, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed,
                                                                  game.board.score)
                                    s = str(number_of_games) + ':' + str(
                                        game.board.score) + ":" + "Player is stuck" + ':' + 'Total no_moves: {}'.format(
                                        num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    game.gameOneGoing = False
                                    # game.newGame()
                                else:
                                    game.board.currentPlayer = (game.board.currentPlayer + 1) % 2
                                    game.panel.updateCurrentPlayer()
                            game.board.setDefaultColors()
                            print(f"{self.no_win} move(s) with no win.")




                elif game.board.currentPlayer == 1:  # white player
                    if (self.canPlayHere(x, y)):
                        # print(self.isStuck((self.color[game.board.currentPlayer])), self.color[game.board.currentPlayer])
                        game.board.setDefaultColors()
                        # game.board.squares[x][y].setBackgroundColor("blue")
                        moves = self.getRealsMoves(x, y)
                        # print("Actual move",(x,y), "Possible Moves",moves, "Origin", self.origin)
                        if self.origin is not None and (x, y) in self.getRealsMoves(self.origin[0], self.origin[1]):
                            self.move(self.origin, (x, y), game.board.currentPlayer)
                            score = game.board.score
                            game.trace.add_action(game.board.currentPlayer, (self.origin, (x, y)), self.step,
                                                  game.board.getListBoard(), score)
                            # print(game.trace.get_actions()[-1])
                            tempOrigin = self.origin
                            self.origin = None
                            # print("Here")
                            captured = self.hasCaptured(x, y, self.color[game.board.currentPlayer])
                            self.white_capture.append(len(captured))
                            # print(captured)
                            if (len(captured) > 0):
                                self.no_win = 0
                                for pos in captured:
                                    game.board.squares[pos[0]][pos[1]].removePiece()
                                    game.board.score[game.board.currentPlayer] += 1
                            else:
                                self.no_win += 1
                            # print("Joueur 1", game.board.score[game.board.currentPlayer])
                            game.panel.updateScore(game.board.score)

                            if self.checkForEnd():
                                winner = None
                                if game.board.score[game.board.currentPlayer] > game.board.score[
                                    (game.board.currentPlayer + 1) % 2]:
                                    winner = game.board.currentPlayer

                                    score = game.board.score
                                    game.save_winner_to_collector(winner, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed, score)
                                    s = str(number_of_games) + ':' + str(
                                        winner) + ':' + str(score) + ':' + 'Total no_moves: {}'.format(num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    # game.newGame()
                                    # end = QMessageBox.information(game, "End",
                                    #                             f"{game.panel.playersName[game.board.currentPlayer]} Win")
                                elif game.board.score[game.board.currentPlayer] == game.board.score[
                                    (game.board.currentPlayer + 1) % 2]:
                                    winner = 2

                                    score = game.board.score
                                    game.save_winner_to_collector(winner, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed, score)
                                    s = str(number_of_games) + ':' + str(
                                        winner) + ':' + str(
                                        score) + ":" + "No winner. Barrier case." + ':' + 'Total no_moves: {}'.format(
                                        num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    # game.newGame()
                                    # end = QMessageBox.information(game, "End", "No winner. Barrier case.")
                                else:
                                    winner = (game.board.currentPlayer + 1) % 2
                                    score = game.board.score
                                    game.save_winner_to_collector(winner, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed, score)
                                    s = str(number_of_games) + ':' + str(
                                        winner) + ':' + str(score) + ':' + 'Total no_moves: {}'.format(num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    # game.newGame()
                                    # end = QMessageBox.information(game, "End",
                                    #                     f"{game.panel.playersName[(game.board.currentPlayer + 1)%2]} Win")
                                # score = game.board.score
                                # game.trace.winner = winner
                                # game.trace.add_action(game.board.currentPlayer, (tempOrigin, (x, y)), self.step,
                                #                     game.board.getListBoard(), score)
                                # game.board.setDefaultColors()
                                # game.saveGame()
                                game.gameOneGoing = False
                            else:
                                if self.isStuck((self.color[((game.board.currentPlayer) + 1) % 2])):
                                    game.setStatusTip("Player is stuck")
                                    game.save_winner_to_collector(10, self.white_capture, self.black_capture,
                                                                  self.white_placed, self.black_placed,
                                                                  game.board.score)
                                    s = str(number_of_games) + ':' + str(
                                        game.board.score) + ":" + "Player is stuck" + ':' + 'Total no_moves: {}'.format(
                                        num_of_moves)
                                    with open("game_record.txt", 'a+') as f:
                                        f.write(s + "\n")

                                        f.close()
                                    number_of_games += 1
                                    # game.newGame()
                                    game.gameOneGoing = False
                                else:
                                    game.board.currentPlayer = (game.board.currentPlayer + 1) % 2
                                    game.panel.updateCurrentPlayer()
                            game.board.setDefaultColors()
                            print(f"{self.no_win} move(s) with no win.")

    def move(self, origin, dest, currentPlayer):
        game.board.squares[origin[0]][origin[1]].removePiece()
        game.board.squares[dest[0]][dest[1]].setPiece(Piece(currentPlayer, self.color[currentPlayer]))

    def checkForEnd(self):
        # C'est con mais bon
        if not self.getPlayerPiece((game.board.currentPlayer + 1) % 2) or len(
                self.getPlayerPiece((game.board.currentPlayer + 1) % 2)) == 1:
            return True
        if self.no_win >= 50:
            return True


class BoardSquare(QLabel, QWidget, QtCore.QObject):
    trigger = QtCore.pyqtSignal(int, int)

    def __init__(self, col, row, gameSize, parent=None):
        super(BoardSquare, self).__init__(parent)
        # Dimensions
        self.setMinimumSize(100, 100)
        self.setScaledContents(False)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.trigger.connect(GameWindow.coord)
        self.column = col
        self.row = row
        self.gameSize = gameSize

        # In Game
        self.piece = None
        self.active = False
        self.setStatusTip(self.toNotation())
        # SquareColor
        if col % 2 == 0:
            if row % 2 == 0:
                self.__setColor(1)
                self.backgroundColor = "grey"
            else:
                self.__setColor(0)
                self.backgroundColor = "white"
        else:
            if row % 2 == 0:
                self.__setColor(0)
                self.backgroundColor = "white"
            else:
                self.__setColor(1)
                self.backgroundColor = "grey"

    def Active(self, active):
        self.active = active
        self.setStyleSheet('QLabel { background-color : ' + self.backgroundColor + '; }')

    def setActive(self, color):
        if (type(color) == str):
            self.active = True
            self.setStyleSheet('QLabel { background-color : ' + color + '; }')
        elif (type(color) == bool):
            self.active = color
            self.setStyleSheet('QLabel { background-color : ' + self.backgroundColor + '; }')

    def isPiece(self):
        if self.piece == None:
            return False
        return True

    def isActive(self):
        return self.active

    def getPiece(self):
        return self.piece

    def setPiece(self, piece):
        self.piece = piece
        self.setPixmap(piece.getImage())
        self.setStatusTip(self.toNotation() + " - " + self.piece.color)

    def removePiece(self):
        self.piece = None
        empty = QtGui.QPixmap(0, 0)
        self.setPixmap(empty)
        self.setStatusTip(self.toNotation())

    def __setColor(self, color):

        if color == 0:
            self.setStyleSheet("""QLabel { background-color : white; } """)
        elif color == 1:
            self.setStyleSheet("""QLabel { background-color : grey; } """)
        else:
            raise Exception("Incorrect chess square color")
        self.color = color

    def setBackgroundColor(self, color):
        self.backgroundColor = color
        self.setStyleSheet('QLabel { background-color : ' + color + '; }')

    def toNotation(self):
        coordinates = str()
        x = self.column
        y = self.row
        if self.column >= 0 and self.column < self.gameSize and self.row >= 0 and self.row < self.gameSize:
            coordinates += str(str(x) + " ")
            coordinates += str(str(y) + " ")
        return coordinates

    def mousePressEvent(self, ev):
        if ev.button() == 1:
            if self.active == True and game.gameOneGoing == True:
                pass


from ia_player import IA


class GameWindow(QMainWindow):
    dethToCover = 9

    def __init__(self, gameSize, players, train_samples, instance, timeout=.50, sleep_time=.500, parent=None, ):
        super(GameWindow, self).__init__(parent)
        self.setWindowTitle("[*] MAIC 2018 - Seega Game")
        self.saved = True
        self.timeout = timeout
        self.train_samples = train_samples
        self.instance = instance
        self.sleep_time = sleep_time
        self.statusBar()
        self.gameOneGoing = False
        self.setWindowIcon(QtGui.QIcon("pieces/icon.png"))
        layout = QHBoxLayout()
        layout.addStretch()
        # self.player1 is black
        # self.player2 is white
        self.player1 = players[0]
        self.player2 = players[1]

        '''                                                 
        black_agent_dir = 'agent/agent_black_player.hdf5'
        white_agent_dir = 'agent/agent_white_player.hdf5'



        self.collector_white = Experience_Collector()
        self.collector_black = Experience_Collector()
        self.agent_black.set_collector(self.collector_black)
        self.agent_white.set_collector(self.collector_white)
        '''
        # Instances of random players
        self.random_player_one = IA(0, gameSize)
        self.random_player_two = IA(1, gameSize)

        playersName = [player.getName() for player in players]
        self.board = Board(gameSize)
        self.trace = Trace(self.board.getListBoard(), playersName)
        self.rulesgame = RulesGame()
        layout.addWidget(self.board)
        layout.addSpacing(15)

        self.panel = Panel(self.board, playersName)

        layout.addWidget(self.panel)

        layout.addStretch()

        content = QWidget()
        content.setLayout(layout)
        self.setCentralWidget(content)
        self.createMenu()

    # @QtCore.pyqtSlot(int)
    # @QtCore.pyqtSlot('QString')
    @QtCore.pyqtSlot(int, QGraphicsObject)
    def coord(self):
        print("cc")
        # #print(GameWindow.message)

    def createMenu(self):

        menu = self.menuBar()
        # Game Menu
        gameMenu = menu.addMenu("Game")

        # New Game Submenu
        newGameAction = QAction(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon("pieces/New file.png")), 'New Game',
                                self)
        newGameAction.setShortcut(QtGui.QKeySequence.New)
        newGameAction.setStatusTip("New game Luncher")
        newGameAction.triggered.connect(self.newGame)
        gameMenu.addAction(newGameAction)

        gameMenu.addSeparator()

        # Load Game Submenu
        loadGameAction = QAction(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon("pieces/Open file.png")),
                                 'Load Game', self)
        loadGameAction.setShortcut(QtGui.QKeySequence.Open)
        loadGameAction.setStatusTip("Load a previous game")
        loadGameAction.triggered.connect(self.loadGame)
        gameMenu.addAction(loadGameAction)

        # Save Game
        saveGameAction = QAction(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon("pieces/Save.png")), 'Save Game',
                                 self)
        saveGameAction.setShortcut(QtGui.QKeySequence.Save)
        saveGameAction.setStatusTip("Save current game")
        saveGameAction.triggered.connect(self.saveGame)
        gameMenu.addAction(saveGameAction)

        # Load Game
        replayGameAction = QAction(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon("pieces/Save.png")), 'Replay Game',
                                   self)
        replayGameAction.setShortcut(QtGui.QKeySequence.Close)
        replayGameAction.setStatusTip("Replay ended game")
        replayGameAction.triggered.connect(self.replayGame)
        gameMenu.addAction(replayGameAction)

        gameMenu.addSeparator()

        # Exit and close game
        exitGameAction = QAction(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon("pieces/Close.png")), 'Exit Game',
                                 self)
        exitGameAction.setShortcut(QtGui.QKeySequence.Quit)
        exitGameAction.setMenuRole(QAction.QuitRole)
        exitGameAction.setStatusTip("Exit and close window")
        exitGameAction.triggered.connect(self.exitGame)
        gameMenu.addAction(exitGameAction)

        menu.addSeparator()

        # Help Menu
        helpMenu = menu.addMenu("Help")

        # Rules
        gameRulesAction = QAction(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon("pieces/Help.png")), 'Rules', self)
        gameRulesAction.setMenuRole(QAction.AboutRole)
        gameRulesAction.triggered.connect(self.gameRules)
        helpMenu.addAction(gameRulesAction)

        helpMenu.addSeparator()

        # About
        aboutAction = QAction('About', self)
        aboutAction.setMenuRole(QAction.AboutRole)
        aboutAction.triggered.connect(self.about)
        helpMenu.addAction(aboutAction)

    def save_winner_to_collector(self, winner, captured_white, captured_black, white_placed, black_placed, score):
        global num_of_moves
        # This will need to be edited later. Will need to model another rewarding system
        print("Length of white and black captured:     BLACK:{}      WHITE {}    ".format(len(captured_black),len(captured_white)))

        white_reward = []
        black_reward = []
        score_black = int(score[0])
        score_white = int(score[1])
        print("SCore for Black: {}".format(score_black))
        print("Score for White: {}".format(score_white))
        assert (white_placed == 12 and black_placed == 12)
        '''
        for i in range(white_placed):
            white_reward.append(score_white - score_black)
            black_reward.append(score_black - score_white)

        if len(captured_black) > len(captured_white):
            for i in range(len(captured_black)):
                if i <= len(captured_white) - 1:
                    # white_reward.append(captured_white[i]-captured_black[i])
                    # black_reward.append(captured_black[i]-captured_white[i])
                    white_reward.append((score_white - score_black)+captured_white[i])
                    black_reward.append((score_black - score_white)+captured_black[i])
                else:
                    # black_reward.append(captured_black[i])
                    black_reward.append((score_black - score_white)+captured_black[i])
        elif len(captured_black) < len(captured_white):
            for i in range(len(captured_white)):
                if i <= len(captured_black) - 1:
                    # white_reward.append(captured_white[i] - captured_black[i])
                    # black_reward.append(captured_black[i] - captured_white[i])
                    white_reward.append((score_white - score_black)+captured_white[i])
                    black_reward.append((score_black - score_white)+captured_black[i])
                else:
                    # white_reward.append(captured_white[i])
                    white_reward.append((score_white - score_black)+captured_white[i])

        else:
            for i in range(len(captured_black)):
                # white_reward.append(captured_white[i] - captured_black[i])
                # black_reward.append(captured_black[i] - captured_white[i])
                white_reward.append((score_white - score_black)+captured_white[i])
                black_reward.append((score_black - score_white)+captured_black[i])

        assert (len(white_reward) == len(captured_white) + white_placed and len(black_reward) == len(
            captured_black) + black_placed)
        print("---FINAL REWARD---")
        print("FOR WHITE: {}".format(white_reward))
        print("LENGTH : {}".format(len(white_reward)))
        print("FOR BLACK: {}".format(black_reward))
        print("Length : {}".format(len(black_reward)))
        self.collector_white.complete_episode(reward=white_reward)
        self.collector_black.complete_episode(reward=black_reward)
        '''

        if score_black > score_white:
            self.collector_white.complete_episode(reward=[-1 for i in range(len(white_reward))])
            self.collector_black.complete_episode(reward=[1 for i in range(len(black_reward))])
        elif score_white > score_black:
            self.collector_white.complete_episode(reward=[1 for i in range(len(white_reward))])
            self.collector_black.complete_episode(reward=[-1 for i in range(len(black_reward))])
        else:
            self.collector_white.complete_episode(reward=[1 for i in range(len(white_reward))])
            self.collector_black.complete_episode(reward=[1 for i in range(len(black_reward))])

        if number_of_games == self.train_samples:
            print("---COMPILING EXPERIENCE DATA---")
            self.exp_buf = Experience_Collector()
            experience_dict_white = {
                'states': self.collector_white.get_states(),
                'actions': self.collector_white.get_actions(),
                'rewards': self.collector_white.get_rewards(),
                'advantages': self.collector_white.get_advantages()

            }
            experience_dict_black = {
                'states': self.collector_black.get_states(),
                'actions': self.collector_black.get_actions(),
                'rewards': self.collector_black.get_rewards(),
                'advantages': self.collector_black.get_advantages()
            }

            experience_buffer = self.exp_buf.combine_experience(experience_dict_black, experience_dict_white)
            if os.path.isdir('experience2/experience{}'.format(self.instance)) == False:
                try:
                    os.mkdir('experience2/experience{}'.format(self.instance))
                except OSError:
                    print("ERROR CREATING DIRECTORY: experience2/experience{}".format(self.instance))

            filename = 'experience2/experience{}/seegaexperience{}.hdf5'.format(self.instance, self.instance)

            if os.path.isfile(filename):
                os.remove(filename)
            with h5py.File(filename, 'a') as experience_outf:
                experience_buffer.serialize(experience_outf)

    def load_policy_agent(self, h5file_dir):
        h5file = h5py.File(h5file_dir, 'r')
        model = kerasutil.load_model_from_hdf5_group(h5file['model'])
        encoder_name = h5file['encoder'].attrs['name']
        board_width = h5file['encoder'].attrs['board_width']
        board_height = h5file['encoder'].attrs['board_height']
        encoder = self.get_encoder_by_name(encoder_name, board_height)
        return SeegaAgent(model, encoder)

    def get_encoder_by_name(self, name, board_size):
        module = importlib.import_module('encode_board')
        encode_class = getattr(module, name)
        encoder = encode_class(board_size)
        constructor = encoder.create(board_size)
        return constructor

    def load_experience(self, h5file):
        """This loads the experience from the h5file"""
        return Experience_Buffer(states=h5file['experience']['states'], actions=h5file['experience']['actions'],
                                 rewards=h5file['experience']['rewards']
                                 )

    def is_train(self, num_of_games):
        if num_of_games == self.train_samples:
            return True
        else:
            return False

    def newGame(self, n_g):
        global num_of_moves
        global number_of_games
        global num_train

        exp_filename = 'experience2/seegaexperience_{}_{}.hdf5'.format(number_of_games, num_of_moves)
        print(exp_filename)

        num_of_moves = 0
        '''
        if n_g == self.train_samples: #it means it is time to train
            print("----Training model on all experience gathered----")
            num_train+=1
            updated_agent_filename = 'agent/agent_{}.hdf5'.format(num_train)

            number_of_games = 0
            lr = 0.003
            batch_size=2048


            #agent_white = load_policy_agent(h5file_dir=white_agent_dir)
            #agent_black = load_policy_agent(h5file_dir=black_agent_dir)
            experience_array=[]
            exp_dirs = os.listdir('experience/')
            for exp_dir in exp_dirs:
                path = 'experience/'+exp_dir
                for file in os.listdir(exp_dir):
                    filename=path+'/'+file
                    experience_array.append(self.load_experience(h5py.File(filename)))

            exp_buffer = Experience_Collector()
            final_buffer = exp_buffer.combine_buffer_array(experience_array)
            #exp_buffer = self.load_experience(h5py.File(exp_filename))

            #self.agent_white.train(exp_buffer,lr,batch_size)
            self.agent_black.train(final_buffer,lr,batch_size)
            self.agent_white.serialize(updated_agent_filename)
            self.agent_black.serialize(updated_agent_filename)
            self.player1.load_agent(updated_agent_filename,updated_agent_filename)
            self.player2.load_agent(updated_agent_filename, updated_agent_filename)

            #Delete all old experience files used during training


        '''
        self.agent_black = self.player1.get_agent('black')
        self.agent_white = self.player2.get_agent('white')

        self.collector_black = self.player1.get_agent_collector('black')
        self.collector_white = self.player2.get_agent_collector('white')

        self.collector_black.begin_episode()
        self.collector_white.begin_episode()

        # newGame = QMessageBox.question(self, 'New Game', "You're about to start a new Game.",
        #                              QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # if newGame == QMessageBox.Yes:
        self.board.resetBoard()
        game.board.score = [0, 0]
        self.gameOneGoing = True
        game.rulesgame = RulesGame()
        game.panel.updateScore([0, 0])
        self.board.activeAllSquares()
        self.board.setCurrentPlayer(0)
        self.panel.resetPanelPlayer()
        self.startBattle()

    def startBattle(self):
        global num_of_moves

        """
        The self play should be wrapped in a for loop
        """

        i = 0
        while self.gameOneGoing:
            app.processEvents()
            i = i + 1
            time.sleep(0.1)
            if self.board.currentPlayer == 0:
                board = self.board.getListBoard()
                # print(board)
                if self.rulesgame.step == 0:  # ici

                    (a, b) = self.player1.play(self.dethToCover, board, self.rulesgame.step)
                    way_of_move = "exactly"
                    if not self.rulesgame.canPlayHere(a, b):
                        print(f"Illegal move were returned by {self.player1.getName()}. A random choice will be made")
                        way_of_move = "randomly"
                        (a, b) = self.random_player_one.play(self.dethToCover, board, self.rulesgame.step)
                    self.rulesgame.play(a, b)
                    num_of_moves += 1
                    print(f'{self.player1.getName()} {way_of_move} plays ({a}, {b})')
                    time.sleep(self.sleep_time)
                    app.processEvents()
                else:
                    # print("here")
                    unstuck_moves = list()
                    if self.rulesgame.isStuck((self.rulesgame.color[((game.board.currentPlayer) + 1) % 2])):
                        unstuck_moves = self.rulesgame.get_all_unstucking_moves(board, self.rulesgame.color[
                            game.board.currentPlayer], self.rulesgame.color[((game.board.currentPlayer) + 1) % 2])
                        print("The adversary gets stuck. IA has to play a movement of this list:", unstuck_moves)
                    (a, b, c, d) = self.player1.play(self.dethToCover, board, self.rulesgame.step)
                    if (c, d) in self.rulesgame.getRealsMoves(a, b):
                        print(f'{self.player1.getName()} returns a legal move of the tile ({a}, {b}) to ({c}, {d})')
                    else:
                        print(f"Illegal move were returned by {self.player1.getName()}. A random choice will be made")
                        (a, b, c, d) = self.random_player_one.play(self.dethToCover, board, self.rulesgame.step)

                    if unstuck_moves:
                        if (a, b) in unstuck_moves:
                            print(f"{self.player1.getName()}\'s choice ({a}, {b}) is right.")
                        else:
                            import random
                            print(
                                f"{self.player1.getName()}\'s choice ({a}, {b}) is not right. A random move will be made.")
                            choice = unstuck_moves[random.randint(0, len(unstuck_moves) - 1)]
                            move_to_list = self.rulesgame.getRealsMoves(choice[0], choice[1])
                            move_to = move_to_list[random.randint(0, len(move_to_list) - 1)]
                            (a, b, c, d) = choice[0], choice[1], move_to[0], move_to[1]
                    print(f"{self.player1.getName()} moves tile on ({a}, {b}) to ({c}, {d}).")
                    self.board.squares[a][b].setBackgroundColor("blue")
                    self.board.squares[c][d].setBackgroundColor("green")
                    app.processEvents()
                    self.rulesgame.play(a, b)

                    self.board.squares[a][b].setBackgroundColor("blue")
                    self.board.squares[c][d].setBackgroundColor("green")
                    app.processEvents()
                    time.sleep(self.sleep_time)
                    app.processEvents()
                    self.rulesgame.play(c, d)
                    num_of_moves += 1
                    time.sleep(self.sleep_time)
                    app.processEvents()


            elif (self.board.currentPlayer == 1):
                board = self.board.getListBoard()
                if (self.rulesgame.step == 0):
                    (a, b) = self.player2.play(self.dethToCover, board, self.rulesgame.step)
                    way_of_move = "exactly"
                    if not self.rulesgame.canPlayHere(a, b):
                        print(f"Illegal move were returned by {self.player2.getName()}. A random choice will be made")
                        way_of_move = "randomly"
                        (a, b) = self.random_player_two.play(self.dethToCover, board, self.rulesgame.step)
                    self.rulesgame.play(a, b)
                    print(f'{self.player2.getName()} {way_of_move} plays ({a}, {b})')
                    time.sleep(self.sleep_time)
                    app.processEvents()
                else:
                    unstuck_moves = list()
                    if self.rulesgame.isStuck((self.rulesgame.color[((game.board.currentPlayer) + 1) % 2])):
                        unstuck_moves = self.rulesgame.get_all_unstucking_moves(board, self.rulesgame.color[
                            game.board.currentPlayer], self.rulesgame.color[((game.board.currentPlayer) + 1) % 2])
                        print("The adversary gets stuck. IA has to play a movement of this list:", unstuck_moves)
                    (a, b, c, d) = self.player2.play(self.dethToCover, board, self.rulesgame.step)
                    if (c, d) in self.rulesgame.getRealsMoves(a, b):
                        print(f'{self.player2.getName()} returns a legal move of the tile ({a}, {b}) to ({c}, {d})')
                    else:
                        print(f"Illegal move were returned by {self.player2.getName()}. A random choice will be made")
                        (a, b, c, d) = self.random_player_two.play(self.dethToCover, board, self.rulesgame.step)

                    if unstuck_moves:
                        if (a, b) in unstuck_moves:
                            print(f"{self.player2.getName()}\'s choice ({a}, {b}) is right.")
                        else:
                            import random
                            print(
                                f"{self.player2.getName()}\'s choice ({a}, {b}) is not right. A random move will be made.")
                            choice = unstuck_moves[random.randint(0, len(unstuck_moves) - 1)]
                            move_to_list = self.rulesgame.getRealsMoves(choice[0], choice[1])
                            move_to = move_to_list[random.randint(0, len(move_to_list) - 1)]
                            (a, b, c, d) = choice[0], choice[1], move_to[0], move_to[1]
                    print(f"{self.player1.getName()} moves tile on ({a}, {b}) to ({c}, {d}).")
                    self.board.squares[a][b].setBackgroundColor("blue")
                    self.board.squares[c][d].setBackgroundColor("green")
                    app.processEvents()
                    game.rulesgame.play(a, b)
                    self.board.squares[a][b].setBackgroundColor("blue")
                    self.board.squares[c][d].setBackgroundColor("green")
                    app.processEvents()
                    time.sleep(self.sleep_time)
                    app.processEvents()
                    game.rulesgame.play(c, d)
                    num_of_moves += 1
                    time.sleep(self.sleep_time)
                    app.processEvents()
            game.board.setDefaultColors()
        game.board.setDefaultColors()

    def loadGame(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Game')
        listBoard = None
        if name[0] != "":
            listBoard = self.trace.load_trace(name[0])
            if listBoard.winner != -1:
                # print(listBoard.winner)
                warning = QMessageBox.warning(self, "Game Ended", "This game is already finished")
            else:
                if not listBoard.get_actions():
                    self.trace = listBoard
                else:
                    self.gameOneGoing = True
                    self.board.resetBoard()
                    self.rulesgame = RulesGame()
                    self.board.putListBoard(listBoard.get_last_board()[3])
                    self.panel.setName(listBoard.names)
                    self.trace = listBoard
                    self.board.currentPlayer = (listBoard.get_last_board()[0] + 1) % 2
                    self.rulesgame.step = listBoard.get_last_board()[2]
                    self.panel.updateCurrentPlayer()
                    self.board.score = listBoard.score
                    self.panel.updateScore(self.board.score)
                    self.board.activeAllSquares()
        else:
            pass

    def saveGame(self):
        if self.gameOneGoing:
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Game')
            self.trace.write(name[0])
        else:
            warning = QMessageBox.warning(self, "Warning", "No game ongoing")

    def replayGame(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Game')
        listBoard = None
        i = -1
        if name[0] != "":
            listBoard = self.trace.load_trace(name[0])
            if listBoard.winner == -1:
                warning = QMessageBox.warning(self, "Game Not ended",
                                              "This game is not yet finished. Load it to finish it")
            else:
                self.board.resetBoard()
                # #print("Ok")
                self.rulesgame = RulesGame()
                self.panel.setName(listBoard.names)
                self.panel.updateScore([0, 0])
                actions = listBoard.get_actions()
                # print(actions)
                # #print(len(actions))
                # game.board.putListBoard(actions[1][3])
                # time.sleep(1)
                # game.board.putListBoard(actions[2][3])

                for action in actions:
                    i += 1
                    app.processEvents()
                    if action[2] == 0:
                        # #print(i, action[3], action[0])
                        # #print("ok")
                        game.board.currentPlayer = action[0]
                        game.panel.updateCurrentPlayer()
                        game.board.putListBoard(action[3])
                        time.sleep(self.sleep_time)
                    elif action[2] == 1:
                        game.panel.updateScore(action[4])
                        game.board.score = action[4]
                        # print(game.board.score)
                        game.board.currentPlayer = action[0]
                        game.panel.updateCurrentPlayer()
                        game.board.putListBoard(actions[i - 1][3])
                        origin, end = action[1]
                        game.board.squares[origin[0]][origin[1]].setBackgroundColor("blue")
                        time.sleep(self.sleep_time)
                        app.processEvents()
                        game.board.squares[end[0]][end[1]].setBackgroundColor("green")
                        time.sleep(self.sleep_time)
                        app.processEvents()
                        time.sleep(self.sleep_time)
                        game.rulesgame.move(origin, end, game.board.currentPlayer)
                        game.board.putListBoard(action[3])
                        time.sleep(self.sleep_time)
                        game.panel.updateScore(game.board.score)
                        app.processEvents()
                        game.board.setDefaultColors()
                end = QMessageBox.information(game, "End", f" {game.panel.playersName[game.board.currentPlayer]} Win")

    def exitGame(self):
        return True

    def gameRules(self):
        rules = "Seega Rules"
        box = QMessageBox()
        box.about(self, "Rules", rules)

    def about(self):
        about = "MAIC 2018 Seega Game by MIFY"
        box = QMessageBox()
        box.about(self, "About", about)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        if self.exitGame() == True:
            a0.accept()
        else:
            a0.ignore()


class Board(QWidget):
    def __init__(self, gameSize, parent=None):
        super(Board, self).__init__(parent)
        self.currentPlayer = 0
        self.color = ["black", "white"]
        self.gameSize = gameSize
        self.score = [0, 0]
        self.setFixedSize(100 * gameSize, 100 * gameSize)
        gridLayout = QGridLayout()
        gridLayout.setSpacing(0)
        self.blackColor = "brown"
        # self.blackColor = "#413B46"
        self.whiteColor = "#E0EEF1"
        self.selectColor = "blue"
        self.attackColor = "red"
        self.squares = list()
        for i in range(gameSize):
            tempList = list()
            for j in range(gameSize):
                square = BoardSquare(i, j, gameSize)
                gridLayout.addWidget(square, gameSize - i, j)
                # connect(chesssquares[i][j],SIGNAL(clicked(int,int)),this,SLOT(validateClick(int,int)));
                tempList.append(square)
            self.squares.append(tempList)
        self.setDefaultColors()
        self.setLayout(gridLayout)

    def setDefaultColors(self):
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if i % 2 == 0:
                    if j % 2 == 0:
                        self.squares[i][j].setBackgroundColor(self.blackColor)
                    else:
                        self.squares[i][j].setBackgroundColor(self.whiteColor)
                else:
                    if j % 2 == 0:
                        self.squares[i][j].setBackgroundColor(self.whiteColor)
                    else:
                        self.squares[i][j].setBackgroundColor(self.blackColor)

    def setCurrentPlayer(self, player):
        self.currentPlayer = player

    def resetBoard(self):
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                self.squares[i][j].removePiece()

    def activeAllSquares(self):
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                self.squares[i][j].setActive(True)

    def desactiveAllSquares(self):
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                self.squares[i][j].setActive(False)

    def getListBoard(self):
        list_board = []
        for i in range(self.gameSize):
            temp = []
            for j in range(self.gameSize):
                if not self.squares[i][j].isPiece():
                    temp.append(None)
                else:
                    temp.append(self.squares[i][j].piece.getColor())
            list_board.append(temp)
        return list_board

    def putListBoard(self, listBord):
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if listBord[i][j] == None:
                    self.squares[i][j].removePiece()
                elif listBord[i][j] == "black":
                    self.squares[i][j].setPiece(Piece(0, "black"))
                elif listBord[i][j] == "white":
                    self.squares[i][j].setPiece(Piece(1, "white"))


if __name__ == "__main__":
    import sys
    import ctypes

    myappid = 'myfi.maic.seega.1.0'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except AttributeError:
        pass
    app = QApplication(sys.argv)

    # Parse argument from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='total number of seconds credited to each player')
    parser.add_argument('-size', help='board size (5,7 or 9)')
    parser.add_argument('-ai0', help='path to the ai that will play as player 0')
    parser.add_argument('-ai1', help='path to the ai that will play as player 1')
    parser.add_argument('-s', help='time to show the board')
    parser.add_argument('-train_samples', help='number of self play episodes before training')
    parser.add_argument('-instance', help='number of game instance')
    args = parser.parse_args()

    # set the time to play
    timeout = float(args.t) if args.t is not None else .05
    sleep_time = float(args.s) if args.s is not None else .150

    # Set board size
    gameSize = int(args.size) if args.size is not None else 5
    if not gameSize >= 5 and gameSize % 2 == 1:
        raise Exception('the size should be odd and greater or equal to 5')

    player_type = ['human', 'human']
    player_type[0] = args.ai0 if args.ai0 != None else 'human'
    player_type[1] = args.ai1 if args.ai1 != None else 'human'
    for i in range(2):
        if player_type[i].endswith('.py'):
            player_type[i] = player_type[i][:-3]
    agents = [None for _ in range(2)]

    # load the agents
    for i in range(2):
        if player_type[i] != 'human':
            j = player_type[i].rfind('/')
            # extract the dir from the agent
            dir = player_type[i][:j]
            # add the dir to the system path
            sys.path.append(dir)
            # extract the agent filename
            file = player_type[i][j + 1:]
            # create the agent instance
            agents[i] = getattr(__import__(file), 'IA')(i, gameSize)

    if None in agents:
        raise Exception('Problems in  AI players instances.')
    game = GameWindow(gameSize, agents, train_samples=int(args.train_samples), instance=int(args.instance),
                      sleep_time=sleep_time, timeout=timeout)

    game.show()
    n_g = int(args.train_samples)
    for i in range(n_g+1):
        print("---PLAYING {} OF {} GAMES---".format(i+1, n_g))
        game.newGame(n_g)
    sys.exit(app.exec_())
