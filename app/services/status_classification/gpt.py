import os
import json
from typing import List, Dict
from openai import OpenAI
from app.services.status_classification.base import LLMStatusClassifier

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class GPTStatusClassifier(LLMStatusClassifier):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def classify(
        self, statuses: List[str], **kwargs
    ) -> tuple[List[Dict[str, str]], Dict[str, int]]:

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": self.generate_system_prompt(
                        kwargs["status_categories_dict"]
                    ),
                },
                {
                    "role": "user",
                    "content": f"Classify these statuses delimited by triple backticks ```{statuses}```",
                },
            ],
            tools=self.get_function_schema(),
            temperature=0.5,
            max_tokens=10_000,
        )

        # Extract classified_statuses from function definition
        classified_statuses = json.loads(
            response.choices[0].message.tool_calls[0].function.arguments
        )["classified_statuses"]

        # Extract token usage from response
        tokens_used = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        return classified_statuses, tokens_used

    def generate_system_prompt(self, status_categories_dict):
        return f"""
               Classify each status into a status type and substatus type based on the following category dictionary
               delimited by triple backticks:
               ```{status_categories_dict}```

               - The keys from the category dictionary are status types, and their values are valid substatus types.
               - The status type should never be `null`. If a status cannot be classified into any specific status type,
               return `Transit` as the status type.
               - If a status type allows `null`, the substatus type may be `null` only if no better match exists
               or the status is ambiguous.
               - Only return valid combinations from the given dictionary.
               - If the status is too ambiguous to classify accurately, return `Transit` as the `status_type`
               and `null` for the `substatus_type`.
               """

    def get_function_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "classify_statuses",
                    "description": "Get an array of statuses classified by status type and substatus type",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "classified_statuses": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "status_name": {
                                            "type": "string",
                                            "description": "Name of status",
                                        },
                                        "status_type": {
                                            "type": "string",
                                            "description": "Status type of status",
                                        },
                                        "substatus_type": {
                                            "type": "string",
                                            "description": "Substatus type of status",
                                        },
                                    },
                                    "required": [
                                        "status_name",
                                        "status_type",
                                    ],
                                },
                            }
                        },
                    },
                },
            }
        ]
