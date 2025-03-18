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
            contents=self._generate_primary_user_prompt(statuses),
            config=types.GenerateContentConfig(
                system_instruction=self._generate_system_prompt(
                    kwargs["status_categories_dict"]
                ),
                max_output_tokens=8_000,
                temperature=0.1,
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
