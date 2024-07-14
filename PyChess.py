import chess as ch

player = True
FEN = (ch.STARTING_FEN)
chess_board = ch.Board(fen=FEN)

def evaluate_position(position):
    score = 0
    if position.is_checkmate():
        return -1e9
    if position.is_stalemate():
        return 0
    # score += sum of all the pieces multiplied by their values
    # eval function just counts the pieces left

# add tt map later
