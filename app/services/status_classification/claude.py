import os
from typing import List, Dict
from anthropic import Anthropic
from app.services.status_classification.base import LLMStatusClassifier

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class ClaudeStatusClassifier(LLMStatusClassifier):
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def classify(
        self, statuses: List[str], **kwargs
    ) -> tuple[List[Dict[str, str]], Dict[str, int]]:

        response = self.client.messages.create(
            model="claude-3-5-haiku-20241022",
            system=self.generate_system_prompt(kwargs["status_categories_dict"]),
            messages=[
                {
                    "role": "user",
                    "content": f"Classify these statuses delimited by triple backticks ```{statuses}```",
                },
            ],
            tools=self.get_function_schema(),
            temperature=0.1,
            max_tokens=8_000,
        )

        classified_statuses = []

        # Extract classified_statuses from function definition
        for content_block in response.content:
            print(content_block)
            if content_block.type == "tool_use":
                classified_statuses = content_block.input["classified_statuses"]
                break

        # Extract token usage from response
        tokens_used = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
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
                "name": "classify_statuses",
                "description": "Get an array of statuses classified by status type and substatus type",
                "input_schema": {
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
            }
        ]
