"""
Snake Game
"""

from enum import Enum
import random


class CellState(Enum):
    FOOD = -1
    EMPTY = 0
    SNAKE_BODY = 1


class GameBoard:
    BOARD_SIZE = 20 # 20 x 20 2-D board

    def __init__(self): 
        self.board = [[CellState.EMPTY] * GameBoard.BOARD_SIZE for _ in range(GameBoard.BOARD_SIZE)]
    
    # Helper function to validate cell position
    def validate_cell_position(self, i, j):
        if not (0 <= i < GameBoard.BOARD_SIZE and 0 <= j < GameBoard.BOARD_SIZE):
            raise ValueError("Invalid cell position")
        return True
    
    # Does Gameboard needs to know about the snake & food cell positions 
    def update_cell_with_food(self, i, j):
        self.validate_cell_position(i, j)
        self.board[i][j] = CellState.FOOD
        
    def update_cell_with_snake_body(self, i, j):
        self.validate_cell_position(i, j)
        self.board[i][j] = CellState.SNAKE_BODY

    def update_cell_to_empty(self, i, j):
        self.validate_cell_position(i, j)
        self.board[i][j] = CellState.EMPTY


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class Position:
    def __init__(self, i = -1, j = -1):
        self.i = i
        self.j = j
    
    def __add__(self, direction: Direction):
        di, dj = direction.value
        return Position(self.i + di, self.j + dj)
    
    def __eq__(self, other):
        # Check the other value instance 
        if not isinstance(other, Position):
            return NotImplemented
        return self.i == other.i and self.j == other.j

class Snake:
    def __init__(self):
        self.body = [Position(10, 2), Position(10, 1), Position(10, 0)] # Default position to spawn snake with head-first
        self._length = 3 # Default snake size
        self._direction = Direction.RIGHT # Default to move in right direction

    def set_direction(self, new_direction):
        # No change in direction for reversal like UP <-> DOWN or LEFT <-> RIGHT
        if self._direction in (Direction.UP, Direction.DOWN):
            if new_direction in (Direction.LEFT, Direction.RIGHT):
                self._direction = new_direction
        else:
            if new_direction in (Direction.UP, Direction.DOWN):
                self._direction = new_direction

    # Snake moves 1 step in the set direction
    def move(self):
        # Calls the Positon class __add__ method internally
        new_head = self.body[0] + self._direction
        self.body.insert(0, new_head)

        if len(self.body) > self._length:
            self.body.pop() # Removes the old tail
    
    def grow(self, old_tail):
        self._length += 1
        self.body.append(old_tail)

    def has_collided(self, new_head_position: Position):
        # Skip the head as it is already added in snake body 
        for position in self.body[1:]:
            if position == new_head_position:
                return True
        return False

class Food:
    def __init__(self):
        self._position = None

    # Food only spawnned in empty spaces
    def create_food(self, snake_body, board_size=20):
        while True:
            candidate = Position(
                random.randrange(0, board_size),
                random.randrange(0, board_size)
            )
            if candidate not in snake_body:
                self._position = candidate
                return self._position
        
    
    # If snake head matches food position, food is eaten
    def is_eaten(self, snake_head):
        return self._position == snake_head


class GameState(Enum):
    NOT_STARTED = "Not Started"
    PLAYING = "Playing"
    PAUSED = "Pause"
    GAME_OVER = "Game Over"


# Game will act as synchronizer between Snake and GameBoard
class Game:


    KEY_TO_DIRECTION = {
        "UP": Direction.UP, 
        "DOWN": Direction.DOWN,
        "LEFT": Direction.LEFT,
        "RIGHT": Direction.RIGHT
    }

    def __init__(self):
        self._reset_state()
    
    def _reset_state(self):
        self.snake = Snake()
        self.board = GameBoard() # Decide later whether to keep this placeholder "Game Board"
        self.food = Food()
        self.state = GameState.NOT_STARTED # Not started
    
    def start(self):
        self.state = GameState.PLAYING
        self.food.create_food(self.snake.body)
        self._sync_board() # Sync game_board at the start
    
    def _sync_board(self):
        self.board = GameBoard() # Resets game_board to empty state
        for pos in self.snake.body:
            self.board.update_cell_with_snake_body(pos.i, pos.j)
        food_pos = self.food._position
        if food_pos:
            self.board.update_cell_with_food(food_pos.i, food_pos.j)
    
    # Implement the core logic of game play and game rules at each state
    def tick(self):
        if self.state != GameState.PLAYING: 
            return
        old_tail = self.snake.body[-1]
        self.snake.move()
        new_head = self.snake.body[0]

        # Check for collision
        if self.snake.has_collided(new_head):
            self.state = GameState.GAME_OVER
            return
        
        ate_food = self.food.is_eaten(new_head)
        self.board.update_cell_with_snake_body(new_head.i, new_head.j)
        if not ate_food:
            # Old tail becomes empty cell
            self.board.update_cell_to_empty(old_tail.i, old_tail.j) 
        else:
            # Snake grows back adding back the old tail
            self.snake.grow(old_tail)

            self.food.create_food(self.snake.body) # Create new food 
            new_food = self.food._position
            self.board.update_cell_with_food(new_food.i, new_food.j)
        

    # Pause a running game 
    def pause(self):
        if self.state != GameState.PLAYING:
            raise ValueError(f"Invalid game state to pause: {self.state.value}")
        self.state = GameState.PAUSED
    
    # Resume a paused game
    def resume(self):
        if self.state != GameState.PAUSED:
            raise ValueError(f"Invalid game state to resume: {self.state.value}")
        self.state = GameState.PLAYING
    
    # Restart to new game 
    def restart(self):
        if self.state == GameState.NOT_STARTED:
            raise ValueError(f"Invalid game state to restart: {self.state.value}")
        self._reset_state()
        self.start()
    
    # Handle key press to change snake direction
    def handle_key_press(self, key):
        direction = Game.KEY_TO_DIRECTION.get(key)
        # Unrecognized key do nothing
        if direction is None:
            return 
        self.snake.set_direction(direction) 