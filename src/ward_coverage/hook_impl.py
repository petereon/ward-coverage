import os
from distutils.command.install_headers import install_headers
from typing import Any, Dict, List, Union
from unittest import mock

import coverage  # type: ignore
import toml  # type: ignore
from rich.console import ConsoleRenderable
from rich.panel import Panel
from rich.table import Table
from ward.config import Config  # type: ignore
from ward.hooks import hook  # type: ignore

cov: coverage.Coverage


@hook
def before_session(config: Config):
    global cov
    coverage_config = config.plugin_config.get("coverage", {})
    cov = coverage.Coverage(
        data_file=coverage_config.get("data_file", ".coverage"),
        data_suffix=coverage_config.get("data_suffix", None),
        cover_pylib=coverage_config.get("cover_pylib", None),
        auto_data=coverage_config.get("auto_data", False),
        timid=coverage_config.get("timid", None),
        branch=coverage_config.get("branch", None),
        config_file=coverage_config.get("config_file", True),
        source=coverage_config.get("source", None),
        source_pkgs=coverage_config.get("source_pkgs", None),
        omit=coverage_config.get("omit", None),
        include=coverage_config.get("include", None),
        debug=coverage_config.get("debug", None),
        concurrency=coverage_config.get("concurrency", None),
        check_preimported=coverage_config.get("check_preimported", False),
        context=coverage_config.get("context", None),
        messages=coverage_config.get("messages", False),
    )
    cov.start()


@hook
def after_session(config: Config) -> Union[ConsoleRenderable, None]:
    global cov

    report = get_report()
    coverage_config = config.plugin_config.get("coverage", {})
    report_type = coverage_config.get("report_type", ["term"])
    threshold = coverage_config.get("threshold", "80")

    if not isinstance(report_type, list):
        raise Exception("report_type must be a list")

    create_report_files(report_type)
    passed = float(report["totals"]["percent_covered_display"]) > float(threshold)
    if "term" in report_type:
        table = render_table(report)
        return Panel(table, title="[white bold]Coverage report", border_style="green" if passed else "red", expand=False)

    return None


def get_report() -> dict:
    report: dict = {}
    cov.stop()
    with mock.patch("json.dump", lambda *args, **kwargs: report.update(args[0])):
        cov.json_report()
    os.remove(cov.config.json_output)
    return report


def create_report_files(report_type: List[str]) -> None:
    for rt in report_type:
        if rt not in ["lcov", "html", "xml", "json", "term"]:
            raise Exception(
                f"each report_type member must be one of 'lcov', 'html', 'xml', 'json', 'term', found '{rt}'"
            )

        if rt == "lcov":
            cov.lcov_report()

        if rt == "html":
            cov.html_report()

        if rt == "xml":
            cov.xml_report()

        if rt == "json":
            cov.json_report()


def render_table(report: dict) -> Table:
    table = get_preformatted_table()
    for filename, file_report in report["files"].items():
        table.add_row(
            filename,
            str(file_report["summary"]["num_statements"]),
            str(file_report["summary"]["missing_lines"]),
            file_report["summary"]["percent_covered_display"] + "%",
            preprocess_missing_lines(file_report["missing_lines"]),
        )
    table.add_row("", "", "", "", "")
    table.add_row(
        "Total",
        str(report["totals"]["num_statements"]),
        str(report["totals"]["missing_lines"]),
        report["totals"]["percent_covered_display"] + "%",
        "",
        style="bold",
    )

    return table


def get_preformatted_table() -> Table:
    table = Table(box=None, header_style="bold green")
    table.add_column("File", justify="left", style="bold")
    table.add_column("Statements", justify="right")
    table.add_column("Missed", justify="right")
    table.add_column("Coverage", justify="right")
    table.add_column("Missing", style="red")

    return table


def preprocess_missing_lines(missing_lines: list) -> str:
    res = []
    if len(missing_lines) == 0:
        return ""
    for sequence in group_sequence(missing_lines):
        if len(sequence) > 1:
            res.append(str(sequence[0]) + "-" + str(sequence[-1]))
        else:
            res.append(str(sequence[0]))
    return ", ".join(res)


def group_sequence(lst: List[int]) -> list:
    res = [[lst[0]]]
    for i in range(1, len(lst)):
        if lst[i - 1] + 1 == lst[i]:
            res[-1].append(lst[i])
        else:
            res.append([lst[i]])
    return res
