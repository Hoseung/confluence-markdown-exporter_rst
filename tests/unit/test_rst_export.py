"""Tests for reStructuredText export helpers."""

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock


def _load_confluence_module(monkeypatch) -> ModuleType:
    dummy_client = MagicMock()
    monkeypatch.setattr(
        "confluence_markup_exporter.api_clients.get_confluence_instance", lambda: dummy_client
    )
    monkeypatch.setattr(
        "confluence_markup_exporter.api_clients.get_jira_instance", lambda: MagicMock()
    )
    module = importlib.reload(importlib.import_module("confluence_markup_exporter.confluence"))
    return module


def _build_page(confluence_module: ModuleType, body: str, body_export: str | None = None):
    return confluence_module.Page(
        id=123,
        title="Sample Page",
        space=confluence_module.Space(key="KEY", name="Key Space", description="", homepage=123),
        body=body,
        body_export=body_export or body,
        editor2="",
        labels=[],
        attachments=[],
        ancestors=[],
    )


def test_rst_alert_conversion(monkeypatch) -> None:
    """Ensure Confluence alerts become RST admonitions."""
    confluence_module = _load_confluence_module(monkeypatch)
    monkeypatch.setattr(confluence_module.settings.export, "output_format", "rst")
    monkeypatch.setattr(confluence_module.settings.export, "include_document_title", False)
    monkeypatch.setattr(confluence_module.settings.export, "page_breadcrumbs", False)
    page = _build_page(
        confluence_module, '<div data-macro-name="callout"><p>Important callout</p></div>'
    )

    output = page.document

    assert ".. important::" in output
    assert "Important callout" in output


def test_rst_extension_and_path(monkeypatch) -> None:
    """Ensure export paths honor rst format defaults."""
    confluence_module = _load_confluence_module(monkeypatch)
    monkeypatch.setattr(confluence_module.settings.export, "output_format", "rst")
    monkeypatch.setattr(confluence_module.settings.export, "page_extension", "md")
    monkeypatch.setattr(
        confluence_module.settings.export, "page_path", "{page_title}.{page_extension}"
    )
    page = _build_page(confluence_module, "<p>content</p>")
    monkeypatch.setattr(confluence_module.Page, "from_id", classmethod(lambda cls, pid: page))

    assert page.page_extension == "rst"
    assert page.export_path.suffix == ".rst"
