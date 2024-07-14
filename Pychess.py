#!/usr/bin/env pypy3

import chess as ch, time as tm
MAX_DEPTH = 4

FEN = (
ch.STARTING_FEN
)

# testing positions
'''
"5K2/Q7/8/8/1N6/8/pppppppp/rnbqkbnr w - - 0 1"
"r1b1k2r/pp2b1pp/3pNn2/qNn5/B7/8/PPP2PPP/R1BQ2K1 w kq - 3 13"
"r1b2b1r/pp3Qp1/2nkn2p/3ppP1p/P1p5/1NP1NB2/1PP1PPR1/1K1R3q w - - 0 1"
"1rbqk2r/p3npbp/3pp1p1/2p5/1p1nP3/2PPB1P1/PP1Q1PBP/R1NN1RK1 w k - 0 12"
"r1b1k2r/ppQ1q2n/2p2p2/P3p2p/N3P1pP/1B4P1/1PP2P2/3R1NK1 w - - 1 0"
"8/8/5p1k/pp6/b1pN2PP/8/PP5K/8 w - - 1 37"
"3k4/1pppppp1/1PPPPPP1/4K3/8/8/8/8 w - - 0 1"
'''

CHESS_BOARD = ch.Board(fen = FEN)
player = True
tt = {}

def testing():
    global nodes
    try:
        while True:
            nodes = 0
            time1 = tm.perf_counter()
            score = None
            for i in range(MAX_DEPTH):
                try:
                    nodes = 0
                    #x = score[:]
                    score = list(map(lambda x:x[0], score))
                    #print(score)
                    #print(score)
                    score = minimax(i + 1, CHESS_BOARD, score, player)
                except Exception:
                    score = minimax(i + 1, CHESS_BOARD, list(CHESS_BOARD.legal_moves), player)
                    #print(score)
            if player:
                CHESS_BOARD.push(score[0][0])
            else:
                CHESS_BOARD.push(score[-1][0])
            print(f"Best_move: {score[0][0]} Eval: {score[0][1]}")
            print(f"At MAX_DEPTH {MAX_DEPTH}: took {tm.perf_counter() - time1:0.4f}s")
            print(f"searched a total of {nodes} nodes : Transposition Table Size: {len(tt)}")
            print(CHESS_BOARD, sep = "", end = "\n")
            while True:
                try:
                    dmmm = input()
                    if dmmm == "quit":
                        a = " ".join(list(map(lambda x: str(x), list(CHESS_BOARD.move_stack))))
                        print(a)
                        return
                    if len(dmmm) < 4: CHESS_BOARD.push_san(dmmm)
                    else: CHESS_BOARD.push_uci(dmmm)
                    break
                except Exception as E: print(E)
    except Exception as Error:
        print(Error)
        a = " ".join(list(map(lambda x: str(x), list(CHESS_BOARD.move_stack))))
        print(a)

def minimax(depth: int, position: ch.Board, moves: list, player: bool) -> list:
    global mate_depth, ac, bc; nm = []
    best_evaluation = -1e9
    for i in range(len(moves)):
        ac, bc = 0, 0
        position.push((moves[i]))
        mate_depth = 0
        child_eval = int(ab(depth - 1, not player, position, -abs(len(position.move_stack)*5-100), abs(len(position.move_stack)*5-100), list((position).legal_moves)))
        position.pop()

        if child_eval >> 26 and child_eval > 0:
            nm.append((moves[i], child_eval))
            return sorted(nm, key=lambda x: x[1], reverse=True)
        nm.append((moves[i], child_eval))
        if child_eval >= best_evaluation:
            best_evaluation = (child_eval)
    return sorted(nm, key=lambda x: x[1], reverse=True)

def ab(depth: int, max_player: bool, position: ch.Board, alpha, beta, moves: list) -> int:
    global mate_depth, nodes, ac, bc
    mate_depth += 1
    if depth == 0 or len(moves) == 0:
        nodes += 1
        # if max player means if computer is to move
        return int(evaluate(position, max_player))
    if max_player:
        # maximizing player - (white to play)
        best_evaluation = -1e9
        for i in range(len(moves)):
            if position.is_capture(moves[i]) or position.is_check():
                position.push(moves[i])
                child_eval = int(ab(depth - 1, False, position, alpha, beta, list((position).legal_moves)))
                position.pop()
                if child_eval >= best_evaluation:
                    best_evaluation = (child_eval)
                alpha = max(alpha, best_evaluation)
                ac = min(ac, alpha)
                if child_eval >= beta:
                    break
        return best_evaluation
    else:
        # Black to play
        best_evaluation = 1e9
        for i in range(len(moves)):
            position.push(moves[i])
            child_eval = (ab(depth - 1, True, position, alpha, beta, list((position).legal_moves)))
            position.pop()
            best_evaluation = min(best_evaluation, child_eval)
            beta = min(beta, best_evaluation)
            bc = max(bc, beta)
            if child_eval <= alpha:
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

if __name__ == "__main__":
    testing()
