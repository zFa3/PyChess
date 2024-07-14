#!usr/bin/env pypy 3
import chess as ch
import time as tm

# simple chess engine in Python

# only plays as white
player = True # White goes first
FEN = (ch.STARTING_FEN)
# FEN = "r1b2b1r/pp3Qp1/2nkn2p/3ppP1p/P1p5/1NP1NB2/1PP1PPR1/1K1R3q w - - 0 1"
chess_board = ch.Board(fen = FEN)
tt = {} # transposition table, stores old positions
# depth is how far deep the game tree it searches
DEPTH = 3
nodes = 0

def search(depth: int, position: ch.Board, player: bool, alpha: float, beta: float, moves: list) -> ch.Move:
    if not depth:
        return evaluate(position)
    for i in moves:
        position.push(i)
        search(depth - 1, position, not player, alpha, beta, position.legal_moves)
        position.pop()

def negamax(position: ch.Board):
    # best move's eval, notation (in uci)
    best_move = [-1e9, None]
    search(3, position, not player, -1e9, 1e9, position.legal_moves)


def evaluate(position: ch.Board):
    global nodes; nodes += 1; return
    score = 0
    try: return tt[position.board_fen()]
    except: pass
    if position.is_checkmate():
        if player: return -1e9
        else: return 1e9
    if position.is_stalemate():
        return 0

negamax(chess_board)
print(nodes)
