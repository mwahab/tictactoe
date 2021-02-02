import random
import sys
import math
import pickle

DEBUG = True

class TicTacToePlayer:
    TYPES = ["HUMAN", "COMPUTER"]

    def __init__(self, player, player_type):
        self.player = player
        self.player_type = player_type

    def reset(self):
        pass

    def feed_reward(self, reward):
        pass

    def add_state(self, state):
        pass

    def equals3(self, a, b, c):
        return a == b and b == c and (a == 'X' or a == 'O')

    def space_exist(self, board):
        return (board.count('X') + board.count('O')) != 9

    def can_move(self, move, board):
        return (move != None) and move in range(0,9) and not(board[move] in ('X', 'O'))

    def possible_moves(self, board):
        moves = []
        for i in board:
            if i != 'X' and i != 'O':
                moves.append(i)
        return moves

    def choose_action(self, board):
        return random.choice(self.possible_moves(board))
        
    def can_win(self, board):
        for i in range(3):
            if self.equals3(board[i*3+0], board[i*3+1], board[i*3+2]):
                return True, board[i*3+0]
        for i in range(3):
            if self.equals3(board[0+i], board[3+i], board[6+i]):
                return True, board[0+i]
        if self.equals3(board[0], board[4], board[8]) or self.equals3(board[6], board[4], board[2]):
            return True, board[4]
        return False, None


class MinimaxPlayer(TicTacToePlayer):
    MAX_DEPTH = 10 

    def __init__(self, player):
        super().__init__(player, TicTacToePlayer.TYPES[1])

    def choose_action(self, board):
        potential_moves = self.possible_moves(board)
        action = None

        if len(potential_moves) > 0:
            bestScore = -math.inf
            for i in potential_moves:
                nextState = board.copy()
                nextState[i] = self.player
                score = self.minimax(nextState, 0, -math.inf, math.inf, False)
                if score > bestScore:
                    action = i
                    bestScore = score
        
        return action

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):

        # someone wins
        wins, winner = self.can_win(board)
        if wins:
            if winner == self.player:
                return 10 * (MinimaxPlayer.MAX_DEPTH - depth + 1)

            else:
                return -10 * (MinimaxPlayer.MAX_DEPTH - depth + 1)

        moves = self.possible_moves(board)
        # tie or reached maximum search depth
        if len(moves) == 0 or depth == MinimaxPlayer.MAX_DEPTH:
            return 0

        if maximizingPlayer:
            maxEval  = -math.inf
            for i in moves:
                nextState = board.copy()
                nextState[i] = self.player
                score = self.minimax(nextState, depth+1, alpha, beta, False)
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
                board[i] = opponent
                score = self.minimax(board, depth+1, alpha, beta, True)
                board[i] = i
                minEval = min(minEval, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return minEval    

class RLPlayer(TicTacToePlayer):
    def __init__(self, player, playerType=TicTacToePlayer.TYPES[1], exp_rate=0.3):
        super().__init__(player, playerType)
        self.states = [] # record all positions taken
        self.lr = 0.2 # learning rate
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {} # dictionary of state -> value

    def get_hash(self, board, state=None):
        return (str(board) if state == None else str(state))

    def add_state(self, state):
        self.states.append(state)

    def choose_action(self, board):
        positions = self.possible_moves(board)
        action = None
        if random.uniform(0,1) <= self.exp_rate:
            action = random.choice(positions)
        else:
            value_max = -math.inf
            for p in positions:
                next_state = board.copy()
                next_state[p] = self.player
                next_state_value = self.states_value.get(self.get_hash(next_state))
                value = 0 if next_state_value is None else next_state_value
                if value >= value_max:
                    value_max = value
                    action = p
        return action

    def feed_reward(self, reward):
        for s in reversed(self.states):
            if self.states_value.get(s) is None:
                self.states_value[s] = 0
            self.states_value[s] += self.lr * (self.decay_gamma * reward - self.states_value[s])
            reward = self.states_value[s]

    def reset(self):
        self.states = []

    def save_policy(self):
        fw = open('policy_' + str(self.player), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def load_policy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()

class State:
    def __init__(self, p1, p2):
        self.board = [i for i in range(0,9)]
        self.p1 = p1
        self.p2 = p2
        self.reset()

    def get_hash(self):
        self.boardHash = str(self.board)
        return self.boardHash

    def winner(self):
        self.isEnd, winner = self.current_player.can_win(self.board)
        return winner

    def update_state(self, action):
        self.board[action] = self.current_player.player

    def give_reward(self):
        result = self.winner()
        if result == self.p1.player:
            self.p1.feed_reward(1)
            self.p2.feed_reward(-1)
        elif result == self.p2.player:
            self.p1.feed_reward(-1)
            self.p2.feed_reward(1)
        else: # tie
            self.current_player.feed_reward(0.1)
            self.next_player.feed_reward(0.5)

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
        self.current_player = self.p1
        self.next_player = self.p2

    def play(self, rounds=100):
        for i in range(rounds):
            #print ("Round {}".format(i))
            move_counter = 0
            while not self.isEnd:
                #positions = self.current_player.possible_moves(self.board)
                action = self.current_player.choose_action(self.board)
                #print("Move: %s to %s" %(self.current_player.player, action))
                self.update_state(action)
                self.boardHash = self.get_hash()
                self.current_player.add_state(self.boardHash)
                move_counter = move_counter + 1

                winner = self.winner()
                if winner == self.current_player.player or not self.next_player.space_exist(self.board):
                    if winner is not None:
                        print("Round %s: Winner is %s in %s moves" %(i, winner, move_counter))
                        #self.print_board()
                    else:
                        print("Round %s: Tie in %s moves" %(i, move_counter))
                    self.give_reward()
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
                #positions = self.current_player.possible_moves(self.board)
                action = self.current_player.choose_action(self.board)
            print("Move: %s to %s" %(self.current_player.player, action))
            self.update_state(action)
            self.boardHash = self.get_hash()
            self.current_player.add_state(self.boardHash)
            move_counter = move_counter + 1

            winner = self.winner()
            if winner == self.current_player.player or not self.next_player.space_exist(self.board):
                if winner is not None:
                    print("Winner is %s in %s moves" %(winner, move_counter))
                    self.print_board()
                else:
                    print("Tie in %s moves" %(move_counter))
                self.give_reward()
                self.reset()
                break

            # game is not over, update current player
            temp_player = self.current_player
            self.current_player = self.next_player
            self.next_player = temp_player



if __name__ == "__main__":
    #training
    p1 = RLPlayer('X')
    p2 = RLPlayer('O')
    s = State(p1, p2)

    #print("training...")
    #s.play(50000)

    #p1.save_policy()
    #p2.save_policy()

    #against human
    p1 = TicTacToePlayer('X', TicTacToePlayer.TYPES[0])
    p2 = MinimaxPlayer('O')
    s.p1 = p1
    s.p2 = p2
    s.reset()
    s.play2()
