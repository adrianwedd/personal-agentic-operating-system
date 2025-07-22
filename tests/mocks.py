from langchain_core.messages import AIMessage

class DummyChatModel:
    def __init__(self, *_, **__):
        self.invoked = False
    def invoke(self, messages, **kwargs):
        self.invoked = True
        return AIMessage(content="ok")
    def stream(self, messages, **kwargs):
        self.invoked = True
        yield AIMessage(content="ok1")
        yield AIMessage(content="ok2")

class DummyEmbeddingModel:
    def __init__(self, *_, **__):
        pass
    def embed_documents(self, texts):
        return [[1.0, 0.0, 0.0] for _ in texts]

class DummyGenerativeModel:
    def __init__(self, *_, **__):
        pass
    def generate_content(self, content, stream=False):
        if stream:
            def _gen():
                for t in ["ok1", "ok2"]:
                    yield type("Resp", (), {"text": t})

            return _gen()
        return type("Resp", (), {"text": "ok"})

class DummyResponse:
    def __init__(self, json_data=None, lines=None):
        self._json = json_data or {}
        self._lines = lines or []
    def raise_for_status(self):
        pass
    def json(self):
        return self._json
    def iter_lines(self):
        for line in self._lines:
            yield line.encode()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
