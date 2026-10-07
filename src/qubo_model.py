from itertools import product


def build_constraints(roads, source="Start", target="Hospital"):
    """
    Automatically generate flow constraints from the road network.

    Source:
        outgoing - incoming = 1

    Target:
        incoming - outgoing = 1

    Intermediate node:
        incoming - outgoing = 0
    """

    nodes = set()

    for start, end, cost in roads:
        nodes.add(start)
        nodes.add(end)

    constraints = []

    for node in nodes:

        coefficients = {}

        for edge_id, (start, end, cost) in enumerate(roads):

            if start == node:
                coefficients[edge_id] = (
                    coefficients.get(edge_id, 0) + 1
                )

            if end == node:
                coefficients[edge_id] = (
                    coefficients.get(edge_id, 0) - 1
                )

        if node == source:
            rhs = 1

        elif node == target:
            rhs = -1

        else:
            rhs = 0

        if coefficients:
            constraints.append((coefficients, rhs))

    return constraints


def build_qubo(
    roads,
    source="Start",
    target="Hospital",
    penalty=20
):
    """
    Build QUBO:

        QUBO = travel cost
             + penalty * constraint violations

    Each road is represented by one binary variable.
    """

    qubo = {}

    constraints = build_constraints(
        roads,
        source,
        target
    )

    def add_term(i, j, value):

        key = tuple(sorted((i, j)))

        qubo[key] = qubo.get(key, 0) + value

    # -----------------------------------------------------
    # 1. Travel-cost objective
    # -----------------------------------------------------

    for edge_id, (start, end, cost) in enumerate(roads):

        add_term(
            edge_id,
            edge_id,
            cost
        )

    # -----------------------------------------------------
    # 2. Constraint penalties
    # -----------------------------------------------------

    for coefficients, rhs in constraints:

        variables = list(coefficients.keys())

        # Linear terms
        for i in variables:

            coefficient = coefficients[i]

            linear_value = penalty * (
                coefficient ** 2
                - 2 * rhs * coefficient
            )

            add_term(
                i,
                i,
                linear_value
            )

        # Quadratic terms
        for index_i, i in enumerate(variables):

            for j in variables[index_i + 1:]:

                coefficient_i = coefficients[i]
                coefficient_j = coefficients[j]

                quadratic_value = (
                    2
                    * penalty
                    * coefficient_i
                    * coefficient_j
                )

                add_term(
                    i,
                    j,
                    quadratic_value
                )

    return qubo, constraints


def evaluate_qubo(qubo, bits):

    energy = 0

    for (i, j), coefficient in qubo.items():

        energy += (
            coefficient
            * bits[i]
            * bits[j]
        )

    return energy


def is_valid_solution(
    bits,
    constraints
):
    """
    Check whether all flow constraints are satisfied.
    """

    for coefficients, rhs in constraints:

        value = 0

        for variable, coefficient in coefficients.items():

            value += (
                coefficient
                * bits[variable]
            )

        if value != rhs:
            return False

    return True


def find_best_qubo_solution(
    qubo,
    constraints,
    num_variables
):
    """
    Exhaustively search all binary solutions.

    This is practical only for our small demonstration
    problem and is used to validate the QUBO formulation.
    """

    best_bits = None
    best_energy = float("inf")

    for bits in product(
        [0, 1],
        repeat=num_variables
    ):

        energy = evaluate_qubo(
            qubo,
            bits
        )

        if energy < best_energy:

            best_energy = energy
            best_bits = bits

    return best_bits, best_energy


def decode_route(
    bits,
    roads
):
    """
    Return selected edges.
    """

    selected_edges = []

    for edge_id, bit in enumerate(bits):

        if bit == 1:

            start, end, cost = roads[edge_id]

            selected_edges.append(
                (start, end, cost)
            )

    return selected_edges


def calculate_route_cost(
    bits,
    roads
):
    """
    Calculate actual travel cost,
    without QUBO penalty terms.
    """

    cost = 0

    for edge_id, bit in enumerate(bits):

        if bit == 1:

            cost += roads[edge_id][2]

    return cost


if __name__ == "__main__":

    roads = [
        ("Start", "A", 4),
        ("Start", "B", 2),
        ("A", "C", 3),
        ("A", "Hospital", 7),
        ("B", "C", 1),
        ("B", "Hospital", 8),
        ("C", "Hospital", 2),
    ]

    qubo, constraints = build_qubo(roads)

    bits, energy = find_best_qubo_solution(
        qubo,
        constraints,
        len(roads)
    )

    selected = decode_route(
        bits,
        roads
    )

    travel_cost = calculate_route_cost(
        bits,
        roads
    )

    print("QUBO solution")
    print("-------------")
    print("Binary variables:", bits)
    print("QUBO energy:", energy)
    print("Travel cost:", travel_cost)

    print("\nSelected roads:")

    for start, end, cost in selected:

        print(
            f"{start} -> {end} "
            f"(cost={cost})"
        )