# sudoku-solver

This repository is for building a Dockerized API that is able to solve Sudoku puzzles.

## Sudoku
A sudoku puzzle consists of a grid of 9x9 cells; you can also consider the grid to be built from 9 'blocks' each measure 3x3 cells: three of these blocks are combined on every line and three lines constitute the entire grid.
Every row, column and block consists of 9 cells: every number from 1 to 9 must occur only once in every row, column and block:

![Puzzel van www.sudokuonline.nl](images/sudokuonline.png)

There exist diffent other types of Sudokus as well, e.g. the Sudoku that is published in NRC is subject to an additional restriction, by requiring that in each (consecutive) block formed by the rows and columns 2,3,4,6,7 and 8 the same restriction applies that each number must occur exactly once inside this block:

![NRC Sudoku 9 juni 2023](images/nrc-sudoku-20230609.png)

## Solving Sudokus
This is a search problem of the type CSP, Constraint Satisfaction Problem; it uses the CSP framework described in "[Classic Computer Science Problems in Python](https://www.manning.com/books/classic-computer-science-problems-in-python)" by David Kopec (Manning, 2019). The actual chapter on CSPs has been published as a free article on  [Manning website](https://freecontent.manning.com/constraint-satisfaction-problems-in-python/), the idea that Sudoku puzzles can be solved using the CSP framework is a suggested exercise.
The original code for the CSP framework has been taken from David Kopec's GitHub repository [Classic Computer Science Problems in Python](https://github.com/davecom/ClassicComputerScienceProblemsInPython).

![Manning Classic Computer Science Problems in Python](images/classic-computer-science-problems-in-python.jpg)

## Dependencies
The program was implemented as a self-contained dockerized REST API, running Python 3.11 using the [FastAPI framework](https://fastapi.tiangolo.com/).


## Endpoints
The program supports two different endpoints which are document in the FastAPI documentation endpoints at [doc](/doc) and [redoc](/redoc). The program expects a JSON document for both endpoints, containing a single sudoku element which must be an array of 9 lines. Each line in turn consist of 9 cells separated by a comma; a cell can either be unspecified (space) or contain a single number.


### Sample request
Below is the sample payload for a (valid) request to the regular endpoint, /sudoku:

```json
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
        "5,1, , ,3,2, , ,9"
    ]
}
```

In this case, the API responds with:

```json
{
    "solution-time": "0.078 s",
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
        "|-----------|"
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
        "5,1, , ,3,2, , ,9"
    ]
}```

As you can see from the response above, every number from 1 to 9 occurs only once in every column, row and block.

### NBRC Sudoku
Solving the NRC sudoku takes slightly more time, but is orders of magnitude faster than I could have done it by hand - if I would have succeeded at all!

![NRC Sudoku 9 juni 2023](images/nrc-sudoku-20230609.png)

```json
{
    "solution-time": "0.426 s",
    "solution-mode": "nrc",
    "formatted-solution": [
        "|-----------|",
        "|792|341|865|",
        "|541|698|723|",
        "|638|275|194|",
        "|---+---+---|",
        "|157|926|438|",
        "|386|514|279|",
        "|429|783|516|",
        "|---+---+---|",
        "|265|837|941|",
        "|913|452|687|",
        "|874|169|352|",
        "|-----------|"
    ],
    "input": [
        " , , , , ,1, , , ",
        " , , ,6, , , ,2, ",
        " ,3,8, , , , , ,4",
        " , ,7,9, , , , , ",
        " , , ,5, , , , , ",
        " , ,9, ,8, , , ,6",
        "2, ,5, ,3, ,9, , ",
        " , , ,4, , ,6,8, ",
        " , ,4, , , , ,5, "
    ]
}```

Happy Sudoku-ing!

## Next Step:
As a next step, I might consider building and publishing a new Docker image upon committing the code to Github, using Github Actions.
