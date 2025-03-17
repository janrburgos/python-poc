import pytest

from app.services.status_classification.factory import LLMStatusClassifierFactory
from app.services.status_classification.gemini import GeminiStatusClassifier


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
    mock_genai = mocker.patch("app.services.status_classification.gemini.genai.Client")
    mock_client = mock_genai.return_value
    mock_response = mocker.MagicMock()

    mock_response.parsed = mock_classified_statuses
    mock_response.usage_metadata.candidates_token_count = 10
    mock_response.usage_metadata.prompt_token_count = 20
    mock_response.usage_metadata.total_token_count = 30

    mock_client.models.generate_content.return_value = mock_response

    return mock_client


def test_classify(mock_llm_client, mock_classified_statuses):
    """Test successful classification with mocked Gemini client."""

    test_statuses = ["shipment has been cancelled", "package is in transit"]
    test_status_categories_dict = {}

    classifier = LLMStatusClassifierFactory.get_classifier("gemini")
    result = classifier.classify(
        test_statuses, status_categories_dict=test_status_categories_dict
    )

    expected_tokens = {
        "candidates_token_count": 10,
        "prompt_token_count": 20,
        "total_token_count": 30,
    }

    assert isinstance(classifier, GeminiStatusClassifier)
    assert result == (mock_classified_statuses, expected_tokens)
