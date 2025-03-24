import pytest
import json
from app.services.status_classification.ft_gpt import FTGPTStatusClassifier
from app.services.status_classification.factory import LLMStatusClassifierFactory


@pytest.fixture
def mock_classified_status():
    return {
        "status_name": "shipment has been cancelled",
        "status_type": "Exception",
        "substatus_type": "Cancelled",
    }


@pytest.fixture
def mock_openai_client(mocker, mock_classified_status):
    mock_openai = mocker.patch("app.services.status_classification.ft_gpt.OpenAI")
    mock_client = mock_openai.return_value

    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.tool_calls[0].function.arguments = json.dumps(
        mock_classified_status
    )

    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def test_classify(mock_openai_client, mock_classified_status):
    """Test classify function of FTGPTStatusClassifier."""
    classifier = LLMStatusClassifierFactory.get_classifier("ft-gpt")
    statuses = ["shipment has been cancelled"]
    result = classifier.classify(
        statuses, status_categories_dict={"Exception": ["Cancelled"]}
    )

    expected_tokens = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
    }

    assert isinstance(classifier, FTGPTStatusClassifier)
    assert result == ([mock_classified_status], expected_tokens)
