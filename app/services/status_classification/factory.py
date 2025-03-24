from app.services.status_classification.ft_gpt import FTGPTStatusClassifier
from app.services.status_classification.gpt import GPTStatusClassifier
from app.services.status_classification.claude import ClaudeStatusClassifier
from app.services.status_classification.gemini import GeminiStatusClassifier


class UnsupportedLLMError(Exception):
    """Raised when the requested LLM is not implemented in the system."""

    def __init__(self, llm: str):
        self.llm = llm
        super().__init__(
            f"LLM '{llm}' is not implemented for status classification. Please use a supported model."
        )


class LLMStatusClassifierFactory:
    @staticmethod
    def get_classifier(llm: str):
        llm = llm.lower()
        if llm == "ft-gpt":
            return FTGPTStatusClassifier()
        if llm == "gpt":
            return GPTStatusClassifier()
        elif llm == "claude":
            return ClaudeStatusClassifier()
        elif llm == "gemini":
            return GeminiStatusClassifier()
        else:
            raise UnsupportedLLMError(llm)
