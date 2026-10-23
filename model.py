"""
The Model: Pure data + one lookup function. No API calls, no side effects on import.
Contains available Claude models and the default.

"""

MODELS = {
    "opus": "claude-opus-5-5",
    "sonnet": "claude-sonnet-5-5",
    "haiku": "claude-haiku-5-5",
    "fable": "claude-fable-5-1",
}

DEFAULT_MODEL = "opus"


def get_model(model_name: str) -> str:
    """
    Return the model ID for a friendly name like 'opus'.
    Raises ValueError if unknown.
    """
    key = model_name.strip().lower()
    if key not in MODELS:
        raise ValueError(
            f"Unknown model name: {model_name}. Please choose from: {', '.join(MODELS)}"
        )

    return MODELS[key]


def list_models() -> list[str]:
    return list(MODELS.keys())
