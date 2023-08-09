from typing import Literal, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sudoku_solver import Sudoku
from time import time

"""
Can test using:
-- list input:
curl -H 'Content-Type: application/json'  --data '{"sudoku" : [ " ,9, , , , ,1, , ", "7, ,8,1, , , , ,3", " ,4,5, ,9, , , , ", " , ,7, ,8, , ,5, ", " , ,6,4, , , ,2,7", " , , , , , ,3,8, ", " , , ,8, , , , , ", " ,7, , , ,4, , , ", "5,1, , ,3,2, , ,9" ]}' localhost:8080/sudoku # noqa: 501
-- sparse dictionary input:
curl -H 'Content-Type: application/json'  --data '{"sudoku" : {"12": 9, "17": 1,"21": 7,"23": 8,"24": 1,"29": 3, "32": 4,"33": 5,"35": 9,"43": 7,"45": 8,"48": 5,"53": 6,"54": 4,"58": 2,"59": 7,"67": 3,"68": 8,"74": 8,"82": 7,"86": 4,"91": 5,"92": 1,"95": 3,"96": 2,"99": 9}}' localhost:8080/sudoku # noqa: 501
"""

app = FastAPI(
    title="Sudoku Solver",
    description="Dockerized sudoku solver",
    summary="Solve sudokus. Rule the world.",
    version="0.0.1",
    contact={"name": "Milco Numan", "url": "https://github.com/mnuman/sudocku/"},
)


class SudokuInput(BaseModel):
    sudoku: List[str] | dict[str, int]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sudoku": [
                        " ,9, , , , ,1, , ",
                        "7, ,8,1, , , , ,3",
                        " ,4,5, ,9, , , , ",
                        " , ,7, ,8, , ,5, ",
                        " , ,6,4, , , ,2,7",
                        " , , , , , ,3,8, ",
                        " , , ,8, , , , , ",
                        " ,7, , , ,4, , , ",
                        "5,1, , ,3,2, , ,9",
                    ],
                },
                {"sudoku": {"11": 1, "22": 2, "33": 3}},
            ]
        }
    }


class SudokuNormalResponse(BaseModel):
    solution_time: str = Field(alias="solution-time")
    solution_mode: Optional[Literal["regular", "nrc"]] = Field(alias="solution-mode")
    formatted_solution: List[str] = Field(alias="formatted-solution")
    input: List[str]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "solution-time": "0.575 s",
                    "solution-mode": "regular",
                    "formatted-solution": [
                        "|-----------|",
                        "|293|768|145|",
                        "|768|145|293|",
                        "|145|293|768|",
                        "|---+---+---|",
                        "|927|386|451|",
                        "|386|451|927|",
                        "|451|927|386|",
                        "|---+---+---|",
                        "|632|879|514|",
                        "|879|514|632|",
                        "|514|632|879|",
                        "|-----------|",
                    ],
                    "input": [
                        " ,9, , , , ,1, , ",
                        "7, ,8,1, , , , ,3",
                        " ,4,5, ,9, , , , ",
                        " , ,7, ,8, , ,5, ",
                        " , ,6,4, , , ,2,7",
                        " , , , , , ,3,8, ",
                        " , , ,8, , , , , ",
                        " ,7, , , ,4, , , ",
                        "5,1, , ,3,2, , ,9",
                    ],
                },
                {"detail": "Invalid (non-square) sudoku"},
            ]
        }
    }


@app.post(
    path="/sudoku",
    description="""Solve sudoku, just the normal blocks, rows and columns.
    The input sudoku can be provided in two ways:
    - a list of strings is provided, one for each line of the sudoku,
      where the cells are separated by a comma and each cell is represented
      by a specific number (1-9) or an empty space.
    - alternatively, the input can be represented as a sparse dictionary,
       listing only the non-empty cells. The key to each entry "rc" must
       be row number r (1-9) and column number c (1-9), its value is the
       value the cell is holding.
    The default solution mode consists of constraints of each number
    occurring only once in each row, column and block and need not be 
    specified explicitly. Alternatively, there is a second solution mode
    call 'nrc', for the Sudoku that is regularly published in the 
    NRC newspaper and this introduces additional constraints on the 
    sudoku where each number may also occur only once in each block
    defined by rows and columns [2,3,4] or [6,7,8].
    """,
)
def sudoku(input_sudoku: SudokuInput, mode: Literal["regular", "nrc"] | None = None):
    return __solve__(input_sudoku, mode)


def __solve__(input_sudoku, mode="regular"):
    start_time = time()
    parsed_sudoku = input_helper(input_sudoku.sudoku)
    try:
        sudoku_to_solve: Sudoku = Sudoku(parsed_sudoku, mode=mode)
    except AssertionError as exc:
        raise HTTPException(status_code=422, detail=",".join(exc.args))
    sudoku_to_solve.setup_csp()
    sudoku_to_solve.solve()
    if sudoku_to_solve.solution_found:
        return {
            "solution-time": f"{time() - start_time:5.3f} s",
            "solution-mode": mode if mode is not None else "regular",
            "formatted-solution": sudoku_to_solve.format(),
            "input": input_sudoku.sudoku,
        }
    else:
        return {
            "status": "No solution could be found for the input sudoku - "
            "are you sure it is correct?",
            "solution-mode": mode if mode is not None else "regular",
            "input": input_sudoku.sudoku,
        }


def input_helper(sudoku: List[str] | dict[str, int]) -> list[list[Optional[int]]]:
    """Parse the provided input, where each element is either unknown (None) or
    the provided numeric value (1-9).
    The input can either be a List of nine strings where each string must
    contain 9 elements, separated by a comma, or alternatively a sparse
    dictionary where the key is a string value (10*row + column) and
    the value its pre-assigned number.
    """
    if isinstance(sudoku, list):
        return [
            [int(i) if i.strip() != "" else None for i in line.strip().split(",")]
            for line in sudoku
        ]
    elif isinstance(sudoku, dict):
        return [
            [
                sudoku[str(10 * r + c)] if str(10 * r + c) in sudoku else None
                for c in range(1, 10)
            ]
            for r in range(1, 10)
        ]
