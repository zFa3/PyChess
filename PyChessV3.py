#!/usr/bin/env pypy3
import chess as ch, time as tm

# DEPTH = int(input("Depth? around 3 recommended -"))
DEPTH = 5
FEN = (
ch.STARTING_FEN
)
# test positions
'''
FEN = "r1b1kb1r/pppp1ppp/5q2/4n3/3KP3/2N3PN/PPP4P/R1BQ1B1R b kq - 0 1"
FEN = "r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0"
FEN = "rnbqkbn1/ppppp3/7r/6pp/3P1p2/3BP1B1/PPP2PPP/RN1QK1NR w - - 1 0"
FEN = "r1b1k2r/ppQ1q2n/2p2p2/P3p2p/N3P1pP/1B4P1/1PP2P2/3R1NK1 w - - 1 0"
FEN = "5K2/Q7/8/8/1N6/8/pppppppp/rnbqkbnr w - - 0 1"
FEN = "r1b2b1r/pp3Qp1/2nkn2p/3ppP1p/P1p5/1NP1NB2/1PP1PPR1/1K1R3q w - - 0 1"
FEN = "r1b1k2r/pp2b1pp/3pNn2/qNn5/B7/8/PPP2PPP/R1BQ2K1 w kq - 3 13"
FEN = "1rbqk2r/p3npbp/3pp1p1/2p5/1p1nP3/2PPB1P1/PP1Q1PBP/R1NN1RK1 w k - 0 12"
FEN = "3k4/1pppppp1/1PPPPPP1/4K3/8/8/8/8 w - - 0 1"
FEN = "8/8/5p1k/pp6/b1pN2PP/8/PP5K/8 w - - 1 37"
FEN = "r6r/pp2kppp/8/1qp2p2/5P2/4B2P/PP4P1/3RR1K1 w - - 0 19"
FEN = "1Q6/6b1/3p2kp/3Pp3/4P3/r2p3b/3B1Pp1/4K1R1 b - - 0 38"
'''
FEN = "1kb5/4N3/3q4/1B6/4p3/1P2P2P/1B6/1K6 w - - 0 1"

best_move = None
CHESS_BOARD = ch.Board(fen=FEN)
tt = {}
attackingWeight = 1
clear = False
moveSort = True
inf = 1e9

def testing():
    while True:
        # timer, to show the time spent thinking
        nodes = perft(CHESS_BOARD, DEPTH)
        time1 = tm.perf_counter()
        # get the best move at a certain depth
        score = negamax(DEPTH, CHESS_BOARD)
        # push (play) the best move that we found
        CHESS_BOARD.push(score[1])
        # print some useful debug info
        print(f"Best Move: {score[1]} Engine_Eval: {score[0]} Transposition Table Size: {len(tt)}")
        print(f"Depth {DEPTH}: took {tm.perf_counter() - time1:0.5f} seconds")
        print(f"Depth {DEPTH}: total nodes available {nodes} - total nodes searched {nodes - len(tt)}")
        # print the chess board
        print(CHESS_BOARD, sep = "", end = "\n")
        print(" ".join(list(map(lambda x: str(x), list(CHESS_BOARD.move_stack)))))
        print(f"fen: {CHESS_BOARD.fen()}")
        while True:
            try:
                inpt = input("Enter your Move here: (uci format, you play as black): ")
                if len(inpt) < 4: CHESS_BOARD.push_san(inpt); break
                else: CHESS_BOARD.push_uci(inpt); break
            except Exception as Error: print(Error)

def mvv_lva(position: ch.Board, move: ch.Move):
    # Calculate the MVV-LVA value for a given move
    piece_value = {
        "k": 0, "q": 4, "r": 3, "b": 2, "n": 1, "p": 0,  # Black pieces
        "K": 0, "Q": 4, "R": 3, "B": 2, "N": 1, "P": 0   # White pieces
    }
    
    # The piece that is being captured
    captured_piece = str(position.piece_at(move.to_square))
    if captured_piece is None:
        return piece_value[captured_piece.lower(), 0]
    
    # The value of the captured piece (Most Valuable Victim)
    victim_value = piece_value.get(captured_piece.lower(), 0)

    # The piece that is doing the capturing
    attacking_piece = str(position.piece_at(move.from_square))
    attacker_value = piece_value.get(attacking_piece.lower(), 0)

    # Combine the values into a single score (MVV-LVA)
    return victim_value - attacker_value

def negamax(depth: int, position: ch.Board):
    global depth_mate
    # depth mate ensures we choose the fastest way to checkmate
    # the opponent, if we dont then we may get stuck in a loop and
    # end up in threefold repetition  
    moves = list(position.legal_moves)
    # attacking sorting
    #moves = sorted(moves, key = lambda move: int.bit_count(int(position.attacks(find_piece_from(move)))))
    if moveSort:
        moves = sorted(moves, key = lambda move: mvv_lva(position, move))

    best_evaluation = -inf
    for i in moves:
        # play a move
        position.push(i)
        depth_mate = DEPTH * 1000
        # how good is that move?
        child_eval = search(depth - 1, False, position, -inf, inf)
        if clear: print("\033c")
        print(i, child_eval)
        # undo the move to try the next one
        position.pop()
        # if it is a mate move, then we save it
        if child_eval == 1e9:
            child_eval *= depth_mate
            # debugging
            print(f"Mate: {i} {child_eval} {(depth_mate)}")
        # if it is a good move, then we save it
        if child_eval >= best_evaluation:
            best_move = i
            best_evaluation = child_eval
        # if found mate in 1, 2, 3, etc play move
        # only when in middle game, turn off in late game
    return best_evaluation, best_move

def search(depth: int, max_player: bool, position: ch.Board, alpha, beta):
    # this function is basically the same as the negamax one, however
    # it searches both black and white moves 
    global depth_mate
    depth_mate -= 1 # increment the depth mate
    moves = list(position.legal_moves)
    if depth < 1 or len(moves) == 0:
        # if max player means if computer is to move
        return int(evaluate(position, max_player))
    if max_player:
        # maximizing player - (white to play)
        best_evaluation = -inf
        for i in moves:
            position.push(i)
            child_eval = search(depth - 1, False, position, alpha, beta)
            position.pop()
            # going with fail soft for the speed
            alpha = max(alpha, child_eval)
            if child_eval > best_evaluation:
                best_evaluation = child_eval
            # beta cutoff is the same as alpha cutoff but for white
            if best_evaluation >= beta:
                break # beta cutoff
        return best_evaluation
    else:
        # Black to play
        best_evaluation = inf
        for i in moves:
            position.push(i)
            child_eval = search(depth - 1, True, position, alpha, beta)
            position.pop()
            beta = min(beta, child_eval)
            if child_eval < best_evaluation:
                best_evaluation = child_eval
            if best_evaluation <= alpha:
                # alpha cutoff essentially means that the move is so
                # bad for black that he would never play it, theres already a
                # better move that was searched
                break # alpha cutoff
        return best_evaluation

def evaluate(position: ch.Board, player: bool) -> int:
    # global the transposition table
    global tt
    # list score to zero
    score = 0
    try: return tt[position._board_state()]
    except: pass
    # check for some overriding factors to the position
    # by that I mean: it doesn't matter if we lose a queen
    # if we can checkmate the opponent
    if position.is_checkmate(): return -1e9 if player else 1e9
    if position.fullmove_number > 25:
        if position.is_stalemate():
            return 0
    # count the amount of moves
    for i in range(64): score += int.bit_count(position.attacks_mask(square=i))
    # count the pieces
    score += int.bit_count(position.pieces_mask(piece_type=ch.QUEEN, color=ch.BLACK)) * -900
    + int.bit_count(position.pieces_mask(piece_type=ch.ROOK, color=ch.BLACK)) * -500
    + int.bit_count(position.pieces_mask(piece_type=ch.BISHOP, color=ch.BLACK)) * -330
    + int.bit_count(position.pieces_mask(piece_type=ch.KNIGHT, color=ch.BLACK)) * -320
    + int.bit_count(position.pieces_mask(piece_type=ch.PAWN, color=ch.BLACK)) * -100
    # white pieces
    + int.bit_count(position.pieces_mask(piece_type=ch.QUEEN, color=ch.WHITE)) * 900
    + int.bit_count(position.pieces_mask(piece_type=ch.ROOK, color=ch.WHITE)) * 500
    + int.bit_count(position.pieces_mask(piece_type=ch.BISHOP, color=ch.WHITE)) * 330
    + int.bit_count(position.pieces_mask(piece_type=ch.KNIGHT, color=ch.WHITE)) * 320
    + int.bit_count(position.pieces_mask(piece_type=ch.PAWN, color=ch.WHITE)) * 100
    tt[position._board_state()] = score
    return score

def perft(position : ch.Board, depth):
    return 1
    nodes = 0
    if depth == 0:
        return nodes + 1
    for i in position.legal_moves:
        position.push(i)
        nodes += perft(position, depth - 1)
        position.pop()
    return nodes

testing()