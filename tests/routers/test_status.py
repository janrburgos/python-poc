import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
# Mock client specific for OpenAI for now
def mock_llm_client(mocker):
    mock_openai = mocker.patch("app.services.status_classification.gpt.OpenAI")

    mock_client = mock_openai.return_value
    mock_response = mocker.MagicMock()

    mock_response.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(
                tool_calls=[
                    mocker.MagicMock(
                        function=mocker.MagicMock(
                            arguments=json.dumps(
                                {
                                    "classified_statuses": [
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
                                }
                            )
                        )
                    )
                ]
            )
        )
    ]

    mock_response.usage.prompt_tokens = 15
    mock_response.usage.completion_tokens = 10
    mock_response.usage.total_tokens = 25

    mock_client.chat.completions.create.return_value = mock_response
    return mock_openai


def test_classify(mock_llm_client):
    """Test classify status API endpoint."""

    response = client.post(
        "/status/classify",
        json={
            "statuses": ["shipment has been cancelled", "package is in transit"],
            "llm": "gpt",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "classified_statuses": [
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
        ],
        "tokens_used": {
            "prompt_tokens": 15,
            "completion_tokens": 10,
            "total_tokens": 25,
        },
    }


def test_classify_statuses_invalid_input():
    """Test validation error when input is not a list of statuses."""
    response = client.post("/status/classify", json={"statuses": "invalid input"})
    assert response.status_code == 422


def test_classify_statuses_unsupported_llm():
    """Test error handling for an unsupported LLM."""
    response = client.post(
        "/status/classify",
        json={"statuses": ["shipment has been cancelled"], "llm": "unsupported_model"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "LLM 'unsupported_model' is not implemented for status classification. Please use a supported model."
    }
