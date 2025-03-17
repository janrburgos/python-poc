from app.services.status_classification.gpt import GPTStatusClassifier


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
        if llm == "gpt":
            return GPTStatusClassifier()
        else:
            raise UnsupportedLLMError(llm)
