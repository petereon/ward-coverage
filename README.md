# Ward Coverage

## Overview

__Disclaimer: Albeit useful already, this is a work-in-progress and should be seen as such. Contributors, issues and feature requests are welcome.__

A coverage plugin for Python's [Ward testing framework](https://ward.readthedocs.io/en/latest/)

## Installation

Build the plugin:

```bash
poetry build
```
and install using

```bash
pip install dist/ward_coverage-0.1.1-py3-none-any.whl
```

## Configuration

To include coverage in your test run, add the following to your `pyproject.toml`:

```toml
[tool.ward]
hook_module = ["ward_coverage"]
```

There are several options to configure the plugin which can be included under section `[tool.ward.plugins.coverage]`, namely:
- All the constructor parameters of `Coverage` class as described here: [https://coverage.readthedocs.io/en/6.4/api_coverage.html#coverage.Coverage](https://coverage.readthedocs.io/en/6.4/api_coverage.html#coverage.Coverage)
- `report_type`, defaulting to `["term"]`, which is a list of report types to generate. Possible values are one or more of _'lcov'_, _'html'_, _'xml'_, _'json'_, _'term'_