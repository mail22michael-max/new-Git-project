# Tic-Tac-Toe

A two-player command-line Tic-Tac-Toe game written in Python.

Players take turns placing **X** and **O** on a 3×3 board. The game checks for a win (row, column, or diagonal) or a draw when the board is full.

## Requirements

- Python 3

## How to run

From this folder:

```bash
python tiktactoe.py
```

## How to play

1. Player **X** starts.
2. On each turn, enter a **row** and **column** as two numbers, separated by a space.
3. Positions are numbered from `0` to `2`.

Example: `1 2` places a mark in the middle row, right column.

Invalid moves (wrong format, out of range, or occupied cells) are rejected and you are asked to try again.
