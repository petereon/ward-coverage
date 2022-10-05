import os
from distutils.command.install_headers import install_headers
from typing import Any, Dict, List, Union
from unittest import mock

import coverage  # type: ignore
from coverage import CoverageException  # type: ignore
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
    cov = coverage.Coverage()

    # [run]
    if coverage.__version__ >= "6.4":
        cov.config.sigterm = get_in_versioned(
            coverage_config, ["sigterm"], cov.config.sigterm, "6.4"
        )
    if coverage.__version__ >= "5.3":
        cov.config.source_pkgs = get_in_versioned(
            coverage_config, ["source_pkgs"], cov.config.source_pkgs, "5.3"
        )

    cov.config.command_line = get_in_versioned(
        coverage_config, ["command_line"], cov.config.command_line, "5.0"
    )
    cov.config.context = get_in_versioned(coverage_config, ["context"], cov.config.context, "5.0")
    cov.config.relative_files = get_in_versioned(
        coverage_config, ["relative_files"], cov.config.relative_files, "5.0"
    )
    cov.config.concurrency = get_in_versioned(
        coverage_config, ["concurrency"], cov.config.concurrency, "4.0"
    )

    cov.config.branch = coverage_config.get("branch", cov.config.branch)
    cov.config.cover_pylib = coverage_config.get("cover_pylib", cov.config.cover_pylib)
    cov.config.data_file = coverage_config.get("data_file", cov.config.data_file)
    cov.config.disable_warnings = coverage_config.get(
        "disable_warnings", cov.config.disable_warnings
    )
    cov.config.debug = coverage_config.get("debug", cov.config.debug)
    cov.config.run_include = coverage_config.get("include", cov.config.run_include)
    cov.config.run_omit = coverage_config.get("omit", cov.config.run_omit)
    cov.config.parallel = coverage_config.get("parallel", cov.config.parallel)
    cov.config.plugins = coverage_config.get("plugins", cov.config.plugins)
    cov.config.source = coverage_config.get("source", cov.config.source)
    cov.config.timid = coverage_config.get("timid", cov.config.timid)
    cov.config.config_file = coverage_config.get("config_file", cov.config.config_file)
    cov.config.dynamic_context = coverage_config.get("dynamic_context", cov.config.dynamic_context)

    # [paths]
    cov.config.paths = coverage_config.get("paths", cov.config.paths)

    # [report]
    cov.config.exclude_list = coverage_config.get("report", {}).get(
        "exclude_lines", cov.config.exclude_list
    )
    cov.config.fail_under = coverage_config.get("report", {}).get(
        "fail_under", cov.config.fail_under
    )
    cov.config.ignore_errors = coverage_config.get("report", {}).get(
        "ignore_errors", cov.config.ignore_errors
    )
    cov.config.report_include = coverage_config.get("report", {}).get(
        "include", cov.config.report_include
    )
    cov.config.report_omit = coverage_config.get("report", {}).get("omit", cov.config.report_omit)
    cov.config.precision = coverage_config.get("report", {}).get("precision", cov.config.precision)
    cov.config.skip_empty = coverage_config.get("report", {}).get(
        "skip_empty", cov.config.skip_empty
    )
    if coverage.__version__ >= "5.2":
        cov.config.sort = get_in_versioned(
            coverage_config, ["report", "sort"], cov.config.sort, "5.2"
        )

    # [html]
    if coverage.__version__ >= "5.4":
        cov.config.html_skip_covered = get_in_versioned(
            coverage_config, ["html", "skip_covered"], cov.config.html_skip_covered, "5.4"
        )
        cov.config.html_skip_empty = get_in_versioned(
            coverage_config, ["html", "skip_empty"], cov.config.html_skip_empty, "5.4"
        )
    cov.config.html_dir = coverage_config.get("html", {}).get("directory", cov.config.html_dir)
    cov.config.extra_css = coverage_config.get("html", {}).get("extra_css", cov.config.extra_css)
    cov.config.show_contexts = coverage_config.get("html", {}).get(
        "show_contexts", cov.config.show_contexts
    )
    cov.config.html_title = coverage_config.get("html", {}).get("title", cov.config.html_title)

    # [xml]
    cov.config.xml_output = coverage_config.get("xml", {}).get("output", cov.config.xml_output)
    cov.config.xml_package_depth = coverage_config.get("xml", {}).get(
        "package_depth", cov.config.xml_package_depth
    )

    # [json]
    cov.config.json_output = get_in_versioned(
        coverage_config, ["json", "output"], cov.config.json_output, "5.0"
    )
    cov.config.json_pretty_print = get_in_versioned(
        coverage_config, ["json", "pretty_print"], cov.config.json_pretty_print, "5.0"
    )
    cov.config.json_show_contexts = get_in_versioned(
        coverage_config, ["json", "show_contexts"], cov.config.json_show_contexts, "5.0"
    )

    # [lcov]
    if coverage.__version__ >= "6.3":
        cov.config.lcov_output = get_in_versioned(
            coverage_config, ["lcov", "output"], cov.config.lcov_output, "6.3"
        )

    cov.start()


@hook
def after_session(config: Config) -> Union[ConsoleRenderable, None]:
    global cov
    try:
        report = get_report()
    except CoverageException:
        return Panel(
            "No data was collected",
            title="[white bold]Coverage report",
            border_style="green",
            expand=False,
        )
    coverage_config = config.plugin_config.get("coverage", {})
    report_type = coverage_config.get("report_type", ["term"])

    if not isinstance(report_type, list):
        raise Exception("report_type must be a list")

    create_report_files(report_type)

    if "term" in report_type:
        table = render_table(report)
        return Panel(table, title="[white bold]Coverage report", border_style="green", expand=False)

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
            str(round(file_report["summary"]["percent_covered"])) + "%",
            preprocess_missing_lines(file_report["missing_lines"]),
        )
    table.add_row("", "", "", "", "")
    table.add_row(
        "Total",
        str(report["totals"]["num_statements"]),
        str(report["totals"]["missing_lines"]),
        str(round(report["totals"]["percent_covered"])) + "%",
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


def get_in_versioned(dictionary: dict, path: list, default: Any, version: str) -> Any:
    result = dictionary
    for path_part in path:
        try:
            result = result[path_part]
        except KeyError:
            result = default
            break
    if (result != default) and (version > coverage.__version__):
        print(
            f'Option {".".join(path[:-1])} unavailable until version {version}. Your current version is {coverage.__version__}'
        )
    return result
