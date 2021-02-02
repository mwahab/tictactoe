import pygame as pg
from pygame.locals import *
import time
import random
import sys
from player import *

DEBUG = True

width, height = 400, 400
white = (255,255,255)
line_color = (0,0,0)
initiating_window, x_img, o_img = None, None, None

p1 = TicTacToePlayer('X', TicTacToePlayer.TYPES[0])
p2 = TicTacToePlayer('O', TicTacToePlayer.TYPES[1])
s = State(p1, p2)

screen = pg.display.set_mode((width, height + 100), 0, 32)

def drawXO(row, col): 
    if DEBUG: print("row %s col %s" %(row, col))
      
    # for the first row, the image 
    # should be pasted at a x coordinate 
    # of 30 from the left margin 
    if row == 1: 
        posx = 30
          
    # for the second row, the image  
    # should be pasted at a x coordinate  
    # of 30 from the game line      
    if row == 2: 
  
        # margin or width / 3 + 30 from  
        # the left margin of the window 
        posx = width / 3 + 30
          
    if row == 3: 
        posx = width / 3 * 2 + 30
   
    if col == 1: 
        posy = 30
          
    if col == 2: 
        posy = height / 3 + 30
      
    if col == 3: 
        posy = height / 3 * 2 + 30
      
    if(s.current_player.player == 'X'): 
          
        # pasting x_img over the screen  
        # at a coordinate position of 
        # (pos_y, posx) defined in the 
        # above code 
        screen.blit(x_img, (posy, posx))
    else: 
        screen.blit(o_img, (posy, posx)) 
    pg.display.update() 
   
def user_click():
    # get coordinates of mouse click 
    x, y = pg.mouse.get_pos()

    if DEBUG: print("user click: %s %s" %(x,y))
   
    # get column of mouse click (1-3) 
    if(x<width / 3): 
        col = 1
      
    elif (x<width / 3 * 2): 
        col = 2
      
    elif(x<width): 
        col = 3
      
    else: 
        col = None
   
    # get row of mouse click (1-3) 
    if(y<height / 3): 
        row = 1
      
    elif (y<height / 3 * 2): 
        row = 2
      
    elif(y<height): 
        row = 3
      
    else: 
        row = None
        
    # after getting the row and col,  
    # we need to draw the images at 
    # the desired positions
    move = 3*(row-1)+ ((col-1))
    player = s.current_player
    if(row and col and player.can_move(move, s.board)):
        s.update_state(move)
        if DEBUG: print(s.board)
        drawXO(row, col) 
        
        # change to computer player
        temp = s.current_player
        s.current_player = s.next_player
        s.next_player = temp

        #draw status and update move 
        draw_status()
        computer_action = s.current_player.choose_action(s.board)
        s.update_state(computer_action)
        drawXO(math.floor(computer_action / 3) + 1, (computer_action % 3) + 1) 

        # change to human player and update status
        temp = s.current_player
        s.current_player = s.next_player
        s.next_player = temp
        draw_status()

def game_initiating_window():
    global screen, initiating_window
    
    screen.blit(initiating_window, (0,0))
    pg.display.update()
    screen.fill(white)
    
    # drawing vertical lines 
    pg.draw.line(screen, line_color, (width / 3, 0), (width / 3, height), 7) 
    pg.draw.line(screen, line_color, (width / 3 * 2, 0), (width / 3 * 2, height), 7) 
   
    # drawing horizontal lines 
    pg.draw.line(screen, line_color, (0, height / 3), (width, height / 3), 7) 
    pg.draw.line(screen, line_color, (0, height / 3 * 2), (width, height / 3 * 2), 7)
    
    draw_status()

def draw_status():
    
    isWin, winner = s.current_player.can_win(s.board)

    if DEBUG: print(isWin)

    if isWin:
        message =  winner + " Won!"
    elif not s.current_player.space_exist(s.board):
        message = "Game Draw!"
    else:
        message = s.current_player.player + "'s Turn"

    font = pg.font.Font(None, 30)
    text = font.render(message, 1, (255, 255, 255))

    screen.fill((0,0,0), (0, 400, 500, 100))
    text_rect = text.get_rect(center =(width / 2, 500-50)) 
    screen.blit(text, text_rect) 
    pg.display.update()     

def reset_game():
    time.sleep(3)
    if DEBUG: print("reset_game")
    winner = None

    #p1 = TicTacToePlayer('X', TicTacToePlayer.TYPES[0])
    #p2 = MinimaxPlayer('Y')
    #s = State(p1, p2)
    s.reset()

    game_initiating_window()
        
def main():
    global screen, initiating_window, x_img, o_img

    if DEBUG: print("Main")
    
    pg.init()
    fps = 30
    CLOCK = pg.time.Clock()

    screen = pg.display.set_mode((width, height + 100), 0, 32)
    pg.display.set_caption("My Tic Tac Toe")

    initiating_window = pg.image.load("modified_cover.png")
    x_img = pg.image.load("x_modified.png")
    o_img = pg.image.load("o_modified.png")

    initiating_window = pg.transform.scale(initiating_window, (width, height+100))
    x_img = pg.transform.scale(x_img, (80, 80)) 
    o_img = pg.transform.scale(o_img, (80, 80))

    reset_game()

    while(True):
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                user_click()
                if s.isEnd: #current_player.can_win(s.board) or not s.current_player.space_exist(s.board):
                    reset_game()
        pg.display.update()
        CLOCK.tick(fps)

if __name__ == "__main__":
    if DEBUG: print("__name__")
    main()
