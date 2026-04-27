try:
    from .rest import app  # noqa: F401
except Exception:
    app = None  # type: ignore
