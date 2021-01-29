import random
import sys
import math
from player import *

DEBUG = True
board = [i for i in range(0,9)]

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
    print('\n')

def select_char():
    chars=('X','O')
    if random.randint(0,1) == 0:
        return chars[::-1]
    return chars        


players = []
players.append(TicTacToePlayer(board, 'X', TicTacToePlayer.TYPES[0]))
#players.append(TicTacToePlayer(board, 'X', TicTacToePlayer.TYPES[1]))
players.append(MinimaxPlayer(board, 'O', TicTacToePlayer.TYPES[1])) 

if DEBUG: print('Player %s is %s' %(players[0].player, players[0].player_type))
if DEBUG: print('Player %s is %s\n\n' %(players[1].player, 'minimax'))

won = False
move_count = 0

current_player = players[move_count % 2]

while current_player.space_exist() and not won:
    print_board()

    moved = False
    #if human player, solicit input for move!
    if current_player.player_type == TicTacToePlayer.TYPES[0]:
        while not moved:
            if DEBUG: print('Make your move [0-8]: ')
            move = int(input())
            moved, won = current_player.make_move(move)
            if DEBUG and not moved:
                print('Invalid move, try again.')
    else:
        moved, won = current_player.make_move()
    if moved: move_count = move_count + 1
    if won:
        if DEBUG: print('Game over, player %s won in %s moves.' %(current_player.player, move_count))
        print_board()
        exit()
    
    current_player = players[move_count % 2]

if DEBUG: print('Game over, tie!')        

exit()    
