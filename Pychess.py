#!/usr/bin/env pypy3

#https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
# userfule resource ^^^
import chess as ch, time as tm

DEPTH = int(input("Depth? around 3 recommended -"))
FEN = (
"r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0"
)

# test positions
'''
ch.STARTING_FEN
"rnbqkbn1/ppppp3/7r/6pp/3P1p2/3BP1B1/PPP2PPP/RN1QK1NR w - - 1 0"
"r1b1k2r/ppQ1q2n/2p2p2/P3p2p/N3P1pP/1B4P1/1PP2P2/3R1NK1 w - - 1 0"
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

def stress_testing():
    with open("TestPositions.txt") as file:
        for i in (file.readlines()):
            CHESS_BOARD = ch.Board(fen = i[1:-2])
            score = negamax(DEPTH, CHESS_BOARD)
            if score[0] < 1e9:
                print("FAILED:", i)
            else:
                print("ACCEPTED:", i)

def testing():
    while True:
        # timer, to show the time spent thinking
        time1 = tm.perf_counter()
        # get the best move at a certain depth
        score = negamax(DEPTH, CHESS_BOARD)
        # push (play) the best move that we found
        CHESS_BOARD.push(score[1])
        # print some useful debug info
        print(f"Best Move: {score[1]} Engine_Eval: {score[0]} Transposition Table Size: {len(tt)}")
        print(f"Depth {DEPTH}: took {tm.perf_counter() - time1:0.2f} seconds")
        # print the chess board
        print(CHESS_BOARD, sep = "", end = "\n")
        print(" ".join(list(map(lambda x: str(x), list(CHESS_BOARD.move_stack)))))
        print(f"fen: {CHESS_BOARD.fen()}")
        while True:
            # input validation, because humans mess up
            try:
                dmmm = input("Enter your Move here: (uci format, you play as black): ")
                if len(dmmm) < 4: CHESS_BOARD.push_san(dmmm); break
                else: CHESS_BOARD.push_uci(dmmm); break
            except Exception as Error: print(Error)

def negamax(depth: int, position: ch.Board):
    # the player variable was kinda useless
    global depth_mate
    # depth mate ensures we choose the fastest way to checkmate
    # the opponent, if we dont then we may get stuck in a loop and
    # end up in threefold repetition  
    moves = list(position.legal_moves)
    best_evaluation = float("-inf")
    for i in range(len(moves)):
        # play a move
        position.push(moves[i])
        depth_mate = DEPTH * 1000
        # how good is that move?
        child_eval = search(depth - 1, False, position, float("-inf"), float("inf"))
        # FIXME TESTING
        # print("\033c", moves[i], child_eval)
        # undo the move to try the next one
        position.pop()
        # if it is a mate move, then we save it
        if child_eval == 1e9:
            child_eval *= depth_mate
            # debugging
            # print(f"Mate: {moves[i]} {child_eval} {(depth_mate)}")
        # if it is a good move, then we save it
        if child_eval >= best_evaluation:
            best_move = moves[i]
            best_evaluation = child_eval
        # if found mate in 1, 2, 3, etc play move
        # only when in middle game, turn off in late game
    return best_evaluation, best_move

def search(depth: int, max_player: bool, position: ch.Board, alpha, beta):
    # this function is basically the same as the negamax one, however
    # it searches both blakc and white moves 
    global depth_mate
    depth_mate -= 1 # increment the depth mate
    moves = list(position.legal_moves)
    if depth < 1 or len(moves) == 0:
        # if max player means if computer is to move
        return int(evaluate(position, max_player))
    if max_player:
        # maximizing player - (white to play)
        best_evaluation = float("-inf")
        for i in range(len(moves)):
            position.push(moves[i])
            child_eval = search(depth - 1, False, position, alpha, beta)
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
            child_eval = search(depth - 1, True, position, alpha, beta)
            position.pop()
            best_evaluation = min(best_evaluation, child_eval)
            beta = min(beta, best_evaluation)
            if beta <= alpha:
                break
        return best_evaluation

def evaluate(position: ch.Board, player: bool) -> int:
    # global the transposition table
    global tt
    # list score to zero
    score = 0
    try: return tt[position.board_fen()]
    except: pass
    # check for some overriding factors to the position
    # by that I mean it doesn't matter if we lose a queen
    # if we can checkmate the opponent
    if position.is_checkmate(): return -1e9 if player else 1e9
    if position.is_stalemate(): return 0
    # not sure which one is better
    # option 1
    score += sum([int.bit_count(position.attackers_mask(color=ch.WHITE, square=i)) for i in range(64)])
    # option 2
    for i in range(64): score += int.bit_count(position.attacks_mask(square=i))
    # count the pieces
    score += int.bit_count(position.attacks_mask(square=i)) + int.bit_count(position.pieces_mask(piece_type=ch.QUEEN, color=ch.BLACK)) * -900 + int.bit_count(position.pieces_mask(piece_type=ch.ROOK, color=ch.BLACK)) * -450 + int.bit_count(position.pieces_mask(piece_type=ch.BISHOP, color=ch.BLACK)) * -330 + int.bit_count(position.pieces_mask(piece_type=ch.KNIGHT, color=ch.BLACK)) * -320 + int.bit_count(position.pieces_mask(piece_type=ch.PAWN, color=ch.BLACK)) * -100 + int.bit_count(position.pieces_mask(piece_type=ch.QUEEN, color=ch.WHITE)) * 900 + int.bit_count(position.pieces_mask(piece_type=ch.ROOK, color=ch.WHITE)) * 450 + int.bit_count(position.pieces_mask(piece_type=ch.BISHOP, color=ch.WHITE)) * 330 + int.bit_count(position.pieces_mask(piece_type=ch.KNIGHT, color=ch.WHITE)) * 320 + int.bit_count(position.pieces_mask(piece_type=ch.PAWN, color=ch.WHITE)) * 100
    tt[position.board_fen()] = score
    return score

#stress_testing()
testing()
