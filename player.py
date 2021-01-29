import random
import sys
import math

DEBUG = True

class TicTacToePlayer:
    TYPES = ["HUMAN", "COMPUTER"]

    def __init__(self, board, player, player_type):
        self.board = board
        self.player = player
        self.player_type = player_type

    def equals3(self, a, b, c):
        return a == b and b == c and (a == 'X' or a == 'O')

    def space_exist(self):
        return (self.board.count('X') + self.board.count('O')) != 9

    def can_move(self, move):
        return (move != None) and move in range(0,9) and not(self.board[move] in ('X', 'O'))

    def possible_moves(self):
        moves = []
        for i in self.board:
            if i != 'X' and i != 'O':
                moves.append(i)
        return moves

    def make_move(self, move=None):
        if move == None:
            move = random.choice(self.possible_moves())
            
        if self.can_move(move):
            self.board[move] = self.player
            win, winner  = self.can_win()
            if DEBUG: print('Move: %s' %(move))
            return True, win
        return False, False

    def can_win(self):
        for i in range(3):
            if self.equals3(self.board[i*3+0], self.board[i*3+1], self.board[i*3+2]):
                return True, self.board[i*3+0]
        for i in range(3):
            if self.equals3(self.board[0+i], self.board[3+i], self.board[6+i]):
                return True, self.board[0+i]
        if self.equals3(self.board[0], self.board[4], self.board[8]) or self.equals3(self.board[6], self.board[4], self.board[2]):
            return True, self.board[4]
        return False, None


class MinimaxPlayer(TicTacToePlayer):
    MAX_DEPTH = 5 

    def make_move(self, move=None):
        potential_moves = self.possible_moves()

        if len(potential_moves) > 0:
            move = None
            bestScore = -math.inf
            for i in potential_moves:
                self.board[i] = self.player
                score = self.minimax(0, -math.inf, math.inf, False)
                self.board[i] = i
                if score > bestScore:
                    move = i
                    bestScore = score
            self.board[move] = self.player
            win, winner = self.can_win()
        
            return True, win
        return False, False

    def minimax(self, depth, alpha, beta, maximizingPlayer):

        # someone wins
        wins, winner = self.can_win()
        if wins:
            if winner == self.player:
                return 10 * (MinimaxPlayer.MAX_DEPTH - depth + 1)

            else:
                return -10 * (MinimaxPlayer.MAX_DEPTH - depth + 1)

        moves = self.possible_moves()
        # tie or reached maximum search depth
        if len(moves) == 0 or depth == MinimaxPlayer.MAX_DEPTH:
            return 0

        if maximizingPlayer:
            maxEval  = -math.inf
            for i in moves:
                self.board[i] = self.player
                score = self.minimax(depth+1, alpha, beta, False)
                self.board[i] = i
                maxEval = max(maxEval, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return maxEval

        else:
            minEval = math.inf
            if self.player == 'X':
                opponent = 'O'
            else:
                opponent = 'X'
            for i in moves:
                self.board[i] = opponent
                score = self.minimax(depth+1, alpha, beta, True)
                self.board[i] = i
                minEval = min(minEval, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return minEval    


