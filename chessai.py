import random

pieceScore = {
    'K': 0,
    'Q': 9,
    'R': 5,
    'B': 3,
    'N': 3,
    'p': 1
}

'''
List of parameters for eval:

Material
Piece-Square Tables
Pawn Structure
Evaluation of Pieces
Evaluation Patterns
Mobility
Center Control
Connectivity
Trapped Pieces
King Safety
Space
Tempo
'''

CHECKMATE = 1000 #positive is winning for white. negative is winning for black
STALEMATE = 0

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def scoreMaterial(board): #purely based on material, not position
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score+= pieceScore[square[1]]
            elif square[0] == 'b':
                score-= pieceScore[square[1]] #based on the piece score
    return score

def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    bestMove = None
    random.shuffle(validMoves)
    opponentMinMaxScore = CHECKMATE #best score for black
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE #best score for white
        for opponentMove in opponentMoves:
            gs.makeMove(opponentMove)

            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE
            if gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board) #neg or pos compared to position
            #if white is winning by 5 points, and white to move, the score is 5, else if BTM then -5
            #if black is winning by 5 points, and black to move, the score is -5, else if WTM then 5
            #Score is just a magnitude

            if score > opponentMaxScore: #if the looping score is better than the best scenario so far, then make it equal to the best scenario
                opponentMaxScore = score #compare the looping score to the best scenario ^
            gs.undoMove()
        if opponentMinMaxScore > opponentMaxScore: 
            # if opponent max score is less than their previous max,
            # this is advantageous to the bot 'US' so this is our best move.
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove
