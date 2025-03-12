from fastapi import APIRouter
from pydantic import BaseModel, conlist
from typing import List, Dict, Optional
from openai import OpenAI
import os
import json

class ClassifyStatusRequest(BaseModel):
    statuses: conlist(str, min_length=1, max_length=100)

class ClassifyStatusResponse(BaseModel):
    status_name: str
    status_type: str
    substatus_type: Optional[str] = None

class ClassifyStatusAPIResponse(BaseModel):
    classified_statuses: List[ClassifyStatusResponse]
    tokens_used: Dict[str, int]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
        "Traffic Delays"
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
        "Pick Up Confirmed"
    ]
}

SYSTEM_PROMPT = f"""
Classify each status into a status type and substatus type based on the following category dictionary
delimited by triple backticks:
```{STATUS_CATEGORIES_DICT}```

- The keys from the category dictionary are status types, and their values are valid substatus types.
- The status type should never be `null`. If a status cannot be classified into any specific status type,
return `Transit` as the status type.
- If a status type allows `null`, the substatus type may be `null` only if no better match exists
or the status is ambiguous.
- Only return valid combinations from the given dictionary.
- If the status is too ambiguous to classify accurately, return `Transit` as the `status_type`
and `null` for the `substatus_type`.
"""

router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)

@router.post("/classify", response_model=ClassifyStatusAPIResponse)
async def classify_statuses(request: ClassifyStatusRequest):
    """
    Classifies a list of status descriptions into predefined status types and substatus types.

        Args:
            request (ClassifyStatusRequest): A request object containing a list of status descriptions.

        Returns:
            dict: A response containing:
                - classified_statuses (List[ClassifyStatusResponse]): A list of classified statuses with
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
    classified_statuses, tokens_used = classify_statuses_batch(request.statuses)
    return {"classified_statuses": classified_statuses, "tokens_used": tokens_used}

def classify_statuses_batch(statuses: List[str]):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify these statuses delimited by triple backticks ```{statuses}```"}
        ],
        tools=function_definitions(),
        temperature=0.5
    )

    # Extract classified_statuses from function definition
    classified_statuses = json.loads(
        response.choices[0].message.tool_calls[0].function.arguments
    )["classified_statuses"]

    # Extract token usage from response
    tokens_used = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

    return classified_statuses, tokens_used

def function_definitions():
    return [{
        'type': 'function',
        'function': {
            'name': 'classify_statuses',
            'description': 'Get an array of statuses classified by status type and substatus type',
            'parameters': {
                'type': 'object',
                'properties': {
                    'classified_statuses': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'status_name': {
                                    'type': 'string',
                                    'description': 'Name of status'
                                },
                                'status_type': {
                                    'type': 'string',
                                    'description': 'Status type of status'
                                },
                                'substatus_type': {
                                    'type': 'string',
                                    'description': 'Substatus type of status'
                                }
                            },
                            'required': ['status_name', 'status_type', 'substatus_type']
                        }
                    }
                }
            }
        }
    }]
