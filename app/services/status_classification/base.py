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

    def _generate_primary_user_prompt(self, statuses):
        return f"Classify these statuses delimited by triple backticks ```{statuses}```"

    def _generate_system_prompt(self, status_categories_dict):
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
               - You must return the same status names as the input statuses.
               - You must return the same number of statuses as the number of input statuses.
               - These bullet points are not just mere suggestions, you must strictly follow them.
               """
