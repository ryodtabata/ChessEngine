import pygame as p
import ChessEngine,SmartMoveFinder

# Constants for game dimensions and FPS
WIDTH = 500
BOARD_HEIGHT = 500  # Height of the chessboard itself
TOP_PADDING = 100   # Whitespace at the top
HEIGHT = BOARD_HEIGHT + TOP_PADDING  # Total height including padding
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
BORDER_WIDTH = 5  # Thickness of the border
MAX_FPS = 15  # Animations FPS rate
images = {}



# Load images for pieces and handle errors if files are missing
def loadImages():
    pieces = ['wp', 'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for i in pieces:
        try:
            images[i] = p.image.load("images/" + i + ".png")
        except FileNotFoundError:
            print(f"Error: Image {i}.png not found.")
    try:
        images['avatar'] = p.image.load("images/avatar.png")
    except FileNotFoundError:
        print("Error: Image avatar.png not found.")

'''
Main driver, takes in user input and handles game state updates
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()  # Create the initial game state
    validMoves = gs.getValidMoves()
    moveMade = False  # flag var if move is made 
    gameOver = False
    playertwo = False  # Black player (AI or human)
    playerone = True # White player (human or AI)
    loadImages()  # Load the chess piece images
    running = True
    sqSelected = ()  # Correct initialization of an empty tuple to track the selected square
    playerClicks = []  # List to store player clicks for move selection

    while running:
        humanTurn = (gs.whiteToMove and playerone) or (not gs.whiteToMove and playertwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # Get mouse click location
                    col = location[0] // SQ_SIZE
                    row = (location[1] - TOP_PADDING) // SQ_SIZE  # Adjust for top padding

                    if row < 0:  # Ignore clicks in the padding area
                        continue

                    # Handle selecting and deselecting the same square
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    # When two squares have been clicked, attempt to make a move
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())  # For debugging purposes, prints the move
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])  # Update game state with the new move
                                moveMade = True
                                sqSelected = ()  # Reset selected square
                                playerClicks = []  # Clear player clicks after the move
                        if not moveMade:
                            playerClicks = [sqSelected]

            if e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if len(gs.moveLog) > 0:  # Check if there are moves to undo
                        if gs.whiteToMove == playerone:  # Only undo if it's the player's move
                            gs.undoMove()  # Undo the player's move
                            moveMade = True
                            # Optionally undo AI move too, if you want to revert the entire last move cycle
                            if not gs.whiteToMove == playerone and len(gs.moveLog) > 0:
                                gs.undoMove()
                                moveMade = True
                if e.key == p.K_r:  # Reset game when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False


        # AI move here
        if not gameOver and not humanTurn:
            AImove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AImove is None:
                AImove = SmartMoveFinder.findBestMove(gs,validMoves)
            gs.makeMove(AImove)
            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)  # Draw the current state of the game

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate!")
            else:
                drawText(screen, "White wins by checkmate!")

        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Draw by Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


# Highlights selected piece and possible moves
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparent
            s.fill(p.Color('yellow'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE + TOP_PADDING))
            # Highlight moves
            s.fill(p.Color('blue'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE + TOP_PADDING))

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

# Draw the entire game state
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # Draw the chess pieces on the board
    drawBorder(screen)  # Draw the border around the board
    drawAvatar(screen)  # Draw the avatar image

# Draw the chessboard
def drawBoard(screen):
    colours = [p.Color("white"), p.Color("gray")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[(r + c) % 2]  # Alternate between two colors
            p.draw.rect(screen, colour, p.Rect(c * SQ_SIZE, r * SQ_SIZE + TOP_PADDING, SQ_SIZE, SQ_SIZE))

# Draw the pieces on the chessboard based on the board state
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Ensure there's a piece on the square
                screen.blit(images[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE + TOP_PADDING, SQ_SIZE, SQ_SIZE))

# Draw the black border around the chessboard
def drawBorder(screen):
    border_rect = p.Rect(0, TOP_PADDING, WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, p.Color("black"), border_rect, BORDER_WIDTH)

# Draw the avatar in the top left corner
def drawAvatar(screen):
    if 'avatar' in images:
        # Define avatar dimensions and position
        avatar_width, avatar_height = 80, 80
        avatar_x, avatar_y = 10, 10
        
        # Draw the avatar
        avatar_rect = p.Rect(-178, -165, avatar_width, avatar_height)
        screen.blit(images['avatar'], avatar_rect)
        
        # Define text properties
        font = p.font.SysFont("Arial", 16, False, False)
        font2 = p.font.SysFont("Arial", 10, False, False)
        name_text = font.render("GM Ryo Tabata", True, p.Color("black"))
        elo_text = font2.render("Elo 1750", False, p.Color("black"))

        # Positioning of the text
        name_x = 150
        name_y = 20
        elo_x = name_x
        elo_y = name_y + name_text.get_height() + 5  # 5 pixels gap between name and Elo text

        # Draw the text
        screen.blit(name_text, (name_x, name_y))
        screen.blit(elo_text, (elo_x, elo_y))
    else:
        print("Avatar image not found in images dictionary.")


if __name__ == '__main__':
    main()
