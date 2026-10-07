import networkx as nx


def create_road_network(roads):
    """
    Create a directed weighted graph from road data.

    roads format:
    [
        ("Start", "A", 4),
        ("Start", "B", 2),
        ...
    ]
    """

    graph = nx.DiGraph()

    for start, end, cost in roads:
        graph.add_edge(start, end, weight=cost)

    return graph


def find_classical_route(graph, source="Start", target="Hospital"):
    """
    Find the minimum-cost route using Dijkstra's algorithm.
    """

    route = nx.shortest_path(
        graph,
        source=source,
        target=target,
        weight="weight"
    )

    distance = nx.shortest_path_length(
        graph,
        source=source,
        target=target,
        weight="weight"
    )

    return route, distance


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

    graph = create_road_network(roads)

    route, distance = find_classical_route(graph)

    print("Emergency Vehicle Route")
    print("-----------------------")
    print("Optimal route:", " -> ".join(route))
    print("Total travel cost:", distance)