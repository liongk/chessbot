'''
Records current state of a chess game.
It also determines all valid moves at the state and keeps a log.
'''

class GameState:
    #what happens at the start - initialize
    def __init__(self):
        #board is an 8x8 2d list, each element represents a piece or an empty square
        #first char represents color (b/w) and second char represents the piece-type
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], 
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"], 
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"], 
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {
            'p': self.getPawnMoves, 
            'R': self.getRookMoves, 
            'N': self.getKnightMoves, 
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves, 
            'K': self.getKingMoves,
        }
        self.whiteToMove = True #white starts the game
        self.moveLog = []
        self.whiteKing = (7,4)
        self.blackKing = (0,4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = () #coordinate (r,c) where an enpassant is possible

        #not to check is castling is possible, but to check if castling rules are broken
        #for example, rook and king are not in original positions
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks, self.currentCastlingRight.bqs)]
        #can be updated as moves are played. In comparison to just keeping it equal to current Castling Right which is constant
    
    '''
    Update Castle Rights
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False    

        if move.pieceMoved == 'wR': #white rooks
            if move.startRow == 7:
                #col 0 - queen, col 7 - king
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
            
        elif move.pieceMoved == 'bR': #black rooks
            if move.startRow == 0:
                #col 0 - queen, col 7 - king
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        # else the rook is not in the original position so we don't do anything

    '''
    Making Moves
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--' #the starting square is emptied
        self.board[move.endRow][move.endCol] = move.pieceMoved #the end square is displaced with the piece
        self.moveLog.append(move) #append move in notation
        self.whiteToMove = not self.whiteToMove #switch turns

        if move.pieceMoved == 'wK':
            self.whiteKing = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKing = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            promotionPiece = str(input("Choose a piece to promote to: 'Q', 'R', 'B' or 'N'")).upper()
            move.promotionPiece += promotionPiece
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionPiece

        #enpassant capturing
        if move.isEnPassantMove == True:
            # print('enpassant')
            # print(self.board[move.startRow][move.endCol])
            self.board[move.startRow][move.endCol] = '--'
            
        #update enpassantpossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #absolute vsalue, black and white applies
            #double divide is integer division - black to move, 7+5/2 = row 6. White? 2+4/2 = row 3.
            self.enPassantPossible = ((move.startRow+move.endRow)//2, move.startCol)
            # print(self.enPassantPossible)
        else:
            self.enPassantPossible = ()

        #updating castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks, self.currentCastlingRight.bqs))
       
        #castleMove
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: 
                #moved to the right by 2 squares, indicating kingside castle
                #king is already moved in the getKingMoves function, this is just to move the rook
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] 
                #moves rook to the left of the king
                self.board[move.endRow][move.endCol+1] = '--' #empty original rook square
            else:
                #a queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol-2] 
                self.board[move.endRow][move.endCol-2] = '--' #empty original rook square

    #UNDO move
    
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop() #removes last move from log
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured #if its is empty it will return '--'
            self.whiteToMove = not self.whiteToMove #switch turns
            if move.pieceMoved == 'wK':
                self.whiteKing = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.blackKing = (move.startRow, move.startCol)
            
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)
            
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
                
            #undo castling rights
            self.castleRightsLog.pop() #get rid of new castle rights from undid move
            self.currentCastlingRight = self.castleRightsLog[-1] #set current castle rights to the latest one pre-undo       
            
            #undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    #kingside:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    #put the rook back
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    #put the rook back
                    self.board[move.endRow][move.endCol+1] = '--'

        self.checkmate = False
        self.stalemate = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)        
        
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            king_row = self.whiteKing[0]
            king_col = self.whiteKing[1]
        else:
            king_row = self.blackKing[0]
            king_col = self.blackKing[1]

        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                #endRow, endCol, [of the checker piece] row direction, column direction
                check_row = check[0]
                check_col = check[1]

                #square - row, col of the chekcing piece
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to

                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # once you get to the checking pieces'srow/col
                            break

                # get rid of any moves that don't block check or move king
                #STILL IN THE INCHECK CONDITIONAL
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].pieceMoved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])

            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)

        else:  # not in check - all moves are fine
            moves = self.getPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKing[0], self.whiteKing[1], moves)
        else:
            self.getCastleMoves(self.blackKing[0], self.blackKing[1], moves)
        
        if len(self.moveLog) >= 6: #shortest possible repetition is 6 moves
            if (self.moveLog[-1] == self.moveLog[-3] == self.moveLog[-5]) and (self.moveLog[-2] == self.moveLog[-4] == self.moveLog[-6]):
                self.stalemate == True
                #draw (stalemate) on third repetition based off movelog

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights

        return moves

    '''----------------------------------------------------------------'''

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKing[0]
            start_col = self.whiteKing[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.blackKing[0]
            start_col = self.blackKing[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = start_row + direction[0] * i
                endCol = start_col + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    end_piece = self.board[endRow][endCol]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (endRow, endCol, direction[0], direction[1])
                            # print(possible_pin)
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (i == 1 and enemy_type == "p" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((endRow, endCol, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks, or empty square
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            endRow = start_row + move[0]
            endCol = start_col + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                end_piece = self.board[endRow][endCol]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((endRow, endCol, move[0], move[1]))
        return in_check, pins, checks
    
    '''----------------------------------------------------------------'''

    '''Determine if the player is in check, r,c'''
    def inCheck(self):
        """
        Determine if a current player is in check
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKing[0], self.whiteKing[1])
        else:
            return self.squareUnderAttack(self.blackKing[0], self.blackKing[1])

    def squareUnderAttack(self, row, col):
        """
        Determine if enemy can attack the square row col
        """
        self.whiteToMove = not self.whiteToMove  # switch to opponent's point of view
        opponents_moves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove        
        for move in opponents_moves:
            if move.endRow == row and move.endCol == col:  # square is under attack
                return True
        return False


    '''
    Without considering checks
    '''
    def getPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of row
            for c in range(len(self.board[r])): #number of columns
                turn = self.board[r][c][0] #either black or white b/w
                if (turn == 'w' and self.whiteToMove == True) or (turn == 'b' and not self.whiteToMove == True):
                    piece = self.board[r][c][1] 

                    '''this looks for the piece on the board and matches each to the 
                    possible moves generated in the functions below'''

                    self.moveFunctions[piece](r, c, moves)
        return moves

    '''
    Get all the possible moves for the piece located at r, c then add the moves to the list
    '''

    '''----------------------------------------------------------------'''

    '''
    Get all the possible PAWN moves
    '''
    def getPawnMoves(self, r, c, moves):

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        #move one forwards
        #move two forward on move one
        if self.whiteToMove:
            '''
            check if square in front is empty
            consider the pawn is on e2. since the column is the same when moving, c is not changed
            but the row is the one changing. since the row goes from 8 at the bottom (see class move)
            it goes r-1
            '''
            if self.board[r-1][c] == '--': #1 square pawn advance
                if not piece_pinned or pin_direction == (-1,0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--': 
                    #if pawn is at starting sq, r6 and two spaces above is empty, twosq pawn move
                        moves.append(Move((r,c), (r-2, c), self.board))
            '''capturing'''
            if c-1 >= 0: #left captures
                if self.board[r-1][c-1][0] == 'b': #first character is labelled black
                    if not piece_pinned or pin_direction == (-1,-1):
                        moves.append(Move((r,c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r-1, c-1), self.board, isEnPassantMove=True))

            if c+1 <= 7: #right captures
                if self.board[r-1][c+1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r,c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r-1, c+1), self.board, isEnPassantMove=True))


        if not self.whiteToMove:
            '''
            check if square in back is empty
            consider the pawn is on e7. since the column is the same when moving, c is not changed
            but the row is the one changing. since the row goes from 8 at the bottom (see class move)
            it goes r-1
            '''
            if self.board[r+1][c] == '--': #1 square pawn advance
                if not piece_pinned or pin_direction == (1,0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == '--': 
                        #if pawn is at starting sq, r6 and two spaces above is empty, twosq pawn move
                        moves.append(Move((r,c), (r+2, c), self.board))
            '''capturing'''
            if c-1 >= 0: #left captures
                if self.board[r+1][c-1][0] == 'w': #first character is labelled black
                    if not piece_pinned or pin_direction == (1,-1):
                        moves.append(Move((r,c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r+1, c-1), self.board, isEnPassantMove=True))

            if c+1 <= 7: #right captures
                if self.board[r+1][c+1][0] == 'w':
                    if not piece_pinned or pin_direction == (1,1):
                        moves.append(Move((r,c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r+1, c+1), self.board, isEnPassantMove=True))

    '''
    Get all the possible ROOK moves
    '''
    def getRookMoves(self, r, c, moves):
        '''adds directions to four sides, so each move is just a repeat of these'''
        '''forming (r,c)'''

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        dirs = ((1,0), (-1,0), (0,1), (0,-1)) #down, up, right, left
        enemyColor = 'b' if self.whiteToMove else 'w'

        '''if white, black. if black, white.'''

        for d in dirs:
            for i in range(1, 8):#just a simple for loop
                endRow = r+d[0]*i 
                '''
                #the for loop adds one to i every loop. because of this,
                #the endrow contains the possible rows a rook can go to.
                #in 'dirs', index 0 represents the row, going from 0 to 8, up and down.
                #the same goes for endcol.
                

                #'r' and 'c' are variables holding the current rook's position.
                #Thus, we keep adding rows to 'r' and columns to 'c' as a rook can
                #travel through rows or columns indefinitely.
                '''
                
                endCol = c+d[1]*i  
                
                '''
                #endRow MUST only go from 0 to 7, as does endCol as seen in object Move
                #This is why it is important to compare and keep adding to the rook's current position 
                #to see how far it can travel down a row or column.
                '''

                if 0 <= endRow < 8 and 0<= endCol < 8: 
                    #if it is on the board'''
                    if not piece_pinned or pin_direction == [d] or pin_direction == (-d[0], -d[1]):
                    #move towards and away from the pin
                        obstaclePiece = self.board[endRow][endCol]
                        if obstaclePiece == '--': #if there are no obstacles,
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            #this is still in the for loop, so the possible moves keep getting added'''
                        elif obstaclePiece[0] == enemyColor:
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break 
                            #if there is an enemy obstacle piece. 
                            #append this final valid move where it gets to the enemy's square, a capture!
                            #then break because you can't jump over pieces with a rook
                        else:
                            break
                            #can't capture non-enemy pieces
                else:
                    break
                    #stop adding new possible moves once it gets out of the board's range
    
    '''
    Get all the possible KNIGHT moves
    '''
    def getKnightMoves(self, r, c, moves):

        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((2,1), (2,-1),(-2,1), (-2,-1),
                        (1,2), (1,-2),(-1,2), (-1,-2))
        ally_color = "w" if self.whiteToMove else "b"
        
        for move in knightMoves:
            endRow = r+move[0]
            endCol = c+move[1]
            if 0 <= endRow < 8 and 0<= endCol < 8:  
                if not piece_pinned:
                        end_piece = self.board[endRow][endCol]
                        if end_piece[0] != ally_color:  # so its either enemy piece or empty square
                            moves.append(Move((r, c), (endRow, endCol), self.board))
    '''
    Get all the possible BISHOP moves
    '''
    def getBishopMoves(self, r, c, moves):

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        '''adds directions to four sides, so each move is just a repeat of these'''
        '''forming (r,c)'''

        dirs = ((1,1), (1,-1), (-1,1), (-1,-1)) #topright, topleft, bottomright, bottomleft
        enemyColor = 'b' if self.whiteToMove else 'w'

        '''if white, black. if black, white.'''
        for d in dirs:
            for i in range(1, 8):
                endRow =r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if not piece_pinned or pin_direction == [d] or pin_direction == (-d[0], -d[1]):
                        obstaclePiece = self.board[endRow][endCol]
                        if obstaclePiece == '--': #if there are no obstacles,
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            '''this is still in the for loop, so the possible moves keep getting added'''
                        elif obstaclePiece[0] == enemyColor:
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break 
                            '''if there is an enemy obstacle piece. 
                            Add this final valid move where it gets to the enemy's square, a capture!
                            then break because you can't jump over pieces with a rook'''
                        else:
                            break
                            '''can't capture non-enemy pieces'''
                else:
                    break
                    '''stop adding new possible moves once it gets out of the board's range'''

    '''
    Get all the possible QUEEN moves
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Get all the possible KING moves
    '''
    def getKingMoves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.whiteKing = (end_row, end_col)
                    else:
                        self.blackKing = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.whiteKing = (r, c)
                    else:
                        self.blackKing = (r, c)

    #get valid castle moves for w/b king at r, c and add to move list
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #return nothing if in check
        
        #if not elif statements will be used as both king and queenside castle moves are possible simultaneously

        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            #if white to move and wks is castle-able or if b to move and bks is castle-able, get kingside castle moves
            self.getKingSideCastleMoves(r, c, moves)

        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            #if white to move and wks is castle-able or if b to move and bks is castle-able, get kingside castle moves
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        #check two square at the right of the king (kingside) - has to be empty
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove = True))

        
    def getQueenSideCastleMoves(self, r, c, moves):
        #three squares to the left must be checked, as the (r, c-3) will occupy the rook movement
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove = True))

'''----------------------------------------------------------------'''

class CastleRights():
    def __init__(self, wks, wqs, bks, bqs):
        #whitekingside, whitequeenside
        self.wks = wks
        self.wqs = wqs
        #blackkingside, blackqueenside
        self.bks = bks
        self.bqs = bqs



#----------------------------------------------------------------

class Move():

    #follows chess notation
    ranksToRows = {"1": 7, "2":6, "3":5, "4": 4, 
                    "5":3, "6":2, "7":1, "8":0}
    '''
    This is DICT Comprehension. rankToRows.items() returns the values 
    of the dictionary, like [("1",7), ("2":6)...] in an iterable form
    k and v can be renamed, but K represents keys and v values.
    Thus in the first iteration, k would be "1" and v is 7, dict Comprehension
    simplifies this process. It instantly makes a dictionary
    that has the format v:k over every iteration, so rowsToRanks.items()
    would contain like [(7, "1"), (6, "2")...] 
    '''
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, 
                    "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startsq, endsq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startsq[0]
        self.startCol = startsq[1]

        self.endRow = endsq[0]
        self.endCol = endsq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7): #pawn promotion
            self.isPawnPromotion = True
        self.promotionPiece = ''
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            # print(self.isEnPassantMove)
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCastleMove = isCastleMove

        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        # print(self.moveID)
        #between 0 and 7777
    '''
    overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getRankFile(self, row, column):
        return self.colsToFiles[column] + self.rowsToRanks[row] #it's f3 not 3f

    def getChessNotation(self):
        #PGN NOTATION 
        #Abnormal Moves
        if self.isPawnPromotion:
            notatedMove = self.getRankFile(self.endRow, self.endCol) + '=' + self.promotionPiece
            return notatedMove
        if self.isCastleMove:
            if self.endCol == 1: #queenside castled kings are in column 1
                notatedMove = 'O-O-O'
                return notatedMove
            else:
                notatedMove = 'O-O'
                return notatedMove
        if self.isEnPassantMove:
            notatedMove = self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow, self.endCol)
            return notatedMove
        #----------------------------------------------------------------
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                notatedMove = self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow, self.endCol)
                return notatedMove
            else:
                notatedMove = self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
                return notatedMove
        else:
            if self.pieceMoved[1] == "p":
                notatedMove = self.getRankFile(self.endRow, self.endCol)
                return notatedMove
            elif self.pieceMoved[1] == "K":
                if self.startCol == 4 and self.endCol == 2:
                    notatedMove = 'O-O-O'
                    return notatedMove
                elif self.startCol == 4 and self.endCol == 6:
                    notatedMove = 'O-O'
                    return notatedMove
                else:
                    notatedMove = self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)
                    return notatedMove
            else:
                notatedMove = self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)
                return notatedMove
        
        #TODO don't get kingmoves confused with castlemoves
        #TODO what happens in a stalemate (draw) and a checkmate and notation
        #TODO disambiguating moves - if a two pieces in distinct columns can move to a certain square, do Piece-column-endSquare