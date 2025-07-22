def test_build_graph(monkeypatch, tmp_path):
    import agent.graph as g
    monkeypatch.setattr(g, "HITL_DIR", tmp_path / "queue")
    # avoid writing image file
    from langgraph.graph import StateGraph as Graph
    monkeypatch.setattr(
        Graph,
        "draw_mermaid_png",
        lambda self, output_file_path: None,
        raising=False,
    )
    compiled = g.build_graph()
    nodes = set(compiled.get_graph().nodes)
    assert "prioritise" in nodes
    edges = {(e.source, e.target) for e in compiled.get_graph().edges}
    assert ("execute", "pause") in edges


def test_graph_layout():
    from agent.graph import graph_layout

    layout = graph_layout()
    node_ids = {n["id"] for n in layout["nodes"]}
    assert "plan" in node_ids
    edge_pairs = {(e["source"], e["target"]) for e in layout["edges"]}
    assert ("plan", "prioritise") in edge_pairs
