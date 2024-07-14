#!/usr/bin/env pypy3

#https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
# userfule resource ^^^
import chess as ch, time as tm

DEPTH = int(input())
FEN = (
"rnbqkbn1/ppppp3/7r/6pp/3P1p2/3BP1B1/PPP2PPP/RN1QK1NR w - - 1 0"
)

# test positions
'''
"r1b1k2r/ppQ1q2n/2p2p2/P3p2p/N3P1pP/1B4P1/1PP2P2/3R1NK1 w - - 1 0"
ch.STARTING_FEN
"5K2/Q7/8/8/1N6/8/pppppppp/rnbqkbnr w - - 0 1"
"r1b2b1r/pp3Qp1/2nkn2p/3ppP1p/P1p5/1NP1NB2/1PP1PPR1/1K1R3q w - - 0 1"
"r1b1k2r/pp2b1pp/3pNn2/qNn5/B7/8/PPP2PPP/R1BQ2K1 w kq - 3 13"
"1rbqk2r/p3npbp/3pp1p1/2p5/1p1nP3/2PPB1P1/PP1Q1PBP/R1NN1RK1 w k - 0 12"
"3k4/1pppppp1/1PPPPPP1/4K3/8/8/8/8 w - - 0 1"
"8/8/5p1k/pp6/b1pN2PP/8/PP5K/8 w - - 1 37"
'''

best_move = None
CHESS_BOARD = ch.Board(fen=FEN)
tt = {}

def testing():
    while True:
        time1 = tm.perf_counter()
        score = negamax(DEPTH, CHESS_BOARD)
        CHESS_BOARD.push(score[1])
        print(f"Best Move: {score[1]} Engine_Eval: {score[0]} Transposition Table Size: {len(tt)}")
        print(f"Depth {DEPTH}: took {tm.perf_counter() - time1:0.2f} seconds")
        print(CHESS_BOARD, sep = "", end = "\n")
        print(" ".join(list(map(lambda x: str(x), list(CHESS_BOARD.move_stack)))))
        print(f"fen: {CHESS_BOARD.fen()}")
        while True:
            try:
                dmmm = input()
                if len(dmmm) < 4: CHESS_BOARD.push_san(dmmm); break
                else: CHESS_BOARD.push_uci(dmmm); break
            except Exception as Error: print(Error)

def negamax(depth: int, position: ch.Board):
    global depth_mate
    moves = list(position.legal_moves)
    best_evaluation = float("-inf")
    for i in range(len(moves)):
        position.push(moves[i])
        depth_mate = DEPTH * 1000
        child_eval = int(search(depth - 1, False, position, float("-inf"), float("inf")))
        print("\033c", moves[i], child_eval)
        position.pop()
        if child_eval == 1e9:
            child_eval *= depth_mate
            print(f"Mate: {moves[i]} {child_eval} {(depth_mate)}")
        if child_eval >= best_evaluation:
            best_move = moves[i]
            best_evaluation = child_eval
        # if found mate in 1, 2, 3, etc play move
        # only when in middle game, turn off in late game
    return best_evaluation, best_move

def search(depth: int, max_player: bool, position: ch.Board, alpha, beta):
    global depth_mate
    depth_mate -= 1
    moves = list((position).legal_moves)
    if depth < 1 or len(moves) == 0:
        # if max player means if computer is to move
        return int(evaluate(position, max_player))
    if max_player:
        # maximizing player - (white to play)
        best_evaluation = float("-inf")
        for i in range(len(moves)):
            position.push(moves[i])
            child_eval = int(search(depth - 1, False, position, alpha, beta))
            position.pop()
            if child_eval >= best_evaluation:
                best_evaluation = (child_eval)
            alpha = max(alpha, best_evaluation)
            if beta <= alpha:
                break
        return best_evaluation
    else:
        # Black to play
        best_evaluation = float("inf")
        for i in range(len(moves)):
            position.push(moves[i])
            child_eval = int(search(depth - 1, True, position, alpha, beta))
            position.pop()
            best_evaluation = min(best_evaluation, child_eval)
            beta = min(beta, best_evaluation)
            if beta <= alpha:
                break
        return best_evaluation

def evaluate(position: ch.Board, player: bool) -> int:
    global tt
    score = 0
    try: return tt[position.board_fen()]
    except: pass
    if position.is_checkmate(): return -1e9 if player else 1e9
    if position.is_stalemate(): return 0
    # option 1
    score += sum([int.bit_count(position.attackers_mask(color=ch.WHITE, square=i)) for i in range(64)])
    # option 2
    for i in range(64): score += int.bit_count(position.attacks_mask(square=i))
    score += int.bit_count(position.attacks_mask(square=i)) + int.bit_count(position.pieces_mask(piece_type=ch.QUEEN, color=ch.BLACK)) * -900 + int.bit_count(position.pieces_mask(piece_type=ch.ROOK, color=ch.BLACK)) * -450 + int.bit_count(position.pieces_mask(piece_type=ch.BISHOP, color=ch.BLACK)) * -330 + int.bit_count(position.pieces_mask(piece_type=ch.KNIGHT, color=ch.BLACK)) * -320 + int.bit_count(position.pieces_mask(piece_type=ch.PAWN, color=ch.BLACK)) * -100 + int.bit_count(position.pieces_mask(piece_type=ch.QUEEN, color=ch.WHITE)) * 900 + int.bit_count(position.pieces_mask(piece_type=ch.ROOK, color=ch.WHITE)) * 450 + int.bit_count(position.pieces_mask(piece_type=ch.BISHOP, color=ch.WHITE)) * 330 + int.bit_count(position.pieces_mask(piece_type=ch.KNIGHT, color=ch.WHITE)) * 320 + int.bit_count(position.pieces_mask(piece_type=ch.PAWN, color=ch.WHITE)) * 100
    tt[position.board_fen()] = score
    return score

testing()
