import curses
import random
import time
from collections import namedtuple

SCREEN_MIN_Y = 24
SCREEN_MIN_X = 80

NW = (-1, -1)
N = (-1, 0)
NE = (-1, 1)
W = (0, -1)
E = (0, 1)
SW = (1, -1)
S = (1, 0)
SE = (1, 1)

EMPTY_PATTERN = {
    1: ("   ",),
    2: (
        "     ",
        "     ",
    ),
    3: (
        "       ",
        "       ",
        "       ",
    ),
}
WALL_PATTERN = {
    1: (" # ",),
    2: (
        " # # ",
        " # # ",
    ),
    3: (
        " ##### ",
        " ##### ",
        " ##### ",
    ),
}
CROSS_PATTERN = {
    1: (" X ",),
    2: (
        r" \ / ",
        r" / \ ",
    ),
    3: (
        r"  \ /  ",
        r"   X   ",
        r"  / \  ",
    ),
}
TRIANGLE_PATTERN = {
    1: (" ^ ",),
    2: (
        "  ^  ",
        " ^ ^ ",
    ),
    3: (
        "   ^   ",
        "  ^ ^  ",
        " ^ ^ ^ ",
    ),
}
SQUARE_PATTERN = {
    1: (" ■ ",),
    2: (
        " ┌─┐ ",
        " └─┘ ",
    ),
    3: (
        " ┌───┐ ",
        " │ ■ │ ",
        " └───┘ ",
    ),
}

Square = namedtuple("Square", "id color pattern moves")
EMPTY = Square(0, 0, EMPTY_PATTERN, ())
WALL = Square(1, 4, WALL_PATTERN, ())
CROSS = Square(2, 5, CROSS_PATTERN, (NW, NE, SW, SE))
TRIANGLE = Square(3, 3, TRIANGLE_PATTERN, (W, N, E))
SQUARE = Square(4, 2, SQUARE_PATTERN, (N, W, S, E))
SQUARES = (EMPTY, WALL, CROSS, TRIANGLE, SQUARE)

BOARD_TUPLE = {
    3: tuple([EMPTY.id] * 1 + [WALL.id] * 2 + [CROSS.id, TRIANGLE.id, SQUARE.id] * 2),
    4: tuple([EMPTY.id] * 1 + [WALL.id] * 3 + [CROSS.id, TRIANGLE.id, SQUARE.id] * 4),
}
MAX_LEVELS = {
    3: 50,
    4: 70,
}


def to_tuple(board_1):
    return tuple(square for row in board_1 for square in row)


def to_board(t):
    board_size = int(len(t) ** 0.5)
    return [list(t[i * board_size : (i + 1) * board_size]) for i in range(board_size)]


def is_valid_board(s, board_size):
    if not all(c.isdigit() for c in s):
        return False
    boards_l = list(map(int, s))
    board_l_1 = boards_l[: board_size**2]
    board_l_2 = boards_l[board_size**2 :]
    squares = sorted(BOARD_TUPLE[board_size])
    if not sorted(board_l_1) == sorted(board_l_2) == squares:
        return False
    walls_1 = [i for i, square in enumerate(board_l_1) if square == WALL.id]
    walls_2 = [i for i, square in enumerate(board_l_2) if square == WALL.id]
    return walls_1 == walls_2


def get_ascii_boards(board_1, board_2, pattern_size):
    ascii_boards = []

    (height,) = set(len(s.pattern[pattern_size]) for s in SQUARES)
    (width,) = set(
        len(s.pattern[pattern_size][i]) for i in range(height) for s in SQUARES
    )
    board_size = len(board_1)
    line = "-" * ((width + 1) * board_size + 1)
    sep = " " * (width - 1) + "║" + " " * (width - 1)
    grid = line + sep + line + "\n"

    def _add_board(_board, _i, _j):
        vbar = "|"
        ascii_boards.append((vbar, 0))
        for square in _board[_i]:
            s = SQUARES[square]
            ascii_boards.append((s.pattern[pattern_size][_j], s.color))
            ascii_boards.append((vbar, 0))

    ascii_boards.append((grid, 0))
    for i in range(board_size):
        for j in range(height):
            _add_board(board_1, i, j)
            ascii_boards.append((sep, 0))
            _add_board(to_board(board_2), i, j)
            ascii_boards.append(("\n", 0))
        ascii_boards.append((grid, 0))

    return ascii_boards


def get_empty_square(board_1):
    board_size = len(board_1)
    for y in range(board_size):
        for x in range(board_size):
            if board_1[y][x] == EMPTY.id:
                return y, x
    raise ValueError("No empty square")


def get_legal_moves(board_1):
    board_size = len(board_1)
    legal_moves = []
    y, x = get_empty_square(board_1)
    for move in (NW, N, NE, W, E, SW, S, SE):
        new_y, new_x = y - move[0], x - move[1]
        if 0 <= new_y < board_size and 0 <= new_x < board_size:
            new_square = SQUARES[board_1[new_y][new_x]]
            if move in new_square.moves:
                legal_moves.append(move)
    return legal_moves


def make_move(board_1, move):
    y, x = get_empty_square(board_1)
    new_y, new_x = y - move[0], x - move[1]
    board_1[new_y][new_x], board_1[y][x] = board_1[y][x], board_1[new_y][new_x]
    return board_1


def undo(board_1, move):
    return make_move(board_1, (-move[0], -move[1]))


def solve(board_1, board_2=None, max_depth=None):
    queue = [[(to_tuple(board_1), None)]]
    path = []
    expanded = []
    i = 0
    while queue:
        path = queue.pop(0)
        if max_depth and len(path) >= max_depth + 1:
            break
        last_board_tuple = path[-1][0]
        if last_board_tuple in expanded:
            continue

        board = to_board(last_board_tuple)
        legal_moves = get_legal_moves(board)
        if not board_2:
            random.shuffle(legal_moves)
        for move in legal_moves:
            board = make_move(board, move)
            board_tuple = to_tuple(board)
            if board_tuple not in expanded:
                queue.append(path + [(board_tuple, move)])
            board = undo(board, move)

        expanded.append(last_board_tuple)
        i += 1
        if board_2 and last_board_tuple == board_2:
            break
        if max_depth and i > max_depth**2:
            break

    return path[1:]


def generate_random_boards(board_size, level):
    squares = list(BOARD_TUPLE[board_size])
    while True:
        random.shuffle(squares)
        board_1 = to_board(tuple(squares))
        path = solve(board_1, max_depth=level)
        if len(path) >= level:
            break
    board_2 = path[-1][0]
    best_moves = [p[1] for p in path]
    return board_1, board_2, best_moves


def _play(stdscr):
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    curses.curs_set(0)

    refresh_move = (0, 0)
    init = True
    imported = False
    _board_1, _board_2, _best_moves = None, None, []
    board_1, board_2, best_moves = None, None, []
    played_moves = []
    puzzle_id = ""
    board_size = 4
    pattern_size = 3
    level = 20
    moves_to_play = []

    while True:
        if init:
            stdscr.addstr("Loading...")
            stdscr.refresh()
            if imported:
                board_1, board_2, best_moves = _board_1, _board_2, _best_moves
                level = len(best_moves)
                imported = False
            else:
                board_1, board_2, best_moves = generate_random_boards(board_size, level)
            played_moves = []
            puzzle_id = "".join(map(str, to_tuple(board_1) + board_2))
            init = False

        if len(moves_to_play) == 0:
            moves_to_play = [refresh_move]
            do_sleep = False
        elif len(moves_to_play) == 1:
            do_sleep = False
        else:
            do_sleep = True

        while moves_to_play:
            move = moves_to_play.pop(0)
            if move != refresh_move:
                board_1 = make_move(board_1, move)
                played_moves.append(move)
            if do_sleep:
                time.sleep(1)

            stdscr.erase()
            puzzle_id_str = f"Puzzle ID: {puzzle_id}"
            moves_str = f"Moves: {len(played_moves)} (shortest: {len(best_moves)})"
            spaces = " " * (SCREEN_MIN_X - 1 - len(puzzle_id_str) - len(moves_str))
            stdscr.addstr(f"{puzzle_id_str}{spaces}{moves_str}\n")
            m1 = "Play: ↑,↓,→,←,s,d,x,c ; Undo: u ; Reset: r ; Hurry: h ; New game: n\n"
            stdscr.addstr(m1)
            m2 = "Import: i ; Board size: b ; Pattern size: p ; Level: l ; Quit: q\n"
            stdscr.addstr(m2)
            stdscr.addstr("\n")
            for s, color in get_ascii_boards(board_1, board_2, pattern_size):
                stdscr.addstr(s, curses.color_pair(color))
            stdscr.addstr("\n")
            stdscr.refresh()

        if to_tuple(board_1) == board_2:
            stdscr.addstr("Congrats! ")
            solved = True
        else:
            solved = False

        keys_to_moves = {
            curses.KEY_UP: N,
            curses.KEY_DOWN: S,
            curses.KEY_LEFT: W,
            curses.KEY_RIGHT: E,
            ord("s"): NW,
            ord("S"): NW,
            ord("d"): NE,
            ord("D"): NE,
            ord("x"): SW,
            ord("X"): SW,
            ord("c"): SE,
            ord("C"): SE,
        }
        c = stdscr.getch()
        if c in keys_to_moves:
            move = keys_to_moves[c]
            if not solved and move in get_legal_moves(board_1):
                moves_to_play = [move]

        elif c in (ord("u"), ord("U")):
            if played_moves:
                board_1 = undo(board_1, played_moves.pop())

        elif c in (ord("r"), ord("R"), ord("h"), ord("H")):
            while played_moves:
                board_1 = undo(board_1, played_moves.pop())
            if c in (ord("h"), ord("H")):
                moves_to_play = [refresh_move] + best_moves

        elif c in (ord("n"), ord("N")):
            init = True

        elif c in (ord("i"), ord("I")):
            curses.echo()
            msg = f"Enter a {board_size}x{board_size} puzzle ID & press ENTER: "
            stdscr.addstr(msg)
            s = stdscr.getstr(2 * (board_size**2)).decode()
            curses.noecho()
            if not is_valid_board(s, board_size):
                continue
            b = tuple(map(int, s))
            _board_1, _board_2 = to_board(b[: board_size**2]), b[board_size**2 :]
            path = solve(_board_1, board_2=_board_2)
            _best_moves = [p[1] for p in path]
            if path[-1][0] == _board_2:
                init = True
                imported = True

        elif c in (ord("b"), ord("B")):
            board_size = 7 - board_size
            level = min(level, MAX_LEVELS[board_size])
            init = True

        elif c in (ord("p"), ord("P")):
            (n_pattern,) = set(len(s.pattern) for s in SQUARES)
            pattern_size = (pattern_size % n_pattern) + 1

        elif c in (ord("l"), ord("L")):
            curses.echo()
            max_level = MAX_LEVELS[board_size]
            stdscr.addstr(f"Enter a level (1-{max_level}) & press ENTER: ")
            s = stdscr.getstr(len(str(max_level))).decode()
            curses.noecho()
            if s.isdigit() and 1 <= (level := int(s)) <= max_level:
                init = True

        elif c in (ord("q"), ord("Q")):
            stdscr.addstr("Are you sure you want to quit? ")
            stdscr.addstr("(press y to quit or any other key to continue)")
            c2 = stdscr.getch()
            if c2 in (ord("y"), ord("Y")):
                break


def play(stdscr):
    try:
        _play(stdscr)
    except curses.error as err:
        y, x = stdscr.getmaxyx()
        if y < SCREEN_MIN_Y or x < SCREEN_MIN_X:
            raise curses.error("Screen is too small")
        raise err


def main():
    try:
        curses.wrapper(play)
    except KeyboardInterrupt:
        pass
    except curses.error as err:
        print(err)


if __name__ == "__main__":
    main()
