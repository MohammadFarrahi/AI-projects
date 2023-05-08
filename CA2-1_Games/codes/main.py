import pygame
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game import Game
from minimax.minimax import minimax

FPS = 15

WHITE_DEPTH = 5
RED_DEPTH = 5

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

def getRowColFromMouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

if __name__ == '__main__':
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        if game.turn == WHITE:
            value, newBoard = minimax(game.getBoard(), WHITE_DEPTH, True)
            if newBoard == None:
                game.changeTurn()
            game.aiMove(newBoard)

        if game.winner() != None:
            print(game.winner())
            run = False

        if game.turn == RED:
            value, newBoard = minimax(game.getBoard(), RED_DEPTH, False)
            if newBoard == None:
                game.changeTurn()
            game.aiMove(newBoard)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        game.update()
    
    pygame.quit()