"""View exports for Streamlit pages.

Views are imported lazily via __getattr__ to prevent:
  - Streamlit ScriptRunContext warnings on bare import
  - Cascade failures when a view-level dependency (joblib, shap) is missing
  - Unnecessary module loading on pages that don't need every view
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.views.auditor import render_auditor
    from app.views.dashboard import (
        render_anomaly_page,
        render_dashboard,
        render_forecasting_page,
    )
    from app.views.login import render_login_view
    from app.views.settings import render_settings

__all__ = [
    "render_auditor",
    "render_anomaly_page",
    "render_dashboard",
    "render_forecasting_page",
    "render_login_view",
    "render_settings",
]

_LAZY_MAP: dict[str, str] = {
    "render_auditor": "app.views.auditor",
    "render_anomaly_page": "app.views.dashboard",
    "render_dashboard": "app.views.dashboard",
    "render_forecasting_page": "app.views.dashboard",
    "render_login_view": "app.views.login",
    "render_settings": "app.views.settings",
}


def __getattr__(name: str):
    if name in _LAZY_MAP:
        import importlib

        module = importlib.import_module(_LAZY_MAP[name])
        obj = getattr(module, name)
        globals()[name] = obj
        return obj
    raise AttributeError(f"module 'app.views' has no attribute {name!r}")


def __dir__() -> list[str]:
    return __all__
