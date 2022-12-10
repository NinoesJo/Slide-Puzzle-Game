"""
Creating a Slide Puzzle game using Pygame in Python.
Author: Johan Nino Espino
Creation Date: 12/09/2022
"""

#Import section
import pygame, sys, random
from pygame.locals import *

# Create the constants for the game
BOARDWIDTH = 4 # Number of columns in the board
BOARDHEIGHT = 4 # Number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#Create constants for color (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

#Set each component of the game based on its color
BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20
BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

#Create the constants for the directions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

"""
This function sets up the buttons for the game, run the game loop, check if the user clicked on one of the option buttons, let the user slide the tiles either with the mouse or with a keyboard, and update the game after each tile slide.
 
Args:
    -
 
Returns:
    -
"""
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

    #Initialize Pygame, creates a clock, setting up the window, and create the caption
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    #Store the option buttons and their rectangles in OPTIONS
    RESET_SURF, RESET_RECT = makeText('Reset', TEXTCOLOR, TILECOLOR,WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF, NEW_RECT = makeText('New Game', TEXTCOLOR, TILECOLOR,WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Solve', TEXTCOLOR, TILECOLOR,WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

    mainBoard, solutionSeq = generateNewPuzzle(80)
    SOLVEDBOARD = getStartingBoard() #A solved board is the same as the board in a start state
    allMoves = [] #List of moves made from the solved configuration

    while True: # Main game loop
        slideTo = None # The direction, if any, a tile should slide
        msg = '' #Contains the message to show in the upper left corner
        if mainBoard == SOLVEDBOARD:
            msg = 'Solved!'

        drawBoard(mainBoard, msg)

        if mainBoard != SOLVEDBOARD:
            msg = 'Click tile or press arrow keys to slide.'
            drawBoard(mainBoard, 'Click tile or press arrow keys to slide.')

        checkForQuit()
        for event in pygame.event.get(): # Event handling loop
            if event.type == MOUSEBUTTONUP: #Check if the user use a mouse
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    #Check if the user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves) #Clicked on Reset button
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80) #Clicked on New Game button
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves) #Clicked on Solve button
                        allMoves = []
                else:
                    #Check if the clicked tile was next to the blank spot

                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN
                    
            elif event.type == KEYUP:
                #Check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo: #Runs when a slide has been made
            slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.', 8) #Show slide on screen
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) #Record the slide
        pygame.display.update() #Updates the game
        FPSCLOCK.tick(FPS)

"""
This function terminates and ends the game.
 
Args:
    -
 
Returns:
    -
"""
def terminate():
    pygame.quit()
    sys.exit()

"""
This function would terminate the game based on if there is a quit event or the user pressed on the Esc key.
 
Args:
    -
 
Returns:
    -
"""
def checkForQuit():
    for event in pygame.event.get(QUIT): #Get all the QUIT events
        terminate() #Terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): #Get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() #Terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) #Put the other KEYUP event objects back

"""
This function creates a board that represents a solved board.
 
Args:
    -
 
Returns:
    board (2d list): A 2d list that contains the tiles in its solved state
"""
def getStartingBoard():
    #Return a board data structure with tiles in the solved state
    #For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    #Returns [[1, 4, 7], [2, 5, 8], [3, 6, None]]
    counter = 1
    board = []
    for row in range(BOARDWIDTH):
        column = []
        for col in range(BOARDHEIGHT):
            column.append(counter) #Add the value into the list
            counter += BOARDWIDTH #Increment the counter value based on the board width
        board.append(column) #Add the column into the board list
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = None #The last tile would be empty
    return board

"""
This function gets the coordinates of where the blank space is at in the board.
 
Args:
    board (2d list): Represents the current board of the tiles
 
Returns:
    row (int): Represents the row of where the blank space is at
    col(int): Represents the column of where the blank space is at
"""
def getBlankPosition(board):
    # Return the row and column of board coordinates of the blank space
    for row in range(BOARDWIDTH):
        for col in range(BOARDHEIGHT):
            #Check if the current location is the blank space
            if board[row][col] == None:
                return (row, col)

"""
This function would swap the value of where the tile is at with the value of where the blank space is at.
 
Args:
    board (2d list): Represents the current board of the tiles
    move (str): Represents the direction that the user want to move
 
Returns:
    -
"""
def makeMove(board, move):
    # This function does not check if the move is valid
    blankx, blanky = getBlankPosition(board)

    #The value of the tile is swapped with the value for the blank space
    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

"""
This function check if it is possible to make the move that the user want to make.
 
Args:
    board (2d list): Represents the current board of the tiles
    move (str): Represents the direction that the user want to move
 
Returns:
    True (bool): The move is possible
    False (bool): The move is not possible
"""
def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board) #Get the coordinates for the blank space
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)

"""
This function randomly select a direction to slide the tiles.
 
Args:
    board (2d list): Represents the current board of the tiles
    lastMove (str): Represents the direction that the user want to move
 
Returns:
    random.choice(validMoves) (str): Represents a random move from the list
"""
def getRandomMove(board, lastMove  = None):
    #Start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # Remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    #Return a random move from the list of remaining moves
    return random.choice(validMoves)

"""
This function converts board coordinates to pixel coordinates by getting the pixel coordinates at the top left of that board space.
 
Args:
    tileX (int): Represents the x coordinates from the board
    tileY (int): Represents the y coordinates from the board
 
Returns:
    left (int): Represents the x pixel coordinates 
    top (int): Represents the y pixel coordinates
"""
def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)

"""
This function convert pixel coordinates to board coordinates.
 
Args:
    board (2d list): Represents the current board of the tiles
    xCoordinates (int): Represents the x pixel coordinates
    yCoordinates (int): Represents the y pixel coordinates
 
Returns:
    tileX (int): Represents the x board coordinates if the pixel coordinate passed a board space
    tileY (int): Represents the y board coordinates if the pixel coordinate passed a board space
"""
def getSpotClicked(board, xCoordinates, yCoordinates):
    #From the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(xCoordinates, yCoordinates):
                return (tileX, tileY)
    return (None, None)

"""
This function draw the tiles in the game.
 
Args:
    tilex (int): Represents the x board coordinates
    tiley (int): Represents the y board coordinates
    number (int): Represents the tile's number
    adjx (int): The adjustment for the x pixel coordinate
    adjy (int): The adjustment for the y pixel coordinate
 
Returns:
    -
"""
def drawTile(tilex, tiley, number, adjx = 0, adjy = 0):
    #Draw a tile at board coordinates tilex and tiley, optionally a few
    #Pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy,TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)

"""
This function makes the text appear on the screen.
 
Args:
    text (str): Represents the message
    color (tuple): Represents the text color
    bgcolor (tuple): Represents the background color
    top (int): Represent the x coordinate
    left (int): Represent the y coordinate
 
Returns:
    textSurf (pygame.Surface): The Surface object for the text
    textRect (pygame.Rect): The Rect object for the box to add the text
"""
def makeText(text, color, bgcolor, top, left):
    #Create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

"""
This function draws the board with the tiles.
 
Args:
    board (2d list): Represents the current board of the tiles
    message (str): Represents the text
 
Returns:
    -
"""
def drawBoard(board, message):
    #Display the message on the screen
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)
    
    #Draw each tile onto the board
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    #Draw the border of the board
    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    #Draw the buttons on the screen
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

"""
This function draws the board with the tiles.
 
Args:
    board (2d list): Represents the current board of the tiles
    direction (str): Represents the direction the user want to slide
    message (str): Represents the text
    animationSpeed (int): Represents the speed of the animation
 
Returns:
    -
"""
def slideAnimation(board, direction, message, animationSpeed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky
    
    #Prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()

    #Draw a blank space over the moving tile on the baseSurf Surface
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for adjCoordinate in range(0, TILESIZE, animationSpeed):
        #Animate the tile sliding over
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -adjCoordinate)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, adjCoordinate)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -adjCoordinate, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], adjCoordinate, 0)
        
        #Update the screen and ensure max framerate is held
        pygame.display.update()
        FPSCLOCK.tick(FPS)

"""
This function generates a new puzzle by scrambling the tile in the board.
 
Args:
    numSlides (int): Represents the number of random moves to make
 
Returns:
    board (2d list): Represent the new board that was created
    sequence (list): Represent the list of moves
"""
def generateNewPuzzle(numSlides):
    # From a starting configuration, make numSlides number of moves (and
    # Animate these moves)
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500) # pause 500 milliseconds for effect
    lastMove = None
    for tile in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', int(TILESIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)

"""
This function reset the puzzle game.
 
Args:
    board (2d list): Represents the current board of the tiles
    allMoves (list): Represents all the directional moves that the user made
 
Returns:
    -
"""
def resetAnimation(board, allMoves):
    #Make all of the moves in allMoves in reverse
    revAllMoves = allMoves[:] #Gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        #Set the correct directional value in the oppositeMove variable
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', int(TILESIZE / 2))
        makeMove(board, oppositeMove)

#Main program
if __name__ == '__main__':
    main()
