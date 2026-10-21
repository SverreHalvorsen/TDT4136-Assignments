import math
import time
from copy import deepcopy

State = tuple[int, list[list[int | None]]]  # Tuple of player (whose turn it is),
# and board
Action = tuple[int, int]  # Where to place the player's piece


class Game:
    def initial_state(self) -> State:
        return (0, [[None, None, None], [None, None, None], [None, None, None]])

    def to_move(self, state: State) -> int:
        player_index, _ = state
        return player_index

    def actions(self, state: State) -> list[Action]:
        _, board = state
        actions = []
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    actions.append((row, col))
        return actions

    def result(self, state: State, action: Action) -> State:
        _, board = state
        row, col = action
        next_board = deepcopy(board)
        next_board[row][col] = self.to_move(state)
        return (self.to_move(state) + 1) % 2, next_board

    def is_winner(self, state: State, player: int) -> bool:
        _, board = state
        for row in range(3):
            if all(board[row][col] == player for col in range(3)):
                return True
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return True
        if all(board[i][i] == player for i in range(3)):
            return True
        return all(board[i][2 - i] == player for i in range(3))

    def is_terminal(self, state: State) -> bool:
        _, board = state
        if self.is_winner(state, (self.to_move(state) + 1) % 2):
            return True
        return all(board[row][col] is not None for row in range(3) for col in range(3))

    def utility(self, state, player):
        assert self.is_terminal(state)
        if self.is_winner(state, player):
            return 1
        if self.is_winner(state, (player + 1) % 2):
            return -1
        return 0

    def print(self, state: State):
        _, board = state
        print()
        for row in range(3):
            cells = [
                ' ' if board[row][col] is None else 'x' if board[row][col] == 0 else 'o'
                for col in range(3)
            ]
            print(f' {cells[0]} | {cells[1]} | {cells[2]}')
            if row < 2:
                print('---+---+---')
        print()
        if self.is_terminal(state):
            if self.utility(state, 0) > 0:
                print(f'P1 won')
            elif self.utility(state, 1) > 0:
                print(f'P2 won')
            else:
                print('The game is a draw')
        else:
            print(f'It is P{self.to_move(state) + 1}\'s turn to move')


def minimax_search(game: Game, state: State) -> Action | None:
    """ Returns the best action for the player to move in the given state using the Minimax algorithm. """
    player = game.to_move(state)
    value, move = max_value_minimax(game, state, player)
    return move


def max_value_minimax(game: Game, state: State, player: int) -> tuple[float, Action | None]:
    """ Returns the maximum utility value and the corresponding action for the player to move in the
        given state using the Minimax algorithm. """
    if game.is_terminal(state):
        return game.utility(state, player), None
    value, move = -math.inf, None
    for action in game.actions(state):
        value2, action2 = min_value_minimax(game, game.result(state, action), player)
        if value2 > value:
            value, move = value2, action
    return value, move


def min_value_minimax(game: Game, state: State, player: int) -> tuple[float, Action | None]:
    """ Returns the minimum utility value and the corresponding action for the player to move in the
        given state using the Minimax algorithm. """
    if game.is_terminal(state):
        return game.utility(state, player), None
    value, move = math.inf, None
    for action in game.actions(state):
        value2, action2 = max_value_minimax(game, game.result(state, action), player)
        if value2 < value:
            value, move = value2, action
    return value, move


def alfa_beta_search(game: Game, state: State) -> Action | None:
    """ Returns the best action for the player to move in the given state using the Alpha-Beta pruning algorithm. """
    player = game.to_move(state)
    value, move = max_value_alfa_beta(game, state, player, -math.inf, math.inf)
    return move


def max_value_alfa_beta(game: Game, state: State, player: int, alfa: float, beta: float) -> tuple[float, Action | None]:
    """ Returns the maximum utility value and the corresponding action for the player to move in the
        given state using the Alpha-Beta pruning algorithm. """
    if game.is_terminal(state):
        return game.utility(state, player), None
    value, move = -math.inf, None
    for action in game.actions(state):
        value2, action2 = min_value_alfa_beta(game, game.result(state, action), player, alfa, beta)
        if value2 > value:
            value, move = value2, action
            alfa = max(alfa, value)
        if value >= beta:
            return value, move
    return value, move


def min_value_alfa_beta(game: Game, state: State, player: int, alfa: float, beta: float) -> tuple[float, Action | None]:
    """ Returns the minimum utility value and the corresponding action for the player to move in the
        given state using the Alpha-Beta pruning algorithm. """
    if game.is_terminal(state):
        return game.utility(state, player), None
    value, move = math.inf, None
    for action in game.actions(state):
        value2, action2 = max_value_alfa_beta(game, game.result(state, action), player, alfa, beta)
        if value2 < value:
            value, move = value2, action
            beta = min(beta, value)
        if value <= alfa:
            return value, move
    return value, move


def run_game(algorithm):
    """ A simple function to run a game between two players using the specified algorithm. Using the handout
        while-loop, running the algorithm passed as a parameter to determine the next move. """
    game = Game()

    state = game.initial_state()
    game.print(state)
    move_number = 1
    while not game.is_terminal(state):
        player = game.to_move(state)
        if move_number == 1:
            start_time = time.perf_counter()
            action = algorithm(game, state)  # The player whose turn it is
            end_time = time.perf_counter()
        else:
            action = algorithm(game, state)
        # is the MAX player
        print(f'P{player + 1}\'s action: {action}')
        assert action is not None
        state = game.result(state, action)
        game.print(state)
        move_number += 1
    return end_time - start_time

print("Minimax algorithm:")
print("-----------------")
first_move_time_minimax = run_game(minimax_search)
print(f"\nTime taken for the first move using Minimax: {first_move_time_minimax:.6f} seconds")

print("\nAlfa-beta pruning algorithm:")
print("-----------------------------")
first_move_time_alfa_beta = run_game(alfa_beta_search)
print(f"\nTime taken for the first move using Alfa-beta: {first_move_time_alfa_beta:.6f} seconds")

print()
print(f"Alpha-beta pruning was {first_move_time_minimax}s / {first_move_time_alfa_beta}s = "
      f"{first_move_time_minimax / first_move_time_alfa_beta:.2f} times faster than Minimax for the first move.")
