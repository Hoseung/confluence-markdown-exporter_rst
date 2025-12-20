import os
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from confluence_markup_exporter import __version__
from confluence_markup_exporter.utils.app_data_store import get_settings
from confluence_markup_exporter.utils.app_data_store import set_setting
from confluence_markup_exporter.utils.config_interactive import main_config_menu_loop
from confluence_markup_exporter.utils.measure_time import measure
from confluence_markup_exporter.utils.type_converter import str_to_bool

DEBUG: bool = str_to_bool(os.getenv("DEBUG", "False"))

app = typer.Typer()


def override_output_path_config(value: Path | None) -> None:
    """Override the default output path if provided."""
    if value is not None:
        set_setting("export.output_path", value)


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    RST = "rst"


def override_output_format_config(value: ExportFormat | None) -> None:
    """Override the default output format if provided."""
    if value is not None:
        format_value = value.value if isinstance(value, ExportFormat) else str(value)
        set_setting("export.output_format", format_value.lower())


@app.command(help="Export one or more Confluence pages by ID or URL to Markdown or RST.")
def pages(
    pages: Annotated[list[str], typer.Argument(help="Page ID(s) or URL(s)")],
    output_path: Annotated[
        Path | None,
        typer.Option(
            help="Directory to write exported files to. Overrides config if set."
        ),
    ] = None,
    output_format: Annotated[
        ExportFormat | None,
        typer.Option(
            "--format",
            help="Markup format for exported files. Overrides config if set.",
            case_sensitive=False,
        ),
    ] = None,
) -> None:
    from confluence_markup_exporter.confluence import Page

    with measure(f"Export pages {', '.join(pages)}"):
        for page in pages:
            override_output_path_config(output_path)
            override_output_format_config(output_format)
            _page = Page.from_id(int(page)) if page.isdigit() else Page.from_url(page)
            _page.export()


@app.command(
    help="Export Confluence pages and their descendant pages by ID or URL to Markdown or RST."
)
def pages_with_descendants(
    pages: Annotated[list[str], typer.Argument(help="Page ID(s) or URL(s)")],
    output_path: Annotated[
        Path | None,
        typer.Option(
            help="Directory to write exported files to. Overrides config if set."
        ),
    ] = None,
    output_format: Annotated[
        ExportFormat | None,
        typer.Option(
            "--format",
            help="Markup format for exported files. Overrides config if set.",
            case_sensitive=False,
        ),
    ] = None,
) -> None:
    from confluence_markup_exporter.confluence import Page

    with measure(f"Export pages {', '.join(pages)} with descendants"):
        for page in pages:
            override_output_path_config(output_path)
            override_output_format_config(output_format)
            _page = Page.from_id(int(page)) if page.isdigit() else Page.from_url(page)
            _page.export_with_descendants()


@app.command(help="Export all Confluence pages of one or more spaces to Markdown or RST.")
def spaces(
    space_keys: Annotated[list[str], typer.Argument()],
    output_path: Annotated[
        Path | None,
        typer.Option(
            help="Directory to write exported files to. Overrides config if set."
        ),
    ] = None,
    output_format: Annotated[
        ExportFormat | None,
        typer.Option(
            "--format",
            help="Markup format for exported files. Overrides config if set.",
            case_sensitive=False,
        ),
    ] = None,
) -> None:
    from confluence_markup_exporter.confluence import Space

    with measure(f"Export spaces {', '.join(space_keys)}"):
        for space_key in space_keys:
            override_output_path_config(output_path)
            override_output_format_config(output_format)
            space = Space.from_key(space_key)
            space.export()


@app.command(help="Export all Confluence pages across all spaces to Markdown or RST.")
def all_spaces(
    output_path: Annotated[
        Path | None,
        typer.Option(
            help="Directory to write exported files to. Overrides config if set."
        ),
    ] = None,
    output_format: Annotated[
        ExportFormat | None,
        typer.Option(
            "--format",
            help="Markup format for exported files. Overrides config if set.",
            case_sensitive=False,
        ),
    ] = None,
) -> None:
    from confluence_markup_exporter.confluence import Organization

    with measure("Export all spaces"):
        override_output_path_config(output_path)
        override_output_format_config(output_format)
        org = Organization.from_api()
        org.export()


@app.command(help="Open the interactive configuration menu or display current configuration.")
def config(
    jump_to: Annotated[
        str | None,
        typer.Option(help="Jump directly to a config submenu, e.g. 'auth.confluence'"),
    ] = None,
    *,
    show: Annotated[
        bool,
        typer.Option(
            "--show",
            help="Display current configuration as YAML instead of opening the interactive menu",
        ),
    ] = False,
) -> None:
    """Interactive configuration menu or display current configuration."""
    if show:
        current_settings = get_settings()
        json_output = current_settings.model_dump_json(indent=2)
        typer.echo(f"```json\n{json_output}\n```")
    else:
        main_config_menu_loop(jump_to)


@app.command(help="Show the current version of confluence-markup-exporter.")
def version() -> None:
    """Display the current version."""
    typer.echo(f"confluence-markup-exporter {__version__}")


if __name__ == "__main__":
    app()
