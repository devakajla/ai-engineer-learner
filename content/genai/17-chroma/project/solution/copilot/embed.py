"""Turn texts into vectors with a local model (no API key, no network after the first download)."""

MODEL_NAME = "BAAI/bge-small-en-v1.5"

_models = {}


def embed_texts(texts, model_name=MODEL_NAME):
    """Embed a list of texts. Returns one list of floats per text.

    The model is loaded the first time and kept, so later calls are fast.
    """
    if not texts:
        return []
    if model_name not in _models:
        from fastembed import TextEmbedding   # imported here so the rest of Copilot works without it

        _models[model_name] = TextEmbedding(model_name)
    return [vector.tolist() for vector in _models[model_name].embed(texts)]
