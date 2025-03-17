import os
from typing import List, Dict
from google import genai
from google.genai import types
from app.services.status_classification.base import LLMStatusClassifier
from app.models.status_classification import StatusClassificationResponse

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiStatusClassifier(LLMStatusClassifier):
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def classify(
        self, statuses: List[str], **kwargs
    ) -> tuple[List[Dict[str, str]], Dict[str, int]]:

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=f"Classify these statuses delimited by triple backticks ```{statuses}```",
            config=types.GenerateContentConfig(
                system_instruction=self.generate_system_prompt(
                    kwargs["status_categories_dict"]
                ),
                max_output_tokens=8_000,
                temperature=0.5,
                response_mime_type="application/json",
                response_schema=list[StatusClassificationResponse],
            ),
        )

        # Extract token usage from response
        tokens_used = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count,
        }

        return response.parsed, tokens_used

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
