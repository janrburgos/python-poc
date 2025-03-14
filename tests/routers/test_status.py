import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_openai_client(mocker):
    mock_client = mocker.patch("app.routers.status.client")

    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.tool_calls[0].function.arguments = json.dumps(
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
    mock_response.usage.prompt_tokens = 15
    mock_response.usage.completion_tokens = 10
    mock_response.usage.total_tokens = 25

    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def test_classify_statuses(mock_openai_client):
    response = client.post(
        "/status/classify",
        json={"statuses": ["shipment has been cancelled", "package is in transit"]},
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
    response = client.post("/status/classify", json={"statuses": "invalid input"})
    assert response.status_code == 422
