import numpy as np
import pygame
import sys
import math

# define colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

# define dimensions of tic-tac-toe board
ROW_COUNT = 6
COLUMN_COUNT = 7

# initialize an empty board stored as a numpy array
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT)) # init board
    return board

# drop piece at specified row and column
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# check if column is available to drop pieces
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

# determine which height to drop piece in specified column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

# print the board array by inverting it vertically
def print_board(board):
    print(np.flip(board, 0))

# check if a player has won (i.e. gotten 4 pieces in a row)
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True


def draw_board(board):
    # initialize blank board 
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    # draw player pieces 
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == 1: # draw red pieces
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: # draw yellow pieces
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

# create and show empty board array
board = create_board()
print_board(board)
game_over = False
turn = 0

# Initialize graphics
pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height) # initialize size of board in pixels

RADIUS = int(SQUARESIZE/2 - 5) # radius of gamepiece 

screen = pygame.display.set_mode(size) 
draw_board(board) # display the board graphically
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

# Main game loop
while not game_over:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            pygame.quit()
            sys.exit()
            
        # Allows player to move their piece before dropping it
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            else: 
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        # Drop piece on user click
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            
            # If Player 1
            if turn == 0:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE)) # find column to drop piece

                if is_valid_location(board, col): # only drop the piece if column is free
                    row = get_next_open_row(board, col) 
                    drop_piece(board, row, col, 1) # drop piece at appropriate height

                    if winning_move(board, 1): # Check if it was a winning move
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True


            # If player 2 (do the same thing)
            else:                
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 2)

                    if winning_move(board, 2):
                        label = myfont.render("Player 2 wins!!", 1, YELLOW)
                        screen.blit(label, (40,10))
                        game_over = True

            print_board(board) # display updated board array
            draw_board(board) # display updated board graphically

            # switch turns
            turn += 1
            turn = turn % 2

            if game_over: # Exit finished game after 3 seconds
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()