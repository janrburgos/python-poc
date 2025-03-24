import os
import json
from typing import List, Dict
from openai import OpenAI
from app.services.status_classification.base import LLMStatusClassifier

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class FTGPTStatusClassifier(LLMStatusClassifier):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def classify(
        self, statuses: List[str], **kwargs
    ) -> tuple[List[Dict[str, str]], Dict[str, int]]:

        classified_statuses = []
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0

        for status in statuses:
            classified_status, response_usage = self._classify_single_status(
                status, **kwargs
            )

            classified_statuses.append(classified_status)
            input_tokens += response_usage.prompt_tokens
            output_tokens += response_usage.completion_tokens
            total_tokens += response_usage.total_tokens

        tokens_used = {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

        return classified_statuses, tokens_used

    def _classify_single_status(
        self, status: str, **kwargs
    ) -> tuple[Dict[str, str], Dict[str, int]]:
        response = self.client.chat.completions.create(
            model=os.getenv("OPENAI_FINE_TUNED_MODEL"),
            messages=self.__generate_messages(status, **kwargs),
            tools=self.__get_function_schema(),
            temperature=0.0,
            max_tokens=10_000,
        )

        # Extract classified_statuses from function definition
        classified_status = json.loads(
            response.choices[0].message.tool_calls[0].function.arguments
        )

        return classified_status, response.usage

    def __get_function_schema(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "classify_status",
                    "description": "Get the status classified by status type and substatus type",
                    "parameters": {
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
                },
            }
        ]

    def __generate_messages(self, status: str, **kwargs) -> List[Dict[str, str]]:
        messages = [
            {
                "role": "system",
                "content": self._generate_system_prompt(
                    self.__generate_status_pairs(kwargs["status_categories_dict"])
                ),
            },
        ]

        messages.append(
            {
                "role": "user",
                "content": self._generate_user_prompt(status),
            }
        )

        return messages

    def _generate_system_prompt(
        self, status_pairs: List[tuple[str, str | None]]
    ) -> str:
        return f"""
               Classify the given status into a status type and substatus type using only these valid pairs:
               {status_pairs}. Do not invent or mix status types and substatus types.
               If the status is only composed of numbers, use this pair: ('Info', None).
               If you cannot determine a better classification or if the status is too ambiguous,
               use this pair as default: ('Transit', None).
               """

    def _generate_user_prompt(self, status: str) -> str:
        return f"Classify the status: `{status}`"

    def __generate_status_pairs(
        self, status_categories_dict: Dict
    ) -> List[tuple[str, str | None]]:
        return [(k, v) for k, values in status_categories_dict.items() for v in values]
