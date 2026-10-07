import csv
from pathlib import Path

from classical_route import (
    create_road_network,
    find_classical_route
)

from qubo_model import (
    build_qubo,
    find_best_qubo_solution,
    decode_route as decode_qubo_route,
    calculate_route_cost as calculate_qubo_cost
)

from qaoa import (
    optimize_qaoa,
    get_best_feasible_solution,
    decode_route as decode_qaoa_route,
    calculate_route_cost as calculate_qaoa_cost
)


# =========================================================
# PROJECT DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

DATA_DIR.mkdir(
    exist_ok=True
)

RESULTS_DIR.mkdir(
    exist_ok=True
)


ROAD_FILE = DATA_DIR / "road_network.csv"


# =========================================================
# DEFAULT ROAD NETWORK
# =========================================================

DEFAULT_ROADS = [
    ("Start", "A", 4),
    ("Start", "B", 2),
    ("A", "C", 3),
    ("A", "Hospital", 7),
    ("B", "C", 1),
    ("B", "Hospital", 8),
    ("C", "Hospital", 2),
]


# =========================================================
# CREATE DEFAULT DATA FILE
# =========================================================

def create_default_road_file():

    with open(
        ROAD_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Road ID",
            "Start Node",
            "End Node",
            "Travel Cost"
        ])

        for road_id, (
            start,
            end,
            cost
        ) in enumerate(DEFAULT_ROADS):

            writer.writerow([
                road_id,
                start,
                end,
                cost
            ])


# =========================================================
# LOAD ROAD NETWORK
# =========================================================

def load_roads():

    if not ROAD_FILE.exists():

        create_default_road_file()

        print(
            "Created default road_network.csv"
        )

    roads = []

    with open(
        ROAD_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            roads.append(
                (
                    row["Start Node"],
                    row["End Node"],
                    float(row["Travel Cost"])
                )
            )

    return roads


# =========================================================
# FORMAT ROUTE
# =========================================================

def format_route(route):

    return " -> ".join(route)


# =========================================================
# SAVE CLASSICAL RESULT
# =========================================================

def save_classical_result(
    route,
    cost
):

    path = RESULTS_DIR / "classical_result.txt"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "CLASSICAL SHORTEST-PATH RESULT\n"
        )

        file.write(
            "================================\n"
        )

        file.write(
            f"Route: {format_route(route)}\n"
        )

        file.write(
            f"Travel cost: {cost}\n"
        )

        file.write(
            "Feasible: Yes\n"
        )


# =========================================================
# SAVE QUBO RESULT
# =========================================================

def save_qubo_result(
    bits,
    energy,
    selected_edges,
    travel_cost
):

    path = RESULTS_DIR / "qubo_result.txt"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "QUBO RESULT\n"
        )

        file.write(
            "===========\n"
        )

        file.write(
            f"Binary variables: {bits}\n"
        )

        file.write(
            f"QUBO energy: {energy}\n"
        )

        file.write(
            f"Travel cost: {travel_cost}\n"
        )

        file.write(
            "Feasible: Yes\n\n"
        )

        file.write(
            "Selected roads:\n"
        )

        for start, end, cost in selected_edges:

            file.write(
                f"{start} -> {end} "
                f"(cost={cost})\n"
            )


# =========================================================
# SAVE QAOA RESULT
# =========================================================

def save_qaoa_result(
    bits,
    probability,
    route,
    travel_cost,
    num_qubits
):

    path = RESULTS_DIR / "qaoa_result.txt"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "QAOA RESULT\n"
        )

        file.write(
            "===========\n"
        )

        file.write(
            f"Binary variables: {bits}\n"
        )

        file.write(
            f"Probability: {probability}\n"
        )

        file.write(
            "Feasible: Yes\n"
        )

        file.write(
            f"Route: {format_route(route)}\n"
        )

        file.write(
            f"Travel cost: {travel_cost}\n\n"
        )

        file.write(
            "QAOA Configuration\n"
        )

        file.write(
            "-------------------\n"
        )

        file.write(
            f"Number of qubits: {num_qubits}\n"
        )

        file.write(
            "QAOA depth: p = 2\n"
        )

        file.write(
            "Simulation: Statevector\n"
        )


# =========================================================
# SAVE COMPARISON
# =========================================================

def save_comparison(
    classical_route,
    classical_cost,
    qubo_route,
    qubo_cost,
    qaoa_route,
    qaoa_cost
):

    path = RESULTS_DIR / "comparison.csv"

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Method",
            "Route",
            "Travel Cost",
            "Feasible"
        ])

        writer.writerow([
            "Classical",
            format_route(classical_route),
            classical_cost,
            "Yes"
        ])

        writer.writerow([
            "QUBO",
            format_route(qubo_route),
            qubo_cost,
            "Yes"
        ])

        writer.writerow([
            "QAOA",
            format_route(qaoa_route),
            qaoa_cost,
            "Yes"
        ])


# =========================================================
# SAVE SUMMARY
# =========================================================

def save_summary(
    classical_route,
    classical_cost,
    qubo_route,
    qubo_cost,
    qaoa_route,
    qaoa_cost,
    num_qubits
):

    path = RESULTS_DIR / "summary.txt"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "QUANTUM OPTIMIZATION OF "
            "EMERGENCY VEHICLE ROUTES\n"
        )

        file.write(
            "====================================\n\n"
        )

        file.write(
            "CLASSICAL RESULT\n"
        )

        file.write(
            f"Route: {format_route(classical_route)}\n"
        )

        file.write(
            f"Cost: {classical_cost}\n\n"
        )

        file.write(
            "QUBO RESULT\n"
        )

        file.write(
            f"Route: {format_route(qubo_route)}\n"
        )

        file.write(
            f"Cost: {qubo_cost}\n\n"
        )

        file.write(
            "QAOA RESULT\n"
        )

        file.write(
            f"Route: {format_route(qaoa_route)}\n"
        )

        file.write(
            f"Cost: {qaoa_cost}\n"
        )

        file.write(
            f"Qubits: {num_qubits}\n\n"
        )

        file.write(
            "CONCLUSION\n"
        )

        if qaoa_cost == classical_cost:

            file.write(
                "QAOA matched the classical optimum "
                "in this experiment.\n"
            )

        else:

            file.write(
                "QAOA produced a feasible route but "
                "did not reach the classical optimum "
                "in this experiment.\n"
            )

        file.write(
            "\nNo quantum advantage is claimed.\n"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n")
    print("=" * 55)
    print("QUANTUM EMERGENCY VEHICLE ROUTE OPTIMIZATION")
    print("=" * 55)

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    roads = load_roads()

    num_qubits = len(roads)

    print(
        f"\nLoaded {len(roads)} roads."
    )

    print(
        f"Required qubits: {num_qubits}"
    )

    # -----------------------------------------------------
    # DISPLAY ROADS
    # -----------------------------------------------------

    print("\nROAD NETWORK")
    print("------------")

    for index, (
        start,
        end,
        cost
    ) in enumerate(roads):

        print(
            f"x{index}: "
            f"{start} -> {end} "
            f"(cost={cost})"
        )

    # =====================================================
    # 1. CLASSICAL
    # =====================================================

    print("\n")
    print("1. CLASSICAL SOLUTION")
    print("---------------------")

    graph = create_road_network(
        roads
    )

    classical_route, classical_cost = (
        find_classical_route(
            graph,
            source="Start",
            target="Hospital"
        )
    )

    print(
        "Route:",
        format_route(classical_route)
    )

    print(
        "Travel cost:",
        classical_cost
    )

    save_classical_result(
        classical_route,
        classical_cost
    )

    # =====================================================
    # 2. QUBO
    # =====================================================

    print("\n")
    print("2. QUBO SOLUTION")
    print("----------------")

    qubo, constraints = build_qubo(
        roads,
        source="Start",
        target="Hospital"
    )

    qubo_bits, qubo_energy = (
        find_best_qubo_solution(
            qubo,
            constraints,
            num_qubits
        )
    )

    qubo_selected_edges = decode_qubo_route(
        qubo_bits,
        roads
    )

    qubo_cost = calculate_qubo_cost(
        qubo_bits,
        roads
    )

    print(
        "Binary variables:",
        qubo_bits
    )

    print(
        "QUBO energy:",
        qubo_energy
    )

    print(
        "Travel cost:",
        qubo_cost
    )

    print(
        "Selected roads:"
    )

    for start, end, cost in qubo_selected_edges:

        print(
            f"{start} -> {end}"
        )

    # Convert selected edges to ordered route
    qubo_route = decode_qaoa_route(
        qubo_bits,
        roads
    )

    save_qubo_result(
        qubo_bits,
        qubo_energy,
        qubo_selected_edges,
        qubo_cost
    )

    # =====================================================
    # 3. QAOA
    # =====================================================

    print("\n")
    print("3. QAOA SOLUTION")
    print("----------------")

    print(
        "Optimizing QAOA..."
    )

    (
        parameters,
        hamiltonian,
        final_state,
        final_expectation
    ) = optimize_qaoa(
        qubo,
        num_qubits,
        p=2
    )

    print(
        "QAOA optimization completed."
    )

    print(
        "Final expectation value:",
        final_expectation
    )

    qaoa_bits, qaoa_probability = (
        get_best_feasible_solution(
            final_state,
            constraints,
            num_qubits
        )
    )

    if qaoa_bits is None:

        print(
            "\nNo feasible QAOA solution found."
        )

        return

    qaoa_route = decode_qaoa_route(
        qaoa_bits,
        roads
    )

    qaoa_cost = calculate_qaoa_cost(
        qaoa_bits,
        roads
    )

    print(
        "\nBest feasible QAOA solution:"
    )

    print(
        "Binary variables:",
        qaoa_bits
    )

    print(
        "Probability:",
        qaoa_probability
    )

    print(
        "Valid route: YES"
    )

    print(
        "Route:",
        format_route(qaoa_route)
    )

    print(
        "Travel cost:",
        qaoa_cost
    )

    save_qaoa_result(
        qaoa_bits,
        qaoa_probability,
        qaoa_route,
        qaoa_cost,
        num_qubits
    )

    # =====================================================
    # 4. COMPARISON
    # =====================================================

    print("\n")
    print("4. FINAL COMPARISON")
    print("-------------------")

    print(
        f"Classical: "
        f"{format_route(classical_route)} "
        f"| Cost = {classical_cost}"
    )

    print(
        f"QUBO: "
        f"{format_route(qubo_route)} "
        f"| Cost = {qubo_cost}"
    )

    print(
        f"QAOA: "
        f"{format_route(qaoa_route)} "
        f"| Cost = {qaoa_cost}"
    )

    save_comparison(
        classical_route,
        classical_cost,
        qubo_route,
        qubo_cost,
        qaoa_route,
        qaoa_cost
    )

    save_summary(
        classical_route,
        classical_cost,
        qubo_route,
        qubo_cost,
        qaoa_route,
        qaoa_cost,
        num_qubits
    )

    # =====================================================
    # DONE
    # =====================================================

    print("\n")
    print("=" * 55)
    print("ALL RESULTS GENERATED SUCCESSFULLY")
    print("=" * 55)

    print("\ndata/")
    print("  └── road_network.csv")

    print("\nresults/")
    print("  ├── classical_result.txt")
    print("  ├── qubo_result.txt")
    print("  ├── qaoa_result.txt")
    print("  ├── comparison.csv")
    print("  └── summary.txt")


if __name__ == "__main__":
    main()