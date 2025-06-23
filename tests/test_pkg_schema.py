from unittest.mock import Mock, patch

from ingestion.build_pkg import build_pkg


def test_hallucinated_node_rejected():
    # mock transformer to emit a forbidden node type
    mock_triplet = Mock()
    mock_triplet.subject_type = "Wizard"
    mock_triplet.object_type = "Person"
    mock_triplet.predicate = "MENTIONS"
    mock_triplet.subject = "Gandalf"
    mock_triplet.object = "Alice"

    with patch(
        "ingestion.build_pkg._load_docs",
        return_value=[Mock(page_content="lore")],
    ), patch("ingestion.build_pkg.LLMGraphTransformer") as fake_tf, patch(
        "ingestion.build_pkg.CallbackHandler",
        return_value=Mock(),
    ), patch("ingestion.build_pkg.GraphDatabase.driver"):
        fake_tf.return_value.convert_to_graph_documents.return_value = [
            Mock(relationships=[mock_triplet])
        ]
        added = build_pkg("query", None)
    assert added == 0





