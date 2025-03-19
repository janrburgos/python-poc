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
            system=self._generate_system_prompt(kwargs["status_categories_dict"]),
            messages=[
                {
                    "role": "user",
                    "content": self._generate_primary_user_prompt(statuses),
                },
            ],
            tools=self.__get_function_schema(),
            temperature=0.0,
            max_tokens=8_000,
        )

        classified_statuses = []

        # Extract classified_statuses from function definition
        for content_block in response.content:
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

    def __get_function_schema(self) -> List[Dict]:
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

    def _generate_primary_user_prompt(self, statuses: List[str]) -> str:
        return f"Classify these statuses delimited by triple backticks ```{statuses}```"
