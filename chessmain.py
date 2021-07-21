import pygame as pg
import sys
import random
from random import randint
import chessengine, chessai

# GAME VARIABLES
# pixel sizes
sheight = 800
swidth = 1280
squareSize = 100

moveLogMargin = 30
moveLogPanelWidth = swidth-sheight - (moveLogMargin)*2 - 150
moveLogPanelHeight = sheight*3/5

btnHeight = moveLogPanelHeight*1/4-20
btnWidth = (swidth-sheight - moveLogPanelWidth)*3/4

undoBtnRect = pg.Rect(sheight + moveLogMargin + 280, sheight/6, btnWidth, btnHeight)
resetBtnRect = pg.Rect(sheight + moveLogMargin + 280, sheight/6 + btnHeight + 10, btnWidth, btnHeight)
resignBtnRect = pg.Rect(sheight + moveLogMargin + 280, sheight/6 + (2*btnHeight) + 20, btnWidth, btnHeight)
drawBtnRect = pg.Rect(sheight + moveLogMargin + 280, sheight/6 + (3*btnHeight) + 30, btnWidth, btnHeight)


#colors
black = pg.Color('black')
white = pg.Color('white')
undoAzure = (0, 128, 255)
resetSangria = (146, 0, 10)
lSquare = (238,238,210)
dSquare = (118,150,86)
selectedColor = (186,202,68)

#numerical values
maxFps = 10
dimension = 8

#positions
# boardx = swidth/2 - (squareSize*dimension/2) 
# boardy = sheight/2 - (squareSize*dimension/2)

#misc
images = {}

#chess pieces - images
def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        images[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"), (squareSize, squareSize))
    #we can access an image by doing images[wp] => white pawn, e.g.

#Main driver for game, handle user input and update graphics
def main():
    #initialize
    pg.init()
    clock = pg.time.Clock()
    pg.display.set_caption('Chess')
    screen = pg.display.set_mode((swidth, sheight)) #the pixel size of the screen
    # clock = pg.time.clock()
    screen.fill(white)
    gs = chessengine.GameState()
    validMoves = gs.getValidMoves() 
    moveMade = False
    gameOver = False
    loadImages()
    game_over = False
    playerOne = True
    #if human is white, this is true, if AI is playing then false

    playerTwo = False
    #if human is black, this is true, if AI is playing then false. This is default false - black AI

    sqselected = () #last click of the user
    playerClicks = [] #two tuples, keeping track of the player clicks, for instance, (6,4), (4,4) => pawn moves 2
    drawEndGameText(screen, "White to move")
    running = True
    whiteMoveTime = 0
    blackMoveTime = 0

    moveLogFont = pg.font.Font("Product Sans Regular.ttf", 12)
    btnFont = pg.font.Font("FontsFree-Net-SFProDisplay-Regular (2).ttf", 25)

    notatedmoveLog = []

    alliedColour = 'w' if gs.whiteToMove else 'b'

    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)#true
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTurn: #allow mouse algo to pass only if human turn. AI can use makeMove()
                    mouseloc = pg.mouse.get_pos()

                    if undoBtnRect.collidepoint(mouseloc):
                        gs.undoMove()
                        gameOver = False
                        if len(notatedmoveLog)>0:
                            notatedmoveLog.pop()
                        drawMoveLog(screen, notatedmoveLog, moveLogFont)
                        moveMade = True
                        game_over = False

                    if resetBtnRect.collidepoint(mouseloc):
                        gs = chessengine.GameState()
                        validMoves = gs.getValidMoves()
                        sqselected = ()
                        playerClicks = []
                        moveMade = False
                        gameOver = False
                        if len(notatedmoveLog)>0:
                            notatedmoveLog.clear()
                            drawMoveLog(screen, notatedmoveLog, moveLogFont)

                    if resignBtnRect.collidepoint(mouseloc):
                        gameOver = True
                        if gs.whiteToMove:
                            resetText(screen, 'White to move')
                            drawEndGameText(screen, "Black wins by resignation")
                            drawMoveLog(screen, notatedmoveLog, moveLogFont)
                        elif not gs.whiteToMove:
                            resetText(screen, 'Black to move')
                            drawEndGameText(screen, "White wins by resignation")
                            drawMoveLog(screen, notatedmoveLog, moveLogFont)      

                    if drawBtnRect.collidepoint(mouseloc):
                        gameOver = True     
                        resetText(screen, 'Black to move')
                        resetText(screen, 'White to move')
                        drawEndGameText(screen, "Drawn by agreement")
                        drawMoveLog(screen, notatedmoveLog, moveLogFont)


                    col = mouseloc[0]//squareSize
                    row = mouseloc[1]//squareSize

                
                    if sqselected == (row,col) or col >= 8: #if click, select, if its the same square, deselect
                        sqselected = () #deselect, empty
                        playerClicks = []
                    else:
                        sqselected = (row, col)
                        playerClicks.append(sqselected) 
                    if len(playerClicks) == 2: #this is the second click
                        move = chessengine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if gs.in_check:
                                    notatedmoveLog[-1] += '+'
                                elif gs.checkmate:
                                    notatedmoveLog[-1] += '#'
                                elif gs.stalemate:
                                    notatedmoveLog[-1] += '='
                                notatedmoveLog.append(move.getChessNotation())
                                print(notatedmoveLog)
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqselected = () #deselect after move
                                playerClicks = [] #reset clicks  
                                drawMoveLog(screen, notatedmoveLog, moveLogFont)

                        if not moveMade:
                            playerClicks = [sqselected]

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_u: #undo when U is pressed
                    gs.undoMove()
                    gameOver = False
                    if len(notatedmoveLog)>0:
                        notatedmoveLog.pop()
                    drawMoveLog(screen, notatedmoveLog, moveLogFont)
                    moveMade = True

                if event.key == pg.K_r:  # reset the game when 'r' is pressed
                    gs = chessengine.GameState()
                    validMoves = gs.getValidMoves()
                    sqselected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if len(notatedmoveLog)>0:
                        notatedmoveLog.clear()
                        drawMoveLog(screen, notatedmoveLog, moveLogFont)
                
        #AI move finder logic
        if not gameOver and not isHumanTurn:
            aimove = chessai.findBestMove(gs, validMoves)
            if aimove == None:
                aimove = chessai.findRandomMove #just a backup - in lost positions they will resort to random play
            gs.makeMove(aimove)
            notatedmoveLog.append(aimove.getChessNotation())
            print(notatedmoveLog)
            moveMade = True
            

        if moveMade:   
            # animateMove(gs.moveLog[-1], screen, gs.board, clock)
            if gs.whiteToMove:
                resetText(screen,'Black to move')
                resetText(screen,'Black wins by checkmate')
                resetText(screen,'White wins by checkmate')
                drawEndGameText(screen, "White to move")
                drawMoveLog(screen, notatedmoveLog, moveLogFont)

            else:
                resetText(screen, 'White to move')
                resetText(screen,'Black wins by checkmate')
                resetText(screen,'White wins by checkmate')                
                
                drawEndGameText(screen, "Black to move")
                drawMoveLog(screen, notatedmoveLog, moveLogFont)

            validMoves = gs.getValidMoves()
            moveMade = False
        

        drawGameState(screen, gs, validMoves, sqselected)
        drawUndo(screen, btnFont)
        drawReset(screen, btnFont)
        drawResign(screen, btnFont)
        drawDraw(screen, btnFont)
    

        if not gameOver:
            drawMoveLog(screen, notatedmoveLog, moveLogFont)
            
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                resetText(screen, 'White to move')
                drawEndGameText(screen, "Black wins by checkmate")
                drawMoveLog(screen, notatedmoveLog, moveLogFont)
            else:
                resetText(screen,'Black to move')
                drawEndGameText(screen, "White wins by checkmate")
                drawMoveLog(screen, notatedmoveLog, moveLogFont)
        elif gs.stalemate:
            gameOver = True
            resetText(screen,'Black to move')
            resetText(screen, 'White to move')
            drawEndGameText(screen, "Draw by Position")
            drawMoveLog(screen, notatedmoveLog, moveLogFont)

        clock.tick(maxFps)
        pg.display.flip()



#highlight possible squares in each move 

def highlightSquares(screen, gs, validMoves, sqselected):
    if sqselected != ():
        r, c = sqselected
        #if white to move, compare 'w' to the color of the board piece, else compare black
        # Check that the selected square is of a piece you can move 

        if gs.whiteToMove:
            if gs.board[r][c][0] == 'w': 
            # a pygame surface is an image you can impose on the screen
                s = pg.Surface((squareSize, squareSize))
                s.fill(selectedColor)
                screen.blit(s, (c*squareSize, r*squareSize)) #highlight the selected square yellow
                
                #highlight destination squares
                s.set_alpha(70) #  a transparency value, only for the black
                s.fill(pg.Color('black'))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c: #if the starting coords are requal to the starting square
                        screen.blit(s, (squareSize*move.endCol, squareSize*move.endRow))
        elif not gs.whiteToMove:
            if gs.board[r][c][0] == 'b': 
            # a pygame surface is an image you can impose on the screen
                s = pg.Surface((squareSize, squareSize))
                s.fill(selectedColor)
                screen.blit(s, (c*squareSize, r*squareSize)) #highlight the selected square yellow
                
                #highlight destination squares
                s.set_alpha(70) #  a transparency value, only for the black
                s.fill(pg.Color('black'))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c: #if the starting coords are requal to the starting square
                        screen.blit(s, (squareSize*move.endCol, squareSize*move.endRow))

#keeps updating, draws out the board and the pieces with pygame
def drawGameState(screen, gs, validMoves, sqselected):
    drawBoard(screen)
    #piece highlighting
    highlightSquares(screen, gs, validMoves, sqselected)
    drawPieces(screen, gs.board) #board from the chessengine file GS class. 2d arr

def drawBoard(screen):
    global colors
    #black and white is unpleasant - this is lichess theme
    colors = [lSquare, dSquare]  
    for r in range(dimension):
        for c in range(dimension):
            #diagnose color by row/column - evem yields light while odd dark
            color = colors[(r+c)%2] 
            '''
            params listed: surface, diagnosed color,rect object containing xval, yval and dimensions.
            the x and y val are squareSize*r/Squaresize*c +boardx/y
            the Squares are 'printed' one by one with the position of squaresize*r/c as r/c keeps going up with loop
            thus the square position are right next to the other squares, creating the illusion of a board
            the boardx/y is to center the squares in the display of 600x960 px
            '''
            pg.draw.rect(screen, color, pg.Rect(squareSize*c, squareSize*r, squareSize, squareSize))



#draw pieces based on current GS
def drawPieces(screen, board): #board from gamestate class from chessengine
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":#not empty
                '''
                https://www.pygame.org/docs/ref/surface.html?highlight=blit#pygame.Surface.
                BLIT is for placing images on a surface. The used params are (source, destination)
                source is from the images array which holds paths to the chess piece icon PNGs
                the destination can be coordinates or a rect value where the dimensions don't matter, 
                just the positions, but they need to be there to be a rect obj
                boardx is needed for the offset to center the piece.
                '''
                screen.blit(images[piece], pg.Rect(squareSize*c, r*squareSize, squareSize, squareSize))

'''
Undo Button
'''
def drawUndo(screen, font):
    pg.draw.rect(screen, undoAzure, undoBtnRect)
    text_object = font.render("Undo 'U'", True, pg.Color('white'))
    text_location = undoBtnRect.move((btnWidth-text_object.get_width())/2, (btnHeight-text_object.get_height())/2)
    screen.blit(text_object, text_location)

'''
Reset Button
'''
def drawReset(screen, font):
    pg.draw.rect(screen, resetSangria, resetBtnRect)
    text_object = font.render("Reset 'R'", True, pg.Color('white'))
    text_location = resetBtnRect.move((btnWidth-text_object.get_width())/2, (btnHeight-text_object.get_height())/2)
    screen.blit(text_object, text_location)

def drawResign(screen, font):
    pg.draw.rect(screen, pg.Color('black'), resignBtnRect)
    text_object = font.render("Resign", True, pg.Color('white'))
    text_location = resignBtnRect.move((btnWidth-text_object.get_width())/2, (btnHeight-text_object.get_height())/2)
    screen.blit(text_object, text_location)

def drawDraw(screen, font):
    pg.draw.rect(screen, dSquare, drawBtnRect)
    text_object = font.render("Draw", True, lSquare)
    text_location = drawBtnRect.move((btnWidth-text_object.get_width())/2, (btnHeight-text_object.get_height())/2)
    screen.blit(text_object, text_location)


'''Draw movelog'''

def drawMoveLog(screen, moveLog, font):
    moveLogRect = pg.Rect(sheight + moveLogMargin, sheight/6, moveLogPanelWidth, moveLogPanelHeight)
    pg.draw.rect(screen, pg.Color('black'), moveLogRect)
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        move_string = str(i // 2 + 1) + '. ' + str(moveLog[i]) + "  "
        if i + 1 < len(moveLog):
            move_string += str(moveLog[i + 1]) + "   "
        moveTexts.append(move_string)
        # print(moveTexts)

    moves_per_row = 3
    padding = 20
    line_spacing = 2
    text_y = padding
    for i in range(0, len(moveTexts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(moveTexts):
                text += moveTexts[i + j] + ' '

        text_object = font.render(text, True, pg.Color('white'))
        text_location = moveLogRect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

'''
Draw end of game text
'''
def drawEndGameText(screen, text):
    font = pg.font.Font("FontsFree-Net-SFProDisplay-Regular (2).ttf", 30)
    text_object = font.render(text, False, pg.Color("black"))
    text_location = pg.Rect(0, 0, sheight, sheight).move((sheight+swidth)/2 - text_object.get_width() / 2,
                                                                 sheight / 10 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)

def resetText(screen, text):
    font = pg.font.Font("FontsFree-Net-SFProDisplay-Regular (2).ttf", 30)
    text_object = font.render(text, False, pg.Color("white"))
    text_location = pg.Rect(0, 0, sheight, sheight).move((sheight+swidth)/2 - text_object.get_width() / 2,
                                                                 sheight / 10 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)



'''
animating
'''

# def animateMove(move, screen, board, clock):
#     global colors
#     dR = move.endRow - move.startRow
#     dC = move.endCol - move.startCol

#     framespersquare = 10 #fps
#     frameCount = (abs(dR) + abs(dC))*framespersquare 
#     #the number of frames we will have - squares moved through (dr + dc) multiplied by fps

#     for frame in range(frameCount + 1):
#         #animating - putting a frame for each 'position' with row and col - existing parameters of drawboard and drawpieces
#         row, col = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
#         #row is equal to startingRow plus the amount of rows it will move through, multiplied by the specific frame over the total frameCount.
#         #thus at the specific framecount, the row will be the position of the piece moving. Same holds with col.
#         drawBoard(screen)
#         drawPieces(screen, board)
#         #erase the moved piece
#         color = colors[(move.endRow + move.endCol) % 2]
#         endSquare = pg.Rect(move.endCol * squareSize, move.endCol * squareSize, squareSize, squareSize)
#         pg.draw.rect(screen, color, endSquare) 

#         #draw moved piece:
#         if move.pieceCaptured != '--':
#             if move.isEnPassantMove:
#                 enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
#                 endSquare = pg.Rect(move.endCol * squareSize, enpassantRow*squareSize, squareSize, squareSize)
#             screen.blit(IMAGES[move.pieceCaptured], endSquare)
#         # draw moving piece
#         screen.blit(images[move.pieceMoved], pg.Rect(col * squareSize, row * squareSize, squareSize, squareSize))
#         pg.display.flip()
#         clock.tick(60)

if __name__ == '__main__':
    main()