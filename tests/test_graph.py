from agent.graph import ExtractionState, create_extraction_graph

def test_extraction_state_has_required_fields():
    state = ExtractionState
    assert 'pdf_path' in state.__annotations__
    assert 'chunks' in state.__annotations__
    assert 'extraction_results' in state.__annotations__
    assert 'csv_output_path' in state.__annotations__

def test_create_graph_returns_state_graph():
    graph = create_extraction_graph()
    assert graph is not None
