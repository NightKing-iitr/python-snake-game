"""
Terminal runner for the Snake game.

It does three jobs:
  1. Read keyboard input without blocking (so the snake keeps moving even if
     no key is pressed).
  2. Call game.tick() on a fixed interval.
  3. Render game.board by reading its data and printing it 

Run with:  python3 play.py
Controls:  Arrow keys or W,A,S,D to move, P to pause/resume, R to restart
           (when game over), Q to quit any time.
"""

import sys
import termios
import tty
import select
import time

from snake_game import Game, GameState, CellState

TICK_INTERVAL = 0.15  # seconds between automatic snake moves

CELL_CHAR = {
    CellState.EMPTY: ". ",
    CellState.SNAKE_BODY: "\033[92m# \033[0m",      # Green snake
    CellState.FOOD: "\033[91m* \033[0m",            # Red food
}

KEY_MAP = {
    "\x1b[A": "UP", "\x1b[B": "DOWN", "\x1b[C": "RIGHT", "\x1b[D": "LEFT", # Arrow keys maped to direction
    "w": "UP", "W": "UP",
    "s": "DOWN", "S": "DOWN",
    "a": "LEFT", "A": "LEFT",
    "d": "RIGHT", "D": "RIGHT",
    "p": "PAUSE", "P": "PAUSE",
    "r": "RESTART", "R": "RESTART",
    "q": "QUIT", "Q": "QUIT",
}


def get_key_nonblocking(timeout):
    """Return a mapped key string, or None if nothing arrived within timeout."""
    dr, _, _ = select.select([sys.stdin], [], [], timeout)
    if not dr:
        return None
    ch = sys.stdin.read(1)
    if ch == "\x1b":
        ch += sys.stdin.read(1) + sys.stdin.read(1)
    return KEY_MAP.get(ch)


def render(game):
    sys.stdout.write("\x1b[H\x1b[J")  # cursor home + clear screen
    rows = ["".join(CELL_CHAR[cell] for cell in row) for row in game.board.board]
    sys.stdout.write("\n".join(rows))
    sys.stdout.write(f"\n\nScore: {len(game.snake.body)}   State: {game.state.value}")
    if game.state == GameState.GAME_OVER:
        sys.stdout.write("\n\nGame over!  R = restart   Q = quit")
    else:
        sys.stdout.write("\n\nArrows/WASD = move   P = pause/resume   Q = quit")
    sys.stdout.flush()


def main():
    game = Game()
    game.start()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        last_tick = time.time()
        render(game)

        while True:
            elapsed = time.time() - last_tick
            wait = max(0.0, TICK_INTERVAL - elapsed)
            key = get_key_nonblocking(timeout=wait)

            if key == "QUIT":
                break

            elif key == "RESTART" and game.state == GameState.GAME_OVER:
                game.restart()
                last_tick = time.time()
                render(game)
                continue

            elif key == "PAUSE":
                if game.state == GameState.PLAYING:
                    game.pause()
                elif game.state == GameState.PAUSED:
                    game.resume()
                render(game)

            elif key in ("UP", "DOWN", "LEFT", "RIGHT"):
                game.handle_key_press(key)

            if time.time() - last_tick >= TICK_INTERVAL:
                game.tick()
                last_tick = time.time()
                render(game)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nThanks for playing!")


if __name__ == "__main__":
    main()