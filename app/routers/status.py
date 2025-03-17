from fastapi import APIRouter, HTTPException
from app.models.status_classification import (
    StatusClassificationRequest,
    StatusClassificationAPIResponse,
)
from app.services.status_classification.factory import (
    LLMStatusClassifierFactory,
    UnsupportedLLMError,
)

STATUS_CATEGORIES_DICT = {
    "Exception": [
        "Cancelled",
        "Carrier Delays",
        "Claims Issued",
        "Customs/Tax Delays",
        "Delayed",
        "Incorrect Info",
        "Loss/Returns",
        "Natural Causes",
        "Other Delays",
        "Returned",
        "Traffic Delays",
    ],
    "Info": [None],
    "Transit": [
        None,
        "Customs/Tax Delays",
        "Delayed",
        "Delivered",
        "Documents Handover",
        "Incorrect Info",
        "Onboard at Departure Terminal",
        "Other Delays",
        "Pick Up Confirmed",
    ],
}

router = APIRouter()


@router.post("/classify", response_model=StatusClassificationAPIResponse)
async def classify_statuses(request: StatusClassificationRequest):
    """
    Classifies a list of status descriptions into predefined status types and substatus types.

        Args:
            request (StatusClassificationRequest): A request object containing a list of status descriptions.

        Returns:
            dict: A response containing:
                - classified_statuses (List[StatusClassificationResponse]): A list of classified statuses with
                  their status type and substatus type.
                - tokens_used (Dict[str, int]): A dictionary showing token usage details.

        Example:
            Request:
            {
                "statuses": ["shipment has been cancelled", "package is in transit"]
            }

            Response:
            {
                "classified_statuses": [
                    {
                        "status_name": "shipment has been cancelled",
                        "status_type": "Exception", "substatus_type": "Cancelled"
                    },
                    {
                        "status_name": "package is in transit",
                        "status_type": "Transit", "substatus_type": null
                    }
                ],
                "tokens_used": {
                    "prompt_tokens": 15,
                    "completion_tokens": 10,
                    "total_tokens": 25
                }
            }
    """

    try:
        classifier = LLMStatusClassifierFactory.get_classifier(request.llm)

        classified_statuses, tokens_used = classifier.classify(
            request.statuses, status_categories_dict=STATUS_CATEGORIES_DICT
        )
    except UnsupportedLLMError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StatusClassificationAPIResponse(
        classified_statuses=classified_statuses, tokens_used=tokens_used
    )
