from typing import Literal, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sudoku_solver import Sudoku
from time import time

"""
Can test using:
curl -H 'Content-Type: application/json'  --data '{"sudoku" : [ " ,9, , , , ,1, , ", "7, ,8,1, , , , ,3", " ,4,5, ,9, , , , ", " , ,7, ,8, , ,5, ", " , ,6,4, , , ,2,7", " , , , , , ,3,8, ", " , , ,8, , , , , ", " ,7, , , ,4, , , ", "5,1, , ,3,2, , ,9" ]}' localhost:8080/sudoku # noqa: 501
"""

app = FastAPI(
    title="Sudoku Solver",
    description="""Dockerized sudoku solver""",
    summary="Solve sudokus. Rule the world.",
    version="0.0.1",
    contact={"name": "Milco Numan", "url": "https://github.com/mnuman/sudocku/"},
)


class SudokuInput(BaseModel):
    type: str | None = None
    sudoku: List[str]
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
                    ]
                }
            ]
        }
    }


class SudokuNormalResponse(BaseModel):
    solution_time: str = Field(alias="solution-time")
    solution_mode: Literal["regular", "nrc"] = Field(alias="solution-mode")
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
    path="/sudoku-nrc",
    response_model=SudokuNormalResponse,
    description="Solve NRC-style sudoku with four additional blocks",
)
def sudoku_nrc(input_sudoku: SudokuInput):
    return __solve__(input_sudoku, mode="nrc")


@app.post(
    path="/sudoku",
    description="Solve regular sudoku, just the normal blocks, rows and columns ...",
)
def sudoku(input_sudoku: SudokuInput):
    return __solve__(input_sudoku, mode=None)


def __solve__(input_sudoku, mode):
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
            "solution-mode": "regular" if mode is None else mode,
            "formatted-solution": sudoku_to_solve.format(),
            "input": input_sudoku.sudoku,
        }
    else:
        return {
            "status":
                "No solution could be found for the input sudoku - "
                "are you sure it is correct?",
            "solution-mode": "regular" if mode is None else mode,
            "input": input_sudoku.sudoku,
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
