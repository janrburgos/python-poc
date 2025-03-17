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
