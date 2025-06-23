from unittest.mock import Mock, patch

from langchain_experimental.graph_transformers.llm import (
    Node,
    Relationship,
    GraphDocument,
)
from ingestion.build_pkg import build_pkg, _convert_filter


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


def test_convert_filter_strips_invalid_triples():
    fake_transformer = Mock()
    handler = Mock()
    from langchain_core.documents import Document

    doc = Document(page_content="stuff")
    valid_a = Node(id="Alice", type="Person")
    valid_b = Node(id="Acme", type="Company")
    good_rel = Relationship(source=valid_a, target=valid_b, type="EMPLOYED_AT")
    bad_node = Node(id="Gandalf", type="Wizard")
    bad_rel = Relationship(source=bad_node, target=valid_a, type="MENTIONS")
    gdoc = GraphDocument(
        nodes=[valid_a, valid_b, bad_node],
        relationships=[good_rel, bad_rel],
        source=doc,
    )
    fake_transformer.convert_to_graph_documents.return_value = [gdoc]

    triples = _convert_filter(fake_transformer, [doc], handler)

    assert triples == [
        (
            "Alice",
            "Person",
            "EMPLOYED_AT",
            "Acme",
            "Company",
        )
    ]





