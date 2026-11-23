def next_node(edges, node, state):
    target = edges.get(node, "END")
    if callable(target):
        target = target(state)
    return target


def run_graph(nodes, edges, start, state, max_steps=20):
    path = []
    node = start
    while node != "END":
        path.append(node)
        if len(path) > max_steps:
            raise RuntimeError("recursion limit reached")
        state.update(nodes[node](state))
        node = next_node(edges, node, state)
    return {"state": state, "path": path}
