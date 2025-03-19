from abc import ABC, abstractmethod
from typing import List, Dict


class LLMStatusClassifier(ABC):
    """
    Abstract base class for LLM classifiers.
    """

    @abstractmethod
    def classify(
        self, statuses: List[str]
    ) -> tuple[List[Dict[str, str]], Dict[str, int]]:
        pass

    def _generate_primary_user_prompt(self, status: str) -> str:
        return f"Classify this status delimited by triple backticks ```{status}```"

    def _generate_system_prompt(self, status_categories_dict) -> str:
        return f"""
               Classify the given status (or statuses) into a status type and substatus type based on the
               following category dictionary delimited by triple backticks:
               ```{status_categories_dict}```

               - The keys from the category dictionary are status types, and their values are their only
               valid substatus types.
               - The status type must not be `null`. If a status cannot be classified into any specific
               status type, return `Transit` as the status type.
               - If the chosen status type has `null` substatus_type, the substatus type of the given status
               may be `null` only if no better match exists or the status is too ambiguous.
               - Only return valid combinations of status type and substatus type from the given dictionary.
               - If the status is too ambiguous to classify accurately, return `Transit` as the `status_type`
               and `null` for the `substatus_type`.
               - You must return a result for each status. Do not omit or clean any statuses.
               """
