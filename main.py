from typing import Union, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from sudoku_solver import Sudoku
"""
Can test using:
curl -H 'Content-Type: application/json'  --data '{"sudoku" : [ " ,9, , , , ,1, , ", "7, ,8,1, , , , ,3", " ,4,5, ,9, , , , ", " , ,7, ,8, , ,5, ", " , ,6,4, , , ,2,7", " , , , , , ,3,8, ", " , , ,8, , , , , ", " ,7, , , ,4, , , ", " 51, , ,3,2, , ,9" ]}' localhost:8000/sudoku
"""
class SudokuInput(BaseModel):
    type: str | None = None
    sudoku: List[str]

app = FastAPI()

@app.get("/")
def read_root():
    return {"error" : "Cannot understand the input provided",
            "description": """Hi ... you've reached the automated Sudoku solver.
    Please post your input sudoku to the /sudoku endpoint, consisting of 9 lines of input, where each line
    consists of a sequence of 9 fields, either an empty slot or a space or containing a number 1-9, separated by commas.
    The request can be a JSON object contain a sudoku element with the lines array:
    """,
    "sudoku" : [
" ,9, , , , ,1, , ",
"7, ,8,1, , , , ,3",
" ,4,5, ,9, , , , ",
" , ,7, ,8, , ,5, ",
" , ,6,4, , , ,2,7",
" , , , , , ,3,8, ",
" , , ,8, , , , , ",
" ,7, , , ,4, , , ",
" 5,1, , ,3,2, , ,9"
]}

@app.post("/sudoku")
def sudoku(input_sudoku: SudokuInput):
    parsed_sudoku = input_helper(input_sudoku.sudoku)
    # need to handle exceptions here - i.e. non-square sudoku
    sudoku_to_solve: Sudoku = Sudoku(parsed_sudoku)
    sudoku_to_solve.setup_csp()
    sudoku_to_solve.solve()
    return {
        "input" : input_sudoku.sudoku,
        "solution": sudoku_to_solve.sudoku
    }


def input_helper(sudoku: List[str]) -> list[list[Optional[int]]]:
    """Parse the provided input (array of strings from the JSON object) into a list of lists,
    where each element is either unknown (None) or the provided numeric value (1-9).
    """
    return [
        [int(i) if i.strip() != "" else None for i in line.strip().split(",")]
        for line in sudoku
    ]

