# Chess Engine: Stores all info about current state of a chess game, stores the game log

class GameState():
    ''' Defines the board, an 8x8 2D list where each element is two characters -- represents an empty square '''
    def __init__(self):
        # Initial board setup
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "B": self.getBishopMoves, "N": self.getKnightMoves,"K": self.getKingMoves, "Q": self.getQueenMoves}
        self.whiteToMove = True  # True if white's turn, False if black's turn
        self.moveLog = []  # Log of all moves made in the game
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #coordinates of square where en passent is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        
        self.currentcastlerights = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentcastlerights.wks,self.currentcastlerights.bks,self.currentcastlerights.wqs,self.currentcastlerights.bqs)]


    def boardString(self):
        """
        Creates a string representation of the board.
        This string can be used as a unique identifier for the current board state.
        """
        boardStr = ""
        for row in self.board:
            for square in row:
                boardStr += square
        return boardStr + ("w" if self.whiteToMove else "b")


    # Update the game state with the given move
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"  # Clear the start square
        self.board[move.endRow][move.endCol] = move.pieceMoved  # Move the piece to the destination
        self.moveLog.append(move)  # Add the move to the move log
        self.whiteToMove = not self.whiteToMove  # Switch turns
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow,move.endCol)
        
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #en passant
        if move.isEnpassantmove:
            self.board[move.startRow][move.endCol] = "--" #pawn captured

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #only on two square pan advanced
            self.enpassantPossible = ((move.endRow + move.startRow)//2,move.endCol)
        else:
            self.enpassantPossible = ()

        #castle move 
        if move.iscastlemove:
            if move.endCol - move.startCol ==2: #kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else: # queensidde castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'
        
        self.enpassantPossibleLog.append(self.enpassantPossible)
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentcastlerights.wks,self.currentcastlerights.bks,self.currentcastlerights.wqs,self.currentcastlerights.bqs))




    def updateCastleRights(self,move):
        if move.pieceMoved == "wK":
            self.currentcastlerights.wks = False
            self.currentcastlerights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentcastlerights.bks = False
            self.currentcastlerights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentcastlerights.wqs  = False
                elif move.startCol == 7:
                    self.currentcastlerights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentcastlerights.bqs  = False
                elif move.startCol == 7:
                    self.currentcastlerights.bks = False
        
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentcastlerights.wqs = False
                elif move.endCol == 7:
                    self.currentcastlerights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentcastlerights.bqs = False
                elif move.endCol == 7:
                    self.currentcastlerights.bks = False

            


    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow,move.startCol)
            #undoing en passant
            if move.isEnpassantmove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow,move.endCol)
            #undo a 2 sqaure pawn advance
            if move.pieceMoved[1] =="p" and abs(move.startRow-move.endRow)==2:
                self.enpassantPossible = ()
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            #undo castle rights 
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentcastlerights = CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)
            #undo castle move 
            if move.iscastlemove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1]= self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2]= self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            self.checkmate = False
            self.stalemage = False


            
    def getValidMoves(self):
        tempEnpassantPossilbe = self.enpassantPossible
        tempCastlerights = CastleRights(self.currentcastlerights.wks,self.currentcastlerights.bks,self.currentcastlerights.wqs,self.currentcastlerights.bqs)
        moves = self.getAllMoves()
        #make each move 
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        for i in range (len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves)==0:
            if self.inCheck:
                self.checkmate = True
                self.stalemate = False
            else:
                self.stalemate = True
                self.checkmate = False

        self.enpassantPossible = tempEnpassantPossilbe
        self.currentcastlerights = tempCastlerights
        return moves

        
    #determine if current player is in check    
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else: 
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    


    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow ==r and move.endCol == c:
                return True
        return False 
                


    
    # all moves not considering checks
    def getAllMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])): 
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn =='b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) #calls move functions 
        return moves 


    def getPawnMoves(self,r,c,moves):
        #missing en passent and promotion
        if self.whiteToMove:
            if self.board[r-1][c] == "--": #square infront is empty
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--": #on first square and can move up 2
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >=0:
                if self.board[r-1][c-1][0] == "b": #black piece is there
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnpassantmove=True))

            if c+1 <=7:
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnpassantmove=True))

        
        else: #black to move
            if self.board[r+1][c] == "--": #square infront is empty
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--": #on first square and can move up 2
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >=0:
                if self.board[r+1][c-1][0] == "w": #white piece is there
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnpassantmove=True))

            if c+1 <=7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantmove=True))

             
    def getRookMoves(self, r, c, moves):
        if self.whiteToMove: 
            # Moving up the board (increasing rows)
            i = r
            while i < 7:  # Loop until the edge of the board
                if self.board[i+1][c] == "--":
                    moves.append(Move((r, c), (i+1, c), self.board))
                elif self.board[i+1][c][0] == "b":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (i+1, c), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                i += 1

            # Moving down the board (decreasing rows)
            i = r
            while i > 0:
                if self.board[i-1][c] == "--":
                    moves.append(Move((r, c), (i-1, c), self.board))
                elif self.board[i-1][c][0] == "b":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (i-1, c), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                i -= 1

            # Moving right across the board (increasing columns)
            j = c
            while j < 7:
                if self.board[r][j+1] == "--":
                    moves.append(Move((r, c), (r, j+1), self.board))
                elif self.board[r][j+1][0] == "b":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (r, j+1), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                j += 1

            # Moving left across the board (decreasing columns)
            j = c
            while j > 0:
                if self.board[r][j-1] == "--":
                    moves.append(Move((r, c), (r, j-1), self.board))
                elif self.board[r][j-1][0] == "b":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (r, j-1), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                j -= 1
        else: 
             # Moving up the board (increasing rows)
            i = r
            while i < 7:  # Loop until the edge of the board
                if self.board[i+1][c] == "--":
                    moves.append(Move((r, c), (i+1, c), self.board))
                elif self.board[i+1][c][0] == "w":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (i+1, c), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                i += 1

            # Moving down the board (decreasing rows)
            i = r
            while i > 0:
                if self.board[i-1][c] == "--":
                    moves.append(Move((r, c), (i-1, c), self.board))
                elif self.board[i-1][c][0] == "w":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (i-1, c), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                i -= 1

            # Moving right across the board (increasing columns)
            j = c
            while j < 7:
                if self.board[r][j+1] == "--":
                    moves.append(Move((r, c), (r, j+1), self.board))
                elif self.board[r][j+1][0] == "w":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (r, j+1), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                j += 1

            # Moving left across the board (decreasing columns)
            j = c
            while j > 0:
                if self.board[r][j-1] == "--":
                    moves.append(Move((r, c), (r, j-1), self.board))
                elif self.board[r][j-1][0] == "w":  # If it's a black piece, capture it
                    moves.append(Move((r, c), (r, j-1), self.board))
                    break  # Stop after capturing
                else:  # Encounter your own piece, stop
                    break
                j -= 1

    def getKingMoves(self, r, c, moves):
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        ally_color = "w" if self.whiteToMove else "b"
        
        for move in king_moves:
            dr, dc = move
            new_r = r + dr
            new_c = c + dc
            
            # Check if the move is within board boundaries
            if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                piece = self.board[new_r][new_c]
                if piece == "--" or piece[0] != ally_color:  # Empty square or opponent's piece
                    moves.append(Move((r, c), (new_r, new_c), self.board))
        

    
    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return 
        if (self.whiteToMove and self.currentcastlerights.wks) or (not self.whiteToMove and self.currentcastlerights.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if(self.whiteToMove and self.currentcastlerights.wqs) or (not self.whiteToMove and self.currentcastlerights.bqs):
            self.getQueensideCastleMoves(r,c,moves)



    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,iscastlemove=True))


    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--": 
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,iscastlemove=True))





    def getBishopMoves(self, r, c, moves):
        ally_color = "w" if self.whiteToMove else "b"
        # Define all four diagonal directions (up-right, down-left, up-left, down-right)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in directions:
            dr, dc = d
            i, x = r + dr, c + dc
            
            while 0 <= i <= 7 and 0 <= x <= 7:  # Ensure the move stays within board boundaries
                if self.board[i][x] == "--":  # Empty square, valid move
                    moves.append(Move((r, c), (i, x), self.board))
                elif self.board[i][x][0] != ally_color:  # Opponent's piece, capture it
                    moves.append(Move((r, c), (i, x), self.board))
                    break  # Stop after capturing
                else:  # Own piece, stop
                    break
                
                # Continue moving in the current direction
                i += dr
                x += dc

    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)


    def getKnightMoves(self,r,c,moves):
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        ally_color = "w" if self.whiteToMove else "b"
        
        for move in knight_moves:
            dr, dc = move
            new_r = r + dr
            new_c = c + dc
            
            # Check if the move is within board boundaries
            if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                piece = self.board[new_r][new_c]
                if piece == "--" or piece[0] != ally_color:  # Empty square or opponent's piece
                    moves.append(Move((r, c), (new_r, new_c), self.board))
        
class CastleRights():

    def __init__(self, wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.bqs = bqs
        self.wqs = wqs



# Move class handles chess notation and translating moves
class Move():

    # Fixed column mapping for correct file-to-column translation
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}  # Fixed mapping
    colsToFiles = {v: k for k, v in filesToCol.items()}

    def __init__(self, startSq, endSq, board, isEnpassantmove=False, iscastlemove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
    
        self.isPawnPromotion =  (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved=="bp" and self.endRow == 7)  
        #en passent
        self.isEnpassantmove = isEnpassantmove
        if self.isEnpassantmove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.iscastlemove = iscastlemove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        

    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID



    # Return the move in standard chess notation
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    # Helper function to get the rank and file from row and column
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]