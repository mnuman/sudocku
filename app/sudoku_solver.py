"""
Solve the sudoku!
"""
from csp import Constraint, CSP


class SudokuConstraint(Constraint[tuple[int, int], tuple[int, int]]):
    """Represents the constraint between two variables for the sudoku."""

    def __init__(
        self, cell: tuple[int, int], restricting_cell: tuple[int, int]
    ) -> None:
        super().__init__([cell, restricting_cell])
        self.__cell = cell
        self.__restricting_cell = restricting_cell

    def satisfied(self, assignment: dict[tuple[int, int], int]) -> bool:
        """If both values are populated in the assignment, we require that
        their values be different. For every *pair* of cells which belong
        to the same row, the same column of the same 3x3 block, there
        must exist _exactly_ one constraint.
        (If we already have a constraint requiring x !=y , we do not
        need another requiring y != x).
        """
        return (
            assignment[self.__cell] != assignment[self.__restricting_cell]
            if self.__cell in assignment and self.__restricting_cell in assignment
            else True
        )


class Sudoku:
    """Main class representing the Sudoku puzzle to be solved. It does
    contain the CSP in order to solve itself.
    """

    sudoku: list[list[int]]
    _dim: int
    _csp: CSP
    _variables: list[tuple[int, int]]
    _domains: dict[tuple[int, int], list[int]]
    _mode: str
    __nrc_restricted: list[int] = [1, 2, 3, 5, 6, 7]

    def __init__(self, cells: list[list[int]], mode=None) -> None:
        """Make sure that we have a proper sudoku read in, at least it does
        contain cells in a square pattern.
        """
        rows = len(cells)
        assert rows > 0, "No list provided for setting up initial sudoku"
        for row in cells:
            assert len(row) == rows, "Invalid (non-square) sudoku"
        self.sudoku = cells
        self._dim = len(cells)
        self._mode = mode

    def __str__(self):
        """As its string representation, concatenate all rows from the format."""
        return "\n".join(self.format())

    def format(self):
        """Provide a displayable representation of the sudoku"""
        s = [
            "".join([str(c) if c is not None else "-" for c in r]) for r in self.sudoku
        ]
        for i in range(self._dim):
            s[i] = "|" + s[i][0:3] + "|" + s[i][3:6] + "|" + s[i][6:] + "|"
        s.insert(10, "|-----------|")
        s.insert(6, "|---+---+---|")
        s.insert(3, "|---+---+---|")
        s.insert(0, "|-----------|")
        return s
    
    def generate_variables(self) -> None:
        """The variables are the cells that need to be filled, so
        each row/column combination
        """
        self._variables = [(r, c) for r in range(self._dim) for c in range(self._dim)]

    def generate_restricting_cells(
        self, cell: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Generate the list of tuples (row,col) that restrict the value
        of a restricted location (r, c); excluding the cell itself.
        """
        row, col = cell
        apply_nrc_restrictions = (
            self._mode == "nrc"
            and row in self.__nrc_restricted
            and col in self.__nrc_restricted
        )
        block_row, block_col = (
            row // 3,
            col // 3,
        )  # row, column of the 3x3 block the cell belongs to
        restricting_cells = (
            [(row, c) for c in range(self._dim) if c != col]
            + [(r, col) for r in range(self._dim) if r != row]
            + [
                (3 * block_row + i, 3 * block_col + j)
                for i in range(0, 3)
                for j in range(0, 3)
                if 3 * block_row + i != row and 3 * block_col + j != col
            ]
            + [
                (r, c)
                for r in range(1 + 4 * (row // 4), 4 + 4 * (row // 4))
                for c in range(1 + 4 * (col // 4), 4 + 4 * (col // 4))
                if apply_nrc_restrictions and r != row and c != col
            ]
        )
        return list(set(restricting_cells))

    def generate_domains(self) -> None:
        """The domains are the values the variables are allowed to have. For
        a given cell, this will depend on values already assigned in
        that particular cell by setup, to other cells in the row and
        column the cell is in and to all other cells in its 3x3 block.
        """
        domains = {}
        all_options = set(range(1, 10))
        for var in self._variables:
            row, col = var  # row, column of the cell
            if self.sudoku[row][col] is None:  # not specified in setup
                used_values = list(
                    set(
                        [
                            self.sudoku[cell[0]][cell[1]]
                            for cell in self.generate_restricting_cells(var)
                            if self.sudoku[cell[0]][cell[1]] is not None
                        ]
                    )
                )
                domains[var] = list(all_options - set(used_values) - {None})
            else:  # specified in setup: must restrict to this value only
                domains[var] = [self.sudoku[row][col]]
        self._domains = domains

    def setup_csp(self) -> None:
        """Modelling the problem as a Constraint Satisfying Problem by
        setting up:
         - variables - all cells in the sudoku
         - domains - allowable values per variable
         - constraints - relations between the variables that must be satisfied
        """
        self.generate_variables()
        self.generate_domains()
        self._csp = CSP(self._variables, self._domains)
        for c, rc in [
            (cell, restricting_cell)
            for cell in self._domains.keys()
            for restricting_cell in sorted(self.generate_restricting_cells(cell))
            # ensure we do not have any duplicates. If we register (c,rc)
            # we need not register (rc,c)!
            if cell > restricting_cell
        ]:
            self._csp.add_constraint(SudokuConstraint(c, rc))

    def solve(self) -> None:
        """Perform the backtracking search to find a solution that
        satisfies all constraints.
        """
        solution = self._csp.backtracking_search()
        if solution is not None:
            for (r, c), value in solution.items():
                self.sudoku[r][c] = value

    @property
    def solution_found(self) -> bool:
        return all([cell is not None for row in self.sudoku for cell in row])
