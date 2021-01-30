import random
import sys
import math
import pickle

DEBUG = True

class TicTacToePlayer:
    TYPES = ["HUMAN", "COMPUTER"]

    def __init__(self, board, player, player_type):
        self.board = board
        self.player = player
        self.player_type = player_type

    def reset(self):
        pass

    def feedReward(self, reward):
        pass

    def addState(self, state):
        pass

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
    MAX_DEPTH = 10 

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

class RLPlayer(TicTacToePlayer):
    def __init__(self, board, player, playerType=TicTacToePlayer.TYPES[1], exp_rate=0.3):
        super().__init__(board, player, playerType)
        self.states = [] # record all positions taken
        self.lr = 0.2 # learning rate
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {} # dictionary of state -> value

    def getHash(self, state=None):
        return (str(self.board) if state == None else str(state))

    def addState(self, state):
        self.states.append(state)

    def chooseAction(self):
        positions = self.possible_moves()
        action = None
        if random.uniform(0,1) <= self.exp_rate:
            action = random.choice(positions)
        else:
            value_max = -math.inf
            for p in positions:
                next_state = self.board.copy()
                next_state[p] = self.player
                next_state_value = self.states_value.get(self.getHash(next_state))
                value = 0 if next_state_value is None else next_state_value
                if value >= value_max:
                    value_max = value
                    action = p
        return action

    def feedReward(self, reward):
        for s in reversed(self.states):
            if self.states_value.get(s) is None:
                self.states_value[s] = 0
            self.states_value[s] += self.lr * (self.decay_gamma * reward - self.states_value[s])
            reward = self.states_value[s]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_' + str(self.player), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()

class State:
    def __init__(self, p1, p2):
        self.board = [i for i in range(0,9)]
        self.p1 = p1
        self.p2 = p2
        self.reset()

    def getHash(self):
        self.boardHash = str(self.board)
        return self.boardHash

    def winner(self):
        self.isEnd, winner = self.current_player.can_win()
        return winner

    def updateState(self, action):
        self.board[action] = self.current_player.player

    def giveReward(self):
        result = self.winner()
        if result == self.p1.player:
            self.p1.feedReward(1)
            self.p2.feedReward(-1)
        elif result == self.p2.player:
            self.p1.feedReward(-1)
            self.p2.feedReward(1)
        else: # tie
            self.current_player.feedReward(0.1)
            self.next_player.feedReward(0.5)

    def print_board(self):
        x = 1
        for index,i in enumerate(self.board):
            end = ' | '
            if x%3 == 0:
                end = '\n'
                if i != 1: end += '--------\n'
            char = ' '
            if i in ('X', 'O'):
                char = i
            else:
                char = index
            x+=1
            print (char, end = end)
        print('\n')

    def reset(self):
        self.board = [i for i in range(0,9)]
        self.boardHash = None
        self.isEnd = False
        self.p1.reset()
        self.p2.reset()
        self.p1.board = self.board
        self.p2.board = self.board
        self.current_player = self.p1
        self.next_player = self.p2

    def play(self, rounds=100):
        for i in range(rounds):
            #print ("Round {}".format(i))
            move_counter = 0
            while not self.isEnd:
                positions = self.current_player.possible_moves()
                action = self.current_player.chooseAction()
                #print("Move: %s to %s" %(self.current_player.player, action))
                self.updateState(action)
                self.boardHash = self.getHash()
                self.current_player.addState(self.boardHash)
                move_counter = move_counter + 1

                winner = self.winner()
                if winner == self.current_player.player or not self.next_player.space_exist():
                    if winner is not None:
                        print("Round %s: Winner is %s in %s moves" %(i, winner, move_counter))
                        #self.print_board()
                    else:
                        print("Round %s: Tie in %s moves" %(i, move_counter))
                    self.giveReward()
                    self.reset()
                    break

                # game is not over, update current player
                temp_player = self.current_player
                self.current_player = self.next_player
                self.next_player = temp_player

    def play2(self):
        move_counter = 0
        print("\n\nHuman vs RL player\n\n")
        while not self.isEnd:
            self.print_board()
            action = None
            #if human player, solicit input for move!
            if self.current_player.player_type == TicTacToePlayer.TYPES[0]:
                print('Make your move [0-8]: ')
                action = int(input())
            else:
                positions = self.current_player.possible_moves()
                action = self.current_player.chooseAction()
            print("Move: %s to %s" %(self.current_player.player, action))
            self.updateState(action)
            self.boardHash = self.getHash()
            self.current_player.addState(self.boardHash)
            move_counter = move_counter + 1

            winner = self.winner()
            if winner == self.current_player.player or not self.next_player.space_exist():
                if winner is not None:
                    print("Winner is %s in %s moves" %(winner, move_counter))
                    self.print_board()
                else:
                    print("Tie in %s moves" %(move_counter))
                self.giveReward()
                self.reset()
                break

            # game is not over, update current player
            temp_player = self.current_player
            self.current_player = self.next_player
            self.next_player = temp_player



if __name__ == "__main__":
    #training
    temp_board = [i for i in range(0,9)]
    p1 = RLPlayer(temp_board, 'X')
    p2 = RLPlayer(temp_board, 'O')
    s = State(p1, p2)

    print("training...")
    s.play(50000)

    p1.savePolicy()
    p2.savePolicy()

    #against human
    p1 = TicTacToePlayer(s.board, 'X', TicTacToePlayer.TYPES[0])
    s.p1 = p1
    s.reset()
    s.play2()
