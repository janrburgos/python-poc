import pytest
from app.services.status_classification.claude import ClaudeStatusClassifier
from app.services.status_classification.factory import LLMStatusClassifierFactory


@pytest.fixture
def mock_classified_statuses():
    return [
        {
            "status_name": "shipment has been cancelled",
            "status_type": "Exception",
            "substatus_type": "Cancelled",
        },
        {
            "status_name": "package is in transit",
            "status_type": "Transit",
            "substatus_type": None,
        },
    ]


@pytest.fixture
def mock_llm_client(mocker, mock_classified_statuses):
    mock_anthropic = mocker.patch("app.services.status_classification.claude.Anthropic")
    mock_client = mock_anthropic.return_value
    mock_response = mocker.MagicMock()

    mock_response.content = [
        mocker.MagicMock(
            type="tool_use",
            input={"classified_statuses": mock_classified_statuses},
        )
    ]

    mock_response.usage.input_tokens = 15
    mock_response.usage.output_tokens = 10

    mock_response.usage.total_tokens = (
        mock_response.usage.input_tokens + mock_response.usage.output_tokens
    )

    mock_client.messages.create.return_value = mock_response

    return mock_client


def test_classify(mock_llm_client, mock_classified_statuses):
    """Test classify function of ClaudeStatusClassifier."""
    classifier = LLMStatusClassifierFactory.get_classifier("claude")
    result = classifier.classify(
        ["shipment has been cancelled", "package is in transit"],
        status_categories_dict={},
    )

    expected_tokens = {"input_tokens": 15, "output_tokens": 10, "total_tokens": 25}

    assert isinstance(classifier, ClaudeStatusClassifier)
    assert result == (mock_classified_statuses, expected_tokens)
