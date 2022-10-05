# Ward Coverage

[![CI/CD](https://github.com/petereon/ward_coverage/actions/workflows/python-test.yml/badge.svg?branch=master)](https://github.com/petereon/ward_coverage/actions/workflows/python-test.yml) [![MyPy Lint](https://github.com/petereon/ward_coverage/actions/workflows/python-lint.yml/badge.svg?branch=master)](https://github.com/petereon/ward_coverage/actions/workflows/python-lint.yml) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_ward_coverage&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=petereon_ward_coverage)

__Disclaimer: Albeit useful already, this is a work-in-progress and should be seen as such.__ 

A coverage plugin for Python's [Ward testing framework](https://ward.readthedocs.io/en/latest/)

![Example image](https://raw.githubusercontent.com/petereon/ward-coverage/master/resources/screen.png)

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
- `report_type`, defaulting to `["term"]`, which is a list of report types to generate. Possible values are one or more of _'lcov'_, _'html'_, _'xml'_, _'json'_, _'term'_
- `threshold` for minimum coverage, affecting the color the result panel has for some sort of visual cue
- All of the options described [here](https://coverage.readthedocs.io/en/6.4.4/config.html#run-source-pkgs). Please note that everything here under [`[run]` section](https://coverage.readthedocs.io/en/6.4.4/config.html#run) goes to  `[tool.ward.plugins.coverage]` and other sections need their separate block (e.g `[tool.ward.plugins.coverage.report]`) or dictionary entry within the `[tool.ward.plugins.coverage]` section in toml.

### Example configuration
```toml
[tool.ward.plugins.coverage]
omit = ["*test*", "example.py", "**/__init__.py"]
report_type = ["term", "xml"]
source = ["."]
branch = true
relative_files = true
report = {skip_empty = true}
```

__Contributors, issues and feature requests are welcome.__
