try:
    from .gradio_app import launch  # noqa: F401
except Exception:
    launch = None  # type: ignore
