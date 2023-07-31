from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sudoku_solver import Sudoku
from time import time

"""
Can test using:
curl -H 'Content-Type: application/json'  --data '{"sudoku" : [ " ,9, , , , ,1, , ", "7, ,8,1, , , , ,3", " ,4,5, ,9, , , , ", " , ,7, ,8, , ,5, ", " , ,6,4, , , ,2,7", " , , , , , ,3,8, ", " , , ,8, , , , , ", " ,7, , , ,4, , , ", "5,1, , ,3,2, , ,9" ]}' localhost:8080/sudoku # noqa: 501
"""


class SudokuInput(BaseModel):
    type: str | None = None
    sudoku: List[str]


app = FastAPI()


@app.get("/")
def read_root():
    return {
        "error": "Cannot understand the input provided",
        "description": """Hi ... you've reached the automated Sudoku solver.
    Please post your input sudoku to the /sudoku endpoint, consisting of 9
    lines of input, where each line is composed of a sequence of 9 fields,
    either an empty slot or a space or containing a number 1-9, separated
    by commas.
    The request can be a JSON object contain a sudoku element with the lines array:
    """,
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
    }

@app.post("/sudoku-nrc")
def sudoku_nrc(input_sudoku: SudokuInput):
    return __solve__(input_sudoku, mode="nrc")

@app.post("/sudoku")
def sudoku(input_sudoku: SudokuInput):
    return __solve__(input_sudoku, mode=None)


def __solve__(input_sudoku, mode):
    start_time = time()
    parsed_sudoku = input_helper(input_sudoku.sudoku)
    try:
        sudoku_to_solve: Sudoku = Sudoku(parsed_sudoku, mode=mode)
    except AssertionError as exc:
        raise HTTPException(status_code=400, detail=",".join(exc.args))
    sudoku_to_solve.setup_csp()
    sudoku_to_solve.solve()
    if sudoku_to_solve.solution_found:
        return {
            "solution-time": f"{time() - start_time:5.3f} s",
            "solution-mode": "regular" if mode is None else mode,
            "formatted-solution": sudoku_to_solve.format(),
            "input": input_sudoku.sudoku
        }
    else:
        return {
            "status" : "No solution could be found for the input sudoku - are you sure it is correct?",
            "solution-mode": "regular" if mode is None else mode,
            "input": input_sudoku.sudoku
        }

def input_helper(sudoku: List[str]) -> list[list[Optional[int]]]:
    """Parse the provided input (array of strings from the JSON object) into a list
       of lists, where each element is either unknown (None) or the provided numeric
       value (1-9).
    """
    return [
        [int(i) if i.strip() != "" else None for i in line.strip().split(",")]
        for line in sudoku
    ]
