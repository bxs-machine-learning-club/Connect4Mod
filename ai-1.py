import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

# initialize numpy array representing empty board 
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

# helper method to drop piece
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# check is column is available to drop piece
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

# get height at which to drop piece in a given column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

# display the board array by flipping it over the vertical axis
def print_board(board):
    print(np.flip(board, 0))

# check for 4 in a row of a given piece
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

# Helper function
# score window of 4 consecutive piece on how good or bad it is for the player in question
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    
    if window.count(piece) == 4: # 4 in a row of your piece, very good
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1: # 3 in a row, good
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2: # 2 in a row, decent
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1: # 3 in a row of opposing piece, bad
        score -= 4

    return score

# Score the board heuristically based on how good it is for the player in question
def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])] # get pieces in center column (vertical)
    center_count = center_array.count(piece) # count how many of your pieces are in the center column
    score += center_count * 3 

    ## Score Horizontal -- see how many horizontal 3's and 4's in a row you have
    for r in range(ROW_COUNT): 
        row_array = [int(i) for i in list(board[r,:])] # get a row of pieces (horizontal)
        for c in range(COLUMN_COUNT-3): 
            window = row_array[c:c+WINDOW_LENGTH] # get 4 piece horizontal windows in that row
            score += evaluate_window(window, piece) # score that window

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    ## Score negatively sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

# checks board to see if game is finished, returns True if it is, False otherwise
# does this by checking board to see if either there is 4 in a row of either 
# players' pieces or if all the spaces are filled
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0 

# get list of columns where a piece can be dropped
# helper function for minimax algorithm
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

"""
Returns optimal column for player and the expected score it will yield (column, score)
AI is the maximizing player, depth is 3 (meaning the AI looks 3 moves ahead)

Method is recursive. Base case is a leaf node. Compute scores for leaf nodes. If leaf node is terminal, game ended in a win, loss, or tie. Otherwise, the node represents a theoretical game 3 moves ahead. Compute the score of the theoretical board using the heuristic function. For a non-leaf Node, apply the minimax algorithm recursively until you get to a leaf Node. Importantly, if you are the AI player, you want to maximize your score, but if you are the human player, you want to minimize the AI's score. 
"""
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board) # find all possible moves for both players
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal: # base case: check if Node is a leaf, if so compute the score 
        if is_terminal: # If game over
            if winning_move(board, AI_PIECE): # If player won, very good
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE): # If other player won, very bad
                return (None, -10000000000000)
            else: # Game ended in a tie, neutral
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE)) # Score the board heuristically
    # move recursively to the base case
    if maximizingPlayer:   
        value = -math.inf
        column = random.choice(valid_locations) # AI plays all possible theoretical moves 
        for col in valid_locations:
            row = get_next_open_row(board, col) 
            b_copy = board.copy() # make a copy of the board (child Node)
            drop_piece(b_copy, row, col, AI_PIECE) # simulate the move
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1] # perform minimax on the child board
            if new_score > value: # get maximum score
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player -- same as max, except select minimum score
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value: # get minimum score 
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value



"""
def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col
"""

# draw graphic connect 4 board from board array
def draw_board(board):
    # init empty board
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    # draw each player's pieces in the board array
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

board = create_board() # init board array
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board) # draw empty graphic board
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

#turn = random.randint(PLAYER, AI) # randomize who goes first
turn = AI

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # allow human player to hover piece before dropping
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

        pygame.display.update()
        
        # player drops their piece by clicking
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            #print(event.pos)
            # Ask for Player 1 Input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE)) # get the column in which they dropped their piece

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col) # get the row
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE): # check if player won
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True

                    # switch turns and display the board
                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)


    # AI's turn
    if turn == AI and not game_over:                

        # Use minimax, looking at the board 5 moves ahead, to get the optimal column for the AI 
        col, minimax_score = minimax(board, 2, -math.inf, math.inf, True) 

        if is_valid_location(board, col): # Redundant, why?
            #pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE): # Check if AI won
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40,10))
                game_over = True

            # switch turns and display the board
            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()