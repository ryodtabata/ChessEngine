import random

pieceScore = {"K":0,"R": 5, "Q": 9, "B":3, "N":3, "p":1 }

#Scores for gameplay
CHECKMATE = 1000
STALEMATE = 0

#depth of search, >3 becomes quite slow
DEPTH = 3

#piece-square position tables, indicating which squares for which peices are most positionally advantageous
knightScore = [[1,1,1,1,1,1,1,1],
               [1,2,2,2,2,2,2,1],
               [1,3,3,3,3,3,2,1],
               [1,3,3,4,4,3,2,1],
               [1,3,3,4,4,3,2,1],
               [1,3,3,3,3,3,2,1],
               [1,2,2,2,2,2,2,1],
               [1,1,1,1,1,1,1,1]]

bishopScore = [[4,0,0,0,0,0,0,4],
               [3,4,2,2,2,2,4,3],
               [1,3,4,3,3,4,2,1],
               [1,3,4,4,4,4,2,1],
               [1,3,3,4,4,3,2,1],
               [1,3,4,3,3,4,3,1],
               [1,4,2,2,2,2,4,3],
               [4,0,0,0,0,0,0,4]]

rookScore = [[1,1,4,4,4,3,2,1],
               [1,2,2,2,2,2,2,1],
               [1,2,2,2,2,2,2,1],
               [1,2,2,2,2,2,2,3],
               [1,2,2,2,2,2,2,1],
               [1,3,3,3,3,3,2,3],
               [2,2,2,2,2,2,2,2],
               [1,1,4,4,4,4,2,1]]

KingScore = [[1,1,4,4,4,3,2,1],
               [1,2,2,2,2,2,2,1],
               [1,2,2,2,2,2,2,1],
               [1,2,2,2,2,2,2,3],
               [1,2,2,2,2,2,2,1],
               [1,3,3,3,3,3,2,3],
               [2,2,2,2,2,2,2,2],
               [1,4,4,4,4,4,5,5]]

QueenScore = [[1,1,4,4,4,3,2,1],
               [1,4,4,4,2,2,2,1],
               [1,4,4,2,2,2,2,1],
               [1,4,4,5,5,2,2,3],
               [1,4,4,5,5,3,3,1],
               [1,4,4,3,3,3,2,3],
               [2,2,3,3,3,3,3,2],
               [1,1,2,2,2,2,2,1]]

pawnScore = [[10,10,10,10,10,10,10,10],
               [2,2,2,2,2,2,2,2],
               [3,3,3,3,3,3,3,3],
               [4,4,4,6,6,4,4,4],
               [4,4,4,6,6,4,4,3],
               [1,3,3,3,3,3,3,3],
               [2,2,2,2,2,2,2,2],
               [10,10,10,10,10,10,10,10]]


piecePositionScores = {"N": knightScore, "K": KingScore, "B": bishopScore,"p": pawnScore, "R": rookScore, "Q":QueenScore  }

# random move mostly for testing
def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]


def findBestMove(gs, validMoves):
    global nextMove 
    nextMove = None
    # shuffle rooms so it does not constantly play the same moves 
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs,validMoves,DEPTH,-CHECKMATE,CHECKMATE, 1 if gs.whiteToMove else -1)
    # findMoveNegaMax(gs,validMoves,DEPTH, 1 if gs.whiteToMove else -1)
    return nextMove


def findMoveNegaMaxAlphaBeta(gs,validMoves,depth, alpha,beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs,nextMoves,depth-1,-beta,-alpha,-turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >=beta:
            break

    return maxScore





# Pos number means whites winning, negative means black is winning 
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    piecePositionScore = 0
                    if square[1] != "K":
                        piecePositionScore = piecePositionScores[square[1]][row][col] *.1
                        #score position
                    if square[0] == 'w':
                        score += pieceScore[square[1]] + piecePositionScore
                    elif square[0] == 'b':
                        score -= pieceScore[square[1]] + piecePositionScore
    return score


#score board based on material 
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score