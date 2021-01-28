import random
import sys
import math

DEBUG = True
board = [i for i in range(0,9)]
player, computer, current_player = '','',''


def print_board():
    x = 1
    for index,i in enumerate(board):
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
        if DEBUG: print (char, end = end)

def select_char():
    chars=('X','O')
    if random.randint(0,1) == 0:
        return chars[::-1]
    return chars        

def equals3(a, b, c):
    return a == b and b == c and (a == 'X' or a == 'O')

def space_exist():
    return (board.count('X') + board.count('O')) != 9

def can_move(brd, player, move):
    return move in range(0,9) and not(brd[move] in ('X', 'O'))  #brd[move] == move

def can_win(brd):
    for i in range(3):
        if equals3(brd[i*3+0], brd[i*3+1], brd[i*3+2]):
            return True, brd[i*3+0]
    for i in range(3):
        if equals3(brd[0+i], brd[3+i], brd[6+i]):
            return True, brd[0+i]
    if equals3(brd[0], brd[4], brd[8]) or equals3(brd[6], brd[4], brd[2]):
        return True, brd[4]
    return False, None

MAX_DEPTH = 5 

def computer_move(brd):
    potential_moves = possible_moves(brd)

    if DEBUG: print('computer player %s, potential moves: %s' %(computer, potential_moves))

    if len(potential_moves) > 0:
        #move =  random.choice(potential_moves)
        move = None
        bestScore = -math.inf
        for i in potential_moves:
            brd[i] = computer
            score = minimax(brd, 0, -math.inf, math.inf, False)
            brd[i] = i
            if score > bestScore:
                move = i
                bestScore = score
        brd[move] = computer
        win, winner = can_win(brd)
        
        return True, win
    return False, False

def possible_moves(brd):
    potential_moves = []
    for i in brd:
        if i != 'X' and i != 'O':
            potential_moves.append(i)
    return potential_moves

def minimax(brd, depth, alpha, beta, maximizingPlayer):

    # someone wins
    wins, winner = can_win(brd)
    if wins:
        if winner == computer:
            return 10 * (MAX_DEPTH - depth + 1)

        else:
            return -10 * (MAX_DEPTH - depth + 1)

    moves = possible_moves(brd)
    # tie or reached maximum search depth
    if len(moves) == 0 or depth == MAX_DEPTH:
        return 0

    if maximizingPlayer:
        maxEval  = -math.inf
        moves = possible_moves(brd)
        for i in moves:
            brd[i] = computer
            score = minimax(brd, depth+1, alpha, beta, False)
            brd[i] = i
            maxEval = max(maxEval, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return maxEval

    else:
        minEval = math.inf
        moves = possible_moves(brd)
        for i in moves:
            brd[i] = player
            score = minimax(brd, depth+1, alpha, beta, True)
            brd[i] = i
            minEval = min(minEval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return minEval    

def make_move(brd, player, move):
    if can_move(brd, player, move):
        brd[move] = player
        win, winner  = can_win(brd)
        if DEBUG: print('win: %s' %(win))
        return True, win
    return False, False

player, computer = 'X', 'O'#select_char()

current_player = player #computer

if DEBUG: print('Player is [%s] and computer is [%s]\n' % (player, computer))       

won = False
while space_exist() and not won:
    print_board()
    moved = False
    if current_player == player:
        while not moved:
            if DEBUG: print('Make your move [0-8]: ')
            move = int(input())
            moved, won = make_move(board, current_player, move)
            if DEBUG and moved:
                print('Move: %s\n' % move)
            elif DEBUG:
                print('Invalid move, try again.')
        current_player = computer        
        if won and DEBUG: 
            print('Game over! Player wins')
            print_board()
            exit()
    else:
        moved, won = computer_move(board)
        current_player = player
        if won and DEBUG: 
            print('Game over! Computer wins')
            print_board()
            exit()
print("Tie")
   

