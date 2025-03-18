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
                    "content": self._generate_system_prompt(
                        kwargs["status_categories_dict"]
                    ),
                },
                {
                    "role": "user",
                    "content": self._generate_primary_user_prompt(statuses),
                },
            ],
            tools=self.__get_function_schema(),
            temperature=0.1,
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

    def __get_function_schema(self):
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
