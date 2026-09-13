from popretrieve import __version__, available_scorers
from popretrieve.evaluation import retrieval_metrics


def test_public_namespace_contract():
    assert __version__ == "0.1.0"
    assert "energy" in available_scorers()
    assert "mean_cosine" in available_scorers()


def test_public_evaluation_alias():
    result = retrieval_metrics([[1.0, 0.0]], [0])
    assert result["hit@1"] == 1.0

