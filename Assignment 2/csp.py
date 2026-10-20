from typing import Any
from queue import Queue


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

        # Undirected adjacency map: every variable -> the set of variables it shares a constraint with.
        # binary_constraints only stores one direction per edge, so both directions are added here.
        self.neighbors: dict[str, set[str]] = {variable: set() for variable in variables}
        for variable1, variable2 in edges:
            self.neighbors[variable1].add(variable2)
            self.neighbors[variable2].add(variable1)

    def _is_allowed(self, x_i: str, value_i: Any, x_j: str, value_j: Any) -> bool:
        """Checks whether x_i=value_i and x_j=value_j satisfy the binary constraint between them.

        Handles that binary_constraints is directional, i.e. only (x_i, x_j) or (x_j, x_i) may be stored.

        Parameters
        ----------
        x_i : str
            The first variable
        value_i : Any
            The value assigned to x_i
        x_j : str
            The second variable
        value_j : Any
            The value assigned to x_j

        Returns
        -------
        bool
            True if the pair of values is allowed (or no constraint exists), otherwise False
        """
        if (x_i, x_j) in self.binary_constraints:
            return (value_i, value_j) in self.binary_constraints[(x_i, x_j)]
        if (x_j, x_i) in self.binary_constraints:
            return (value_j, value_i) in self.binary_constraints[(x_j, x_i)]
        return True

    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.
        
        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """
        # Statistics for the report: how many arcs were revised, and how many of those removed values
        self.revise_calls = 0
        self.revise_successes = 0

        # Start with every arc in both directions, since arc consistency is directional
        queue = Queue()
        for x_i in self.variables:
            for x_j in self.neighbors[x_i]:
                queue.put((x_i, x_j))

        while not queue.empty():
            x_i, x_j = queue.get()
            self.revise_calls += 1
            if self._self_revise(x_i, x_j):
                self.revise_successes += 1
                if not self.domains[x_i]:
                    return False
                # x_i's domain shrank, so every other neighbour's arc into x_i must be rechecked
                for x_k in self.neighbors[x_i] - {x_j}:
                    queue.put((x_k, x_i))

        return True


    def _self_revise(self, x_i: str, x_j: str) -> bool:
        """Helper function for ac_3() that revises the domain of x_i with respect to x_j.

        Parameters
        ----------
        x_i : str
            The variable whose domain is being revised
        x_j : str
            The variable that is being used to revise the domain of x_i

        Returns
        -------
        bool
            True if the domain of x_i was revised, otherwise False
        """
        revised = False
        # Iterate over a copy, since values are removed from the domain inside the loop
        for value in list(self.domains[x_i]):
            # Remove value if no value in x_j's domain is compatible with it
            if not any(self._is_allowed(x_i, value, x_j, other_value) for other_value in self.domains[x_j]):
                self.domains[x_i].remove(value)
                revised = True
        return revised

    def backtracking_search(self) -> None | dict[str, Any]:
        """Performs backtracking search on the CSP.
        
        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        # Statistics for the report: how often backtrack() is called and how often it returns failure
        self.backtrack_calls = 0
        self.backtrack_failures = 0

        def backtrack(assignment: dict[str, Any]):
            """Recursive helper that extends the partial assignment one variable at a time.

            Parameters
            ----------
            assignment : dict[str, Any]
                The current consistent partial assignment

            Returns
            -------
            None | dict[str, Any]
                A complete assignment, or None (failure) if no value leads to a solution
            """
            self.backtrack_calls += 1
            if len(assignment) == len(self.variables):
                return assignment

            # Select-Unassigned-Variable: the first unassigned variable
            var = next(v for v in self.variables if v not in assignment)

            # Order-Domain-Values: the domain's own iteration order
            for value in self.domains[var]:
                # Only check constraints against neighbours that are already assigned
                if all(
                    self._is_allowed(var, value, neighbor, assignment[neighbor])
                    for neighbor in self.neighbors[var] if neighbor in assignment
                ):
                    assignment[var] = value
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    del assignment[var]

            self.backtrack_failures += 1
            return None

        return backtrack({})


def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]
