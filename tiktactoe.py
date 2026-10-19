def print_board(board):
    print("---------")
    for row in board:
        print(" | ".join(row))
        print("---------")

def check_winner(board, player):
    # Check rows, columns and diagonals
    for i in range(3):
        if all([cell == player for cell in board[i]]):
            return True
        if all([board[j][i] == player for j in range(3)]):
            return True
    if all([board[i][i] == player for i in range(3)]):
        return True
    if all([board[i][2-i] == player for i in range(3)]):
        return True
    return False

def is_full(board):
    return all(cell != " " for row in board for cell in row)

def tic_tac_toe():
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"
    while True:
        print_board(board)
        print(f"Player {current_player}, enter your move (row and column): ")
        try:
            move = input().split()
            if len(move) != 2:
                print("Please enter two numbers (row and column).")
                continue
            row, col = int(move[0]), int(move[1])
            if not (0 <= row < 3 and 0 <= col < 3):
                print("Row and column must be between 0 and 2.")
                continue
            if board[row][col] != " ":
                print("Cell already occupied. Try again.")
                continue
            board[row][col] = current_player
            if check_winner(board, current_player):
                print_board(board)
                print(f"Player {current_player} wins!")
                break
            if is_full(board):
                print_board(board)
                print("It's a draw!")
                break
            current_player = "O" if current_player == "X" else "X"
        except Exception as e:
            print("Invalid input. Please try again.")
            continue

if __name__ == "__main__":
    tic_tac_toe()