# Sudoku problems.
# Solves every Sudoku board below using AC-3 followed by backtracking search,
# printing each board before and after it is solved.

import time

from csp import CSP, alldiff

width = 9
box_width = 3


def print_solution(solution):
    """Prints a Sudoku solution, as returned from CSP.backtracking_search(), as a Sudoku board.

    Parameters
    ----------
    solution : dict[str, Any]
        Value for every cell, keyed by variable name 'X{row}{col}'
    """
    for row in range(width):
        for col in range(width):
            print(solution[f'X{row+1}{col+1}'], end=" ")
            if col == 2 or col == 5:
                print('|', end=" ")
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')


def print_domains(domains):
    """Prints the domain of every cell as a Sudoku board, e.g. {2, 5, 8}.

    Parameters
    ----------
    domains : dict[str, set]
        The domain of every cell, keyed by variable name 'X{row}{col}'
    """
    cells = {
        variable: '{' + ', '.join(str(value) for value in sorted(domain)) + '}'
        for variable, domain in domains.items()
    }
    # Each column is padded to its own widest cell to keep the board compact
    col_widths = [
        max(len(cells[f'X{row+1}{col+1}']) for row in range(width))
        for col in range(width)
    ]
    for row in range(width):
        line = ''
        for col in range(width):
            line += cells[f'X{row+1}{col+1}'].ljust(col_widths[col]) + ' '
            if col == 2 or col == 5:
                line += '| '
        print(line)
        if row == 2 or row == 5:
            # Dashes span each box's columns, with '+' where the '|' separators are
            boxes = [sum(w + 1 for w in col_widths[i:i + 3]) for i in (0, 3, 6)]
            print('-' * boxes[0] + '+' + '-' * (boxes[1] + 1) + '+' + '-' * (boxes[2] + 1))

    unsolved = sum(len(domain) > 1 for domain in domains.values())
    print(f'Cells with more than one value left: {unsolved}')


def build_csp(filename: str) -> tuple[list[str], CSP]:
    """Reads a Sudoku board from file and constructs the corresponding CSP.

    Parameters
    ----------
    filename : str
        Board file with 9 lines of 9 digits, where 0 is an empty cell

    Returns
    -------
    tuple[list[str], CSP]
        The board as a list of row strings, and the CSP
    """
    grid = open(filename).read().split()

    domains = {}
    for row in range(width):
        for col in range(width):
            if grid[row][col] == '0':
                domains[f'X{row+1}{col+1}'] = set(range(1, 10))
            else:
                domains[f'X{row+1}{col+1}'] = {int(grid[row][col])}

    edges = []
    for row in range(width):
        edges += alldiff([f'X{row+1}{col+1}' for col in range(width)])
    for col in range(width):
        edges += alldiff([f'X{row+1}{col+1}' for row in range(width)])
    for box_row in range(box_width):
        for box_col in range(box_width):
            edges += alldiff(
                [
                    f'X{row+1}{col+1}' for row in range(box_row * box_width, (box_row + 1) * box_width)
                    for col in range(box_col * box_width, (box_col + 1) * box_width)
                ]
            )

    csp = CSP(
        variables=[f'X{row+1}{col+1}' for row in range(width) for col in range(width)],
        domains=domains,
        edges=edges,
    )
    return grid, csp


for filename in ['sudoku_easy.txt', 'sudoku_medium.txt', 'sudoku_hard.txt', 'sudoku_very_hard.txt']:
    print(f'===== {filename} =====')
    grid, csp = build_csp(filename)

    # Unsolved board, with '.' for empty cells
    print('Before:')
    print_solution({
        f'X{row+1}{col+1}': grid[row][col] if grid[row][col] != '0' else '.'
        for row in range(width) for col in range(width)
    })

    # Each algorithm is timed separately so printing is not included in the runtimes
    start = time.perf_counter()
    consistent = csp.ac_3()
    ac_3_time = time.perf_counter() - start

    print('AC-3 consistent:', consistent)
    print('Domains after AC-3:')
    print_domains(csp.domains)

    start = time.perf_counter()
    solution = csp.backtracking_search()
    backtracking_time = time.perf_counter() - start

    print('After:')
    if solution is not None:
        print_solution(solution)
    else:
        print('No solution')
    print(f'AC-3 revise calls: {csp.revise_calls}, of which removed values: {csp.revise_successes}')
    print(f'backtrack() calls: {csp.backtrack_calls}, failures: {csp.backtrack_failures}')
    print(f'AC-3 runtime:                 {ac_3_time * 1000:.3f} ms')
    print(f'Backtracking search runtime:  {backtracking_time * 1000:.3f} ms')
    print(f'Total (AC-3 + backtracking):  {(ac_3_time + backtracking_time) * 1000:.3f} ms')

    # For comparison: backtracking search on a fresh CSP, without running AC-3 first
    _, csp_no_ac_3 = build_csp(filename)
    start = time.perf_counter()
    csp_no_ac_3.backtracking_search()
    no_ac_3_time = time.perf_counter() - start
    print(f'Without AC-3: backtrack() calls: {csp_no_ac_3.backtrack_calls}, '
          f'failures: {csp_no_ac_3.backtrack_failures}, runtime: {no_ac_3_time * 1000:.3f} ms')
    print()

# Expected solution for sudoku_easy.txt:
# 7 8 4 | 9 3 2 | 1 5 6
# 6 1 9 | 4 8 5 | 3 2 7
# 2 3 5 | 1 7 6 | 4 8 9
# ------+-------+------
# 5 7 8 | 2 6 1 | 9 3 4
# 3 4 1 | 8 9 7 | 5 6 2
# 9 2 6 | 5 4 3 | 8 7 1
# ------+-------+------
# 4 5 3 | 7 2 9 | 6 1 8
# 8 6 2 | 3 1 4 | 7 9 5
# 1 9 7 | 6 5 8 | 2 4 3
