"""csp.py
From Classic Computer Science Problems in Python Chapter 3
Copyright 2018 David Kopec

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from typing import Generic, TypeVar, Dict, List, Optional
from abc import ABC, abstractmethod

Variable = TypeVar("Variable")  # variable type
Domain = TypeVar("Domain")  # domain type


class Constraint(Generic[Variable, Domain], ABC):
    """Base class for all constraints"""

    # The variables that the constraint is between
    def __init__(self, variables: List[Variable]) -> None:
        self.variables = variables

    @abstractmethod
    def satisfied(self, assignment: Dict[Variable, Domain]) -> bool:
        """Evaluate if the assignment satisfies all constraints; to be
        implemented in the subclass."""


class CSP(Generic[Variable, Domain]):
    """
    A constraint satisfaction problem consists of variables of type V
    that have ranges of values known as domains of type D and constraints
    that determine whether a particular variable's domain selection is valid
    """

    def __init__(
        self, variables: List[Variable], domains: Dict[Variable, List[Domain]]
    ) -> None:
        self.variables: List[Variable] = variables  # variables to be constrained
        self.domains: Dict[Variable, List[Domain]] = domains  # domain of each variable
        self.constraints: Dict[Variable, List[Constraint[Variable, Domain]]] = {}

        # cross-check
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    def add_constraint(self, constraint: Constraint[Variable, Domain]) -> None:
        """Add a single constraint to the framework"""
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            self.constraints[variable].append(constraint)

    def consistent(
        self, variable: Variable, assignment: Dict[Variable, Domain]
    ) -> bool:
        """Check if the value assignment is consistent by checking all constraints
        for the given variable against it
        """
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True  # fall-through if no violations have been found

    def backtracking_search(
        self, assignment: Dict[Variable, Domain] = None
    ) -> Optional[Dict[Variable, Domain]]:
        """assignment is complete if every variable is assigned (our base case)"""
        assignment = {} if assignment is None else assignment       # don't use mutable ds as parameter default
        if len(assignment) == len(self.variables):
            return assignment

        # get all variables in the CSP but not in the assignment
        unassigned: List[Variable] = [v for v in self.variables if v not in assignment]

        # get the every possible domain value of the first unassigned variable
        first: Variable = unassigned[0]
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            # if we're still consistent, we recurse (continue)
            if self.consistent(first, local_assignment):
                result: Optional[Dict[Variable, Domain]] = self.backtracking_search(
                    local_assignment
                )
                # if we didn't find the result, we will end up backtracking
                if result is not None:
                    return result
        return None
