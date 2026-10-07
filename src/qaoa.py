import numpy as np

from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp


# ---------------------------------------------------------
# QUBO → ISING
# ---------------------------------------------------------

def qubo_to_ising(qubo, num_qubits):

    constant = 0.0

    linear = np.zeros(num_qubits)

    quadratic = {}

    for (i, j), coefficient in qubo.items():

        # -------------------------------------------------
        # Linear term
        # qii * xi
        #
        # xi = (1 - Zi) / 2
        # -------------------------------------------------

        if i == j:

            constant += coefficient / 2

            linear[i] -= coefficient / 2

        # -------------------------------------------------
        # Quadratic term
        #
        # qij * xi*xj
        #
        # xi*xj =
        # (1-Zi)(1-Zj)/4
        # -------------------------------------------------

        else:

            constant += coefficient / 4

            linear[i] -= coefficient / 4
            linear[j] -= coefficient / 4

            key = tuple(sorted((i, j)))

            quadratic[key] = (
                quadratic.get(key, 0)
                + coefficient / 4
            )

    return constant, linear, quadratic


# ---------------------------------------------------------
# CREATE ISING HAMILTONIAN
# ---------------------------------------------------------

def create_ising_hamiltonian(
    qubo,
    num_qubits
):

    constant, linear, quadratic = qubo_to_ising(
        qubo,
        num_qubits
    )

    pauli_terms = []
    coefficients = []

    # Linear Z terms
    for i, value in enumerate(linear):

        if abs(value) < 1e-12:
            continue

        pauli = ["I"] * num_qubits
        pauli[i] = "Z"

        pauli_terms.append(
            "".join(pauli)
        )

        coefficients.append(value)

    # Quadratic ZZ terms
    for (i, j), value in quadratic.items():

        if abs(value) < 1e-12:
            continue

        pauli = ["I"] * num_qubits

        pauli[i] = "Z"
        pauli[j] = "Z"

        pauli_terms.append(
            "".join(pauli)
        )

        coefficients.append(value)

    if pauli_terms:

        hamiltonian = SparsePauliOp.from_list(
            list(
                zip(
                    pauli_terms,
                    coefficients
                )
            )
        )

    else:

        hamiltonian = SparsePauliOp.from_list(
            [
                (
                    "I" * num_qubits,
                    0
                )
            ]
        )

    return hamiltonian, constant


# ---------------------------------------------------------
# QAOA CIRCUIT
# ---------------------------------------------------------

def create_qaoa_circuit(
    hamiltonian,
    parameters,
    num_qubits,
    p
):

    circuit = QuantumCircuit(
        num_qubits
    )

    # -----------------------------------------------------
    # Initial state |+>
    # -----------------------------------------------------

    for qubit in range(num_qubits):

        circuit.h(qubit)

    # -----------------------------------------------------
    # QAOA layers
    # -----------------------------------------------------

    for layer in range(p):

        gamma = parameters[layer]
        beta = parameters[p + layer]

        # ---------------------------------------------
        # Cost Hamiltonian
        # ---------------------------------------------

        pauli_list = hamiltonian.paulis
        coeffs = hamiltonian.coeffs

        for pauli, coefficient in zip(
            pauli_list,
            coeffs
        ):

            label = pauli.to_label()

            # Only handle real Z/ZZ terms
            if "X" in label or "Y" in label:
                continue

            z_positions = [
                index
                for index, char in enumerate(label)
                if char == "Z"
            ]

            if len(z_positions) == 1:

                qubit = z_positions[0]

                angle = float(
                    2
                    * gamma
                    * np.real(coefficient)
                )

                circuit.rz(
                    angle,
                    qubit
                )

            elif len(z_positions) == 2:

                q1, q2 = z_positions

                angle = float(
                    2
                    * gamma
                    * np.real(coefficient)
                )

                circuit.cx(
                    q1,
                    q2
                )

                circuit.rz(
                    angle,
                    q2
                )

                circuit.cx(
                    q1,
                    q2
                )

        # ---------------------------------------------
        # Mixer Hamiltonian
        # ---------------------------------------------

        for qubit in range(num_qubits):

            circuit.rx(
                2 * beta,
                qubit
            )

    return circuit


# ---------------------------------------------------------
# EXPECTATION VALUE
# ---------------------------------------------------------

def expectation_value(
    hamiltonian,
    statevector
):

    value = statevector.expectation_value(
        hamiltonian
    )

    return float(
        np.real(value)
    )


# ---------------------------------------------------------
# QAOA OPTIMIZATION
# ---------------------------------------------------------

def optimize_qaoa(
    qubo,
    num_qubits,
    p=2
):

    hamiltonian, constant = create_ising_hamiltonian(
        qubo,
        num_qubits
    )

    def objective(parameters):

        circuit = create_qaoa_circuit(
            hamiltonian,
            parameters,
            num_qubits,
            p
        )

        state = Statevector.from_instruction(
            circuit
        )

        return expectation_value(
            hamiltonian,
            state
        )

    # -----------------------------------------------------
    # Initial parameters
    # -----------------------------------------------------

    initial_parameters = np.random.uniform(
        0,
        2 * np.pi,
        2 * p
    )

    # -----------------------------------------------------
    # Classical optimization
    # -----------------------------------------------------

    result = minimize(
        objective,
        initial_parameters,
        method="COBYLA",
        options={
            "maxiter": 100
        }
    )

    final_parameters = result.x

    final_circuit = create_qaoa_circuit(
        hamiltonian,
        final_parameters,
        num_qubits,
        p
    )

    final_state = Statevector.from_instruction(
        final_circuit
    )

    final_expectation = expectation_value(
        hamiltonian,
        final_state
    )

    print(
        "Final expectation value:",
        final_expectation
    )

    return (
        final_parameters,
        hamiltonian,
        final_state,
        final_expectation
    )


# ---------------------------------------------------------
# FEASIBLE SOLUTION
# ---------------------------------------------------------

def get_best_feasible_solution(
    statevector,
    constraints,
    num_qubits
):

    probabilities = statevector.probabilities()

    candidates = []

    for integer_state, probability in enumerate(
        probabilities
    ):

        bits_string = format(
            integer_state,
            f"0{num_qubits}b"
        )

        bits = tuple(
            int(bit)
            for bit in bits_string
        )

        # Qiskit bit ordering is reversed relative
        # to the variable order used in our model.
        bits = tuple(
            reversed(bits)
        )

        if probability > 1e-12:

            valid = True

            for coefficients, rhs in constraints:

                value = 0

                for variable, coefficient in coefficients.items():

                    value += (
                        coefficient
                        * bits[variable]
                    )

                if value != rhs:

                    valid = False
                    break

            if valid:

                candidates.append(
                    (
                        probability,
                        bits
                    )
                )

    if not candidates:

        return None, 0.0

    candidates.sort(
        reverse=True
    )

    best_probability, best_bits = candidates[0]

    return (
        best_bits,
        best_probability
    )


# ---------------------------------------------------------
# ROUTE DECODING
# ---------------------------------------------------------

def decode_route(
    bits,
    roads,
    source="Start",
    target="Hospital"
):

    selected_edges = []

    for edge_id, bit in enumerate(bits):

        if bit == 1:

            start, end, cost = roads[edge_id]

            selected_edges.append(
                (start, end, cost)
            )

    # Build selected graph
    adjacency = {}

    for start, end, cost in selected_edges:

        adjacency.setdefault(
            start,
            []
        ).append(
            (end, cost)
        )

    route = [source]
    current = source
    visited = set()

    while current != target:

        if current in visited:
            break

        visited.add(current)

        if current not in adjacency:
            break

        next_nodes = adjacency[current]

        if len(next_nodes) == 0:
            break

        next_node = next_nodes[0][0]

        route.append(
            next_node
        )

        current = next_node

    return route


# ---------------------------------------------------------
# ROUTE COST
# ---------------------------------------------------------

def calculate_route_cost(
    bits,
    roads
):

    cost = 0

    for edge_id, bit in enumerate(bits):

        if bit == 1:

            cost += roads[edge_id][2]

    return cost