from copy import deepcopy
import pygame

RED = (255,0,0)
WHITE = (255,255,255)
MAX = float('inf')
MIN = float('-inf')

def minimax(board, depth, maxPlayer):
    if depth == 0 or board.winner() != None:
        return board.evaluate(), board
    
    best_move = None
    if maxPlayer:
        max_eval = MIN
        for child_board in getAllMoves(board, WHITE):
            evaluation = minimax(child_board, depth-1, False)[0]
            max_eval = max(max_eval, evaluation)
            if max_eval == evaluation:
                best_move = child_board
        return max_eval, best_move
    else:
        min_eval = MAX
        for child_board in getAllMoves(board, RED):
            evaluation = minimax(child_board, depth-1, True)[0]
            min_eval = min(min_eval, evaluation)
            if min_eval == evaluation:
                best_move = child_board
        return min_eval, best_move

def simulateMove(piece, move, board, skip):
    board.move(piece, move[0], move[1])
    if len(skip) != 0:
        board.remove(skip)
    return board

def getAllMoves(board, color):
    child_boards = []
    for piece in board.getAllPieces(color):
        valid_moves = board.getValidMoves(piece)
        for move, skipped in valid_moves.items():
            child_board = deepcopy(board)
            piece_to_move = child_board.getPiece(piece.row, piece.col)
            child_board = simulateMove(piece_to_move, move, child_board, skipped)
            child_boards.append(child_board)
    return child_boards