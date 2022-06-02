import os
from ward import test, fixture
from ward_coverage.hook_impl import (
    get_config,
    get_preformatted_table,
    preprocess_missing_lines,
    render_table,
)
from unittest.mock import MagicMock


@fixture
def temp_config_plugins():
    conf = """
[tool.ward]
built_in_config="some-value"

[tool.ward.plugins.coverage]
something = 3
"""
    with open("/tmp/temp_config.toml", "w") as f:
        f.write(conf)
    yield

    os.remove("/tmp/temp_config.toml")


for lines, result in [
    ([1, 2, 3, 5, 9], "1-3, 5, 9"),
    ([122, 123, 188, 189, 2000], "122-123, 188-189, 2000"),
]:

    @test(f"`preprocess_missing_lines` concatenates {lines} to {result}")
    def _(lines=lines, result=result):
        assert preprocess_missing_lines(lines) == result


@test("`get_preformatted_table` gives table with formatting")
def _():
    table = get_preformatted_table()
    assert len(table.columns) == 5
    assert table.columns[0].header == "File"
    assert table.columns[0].justify == "left"
    assert table.columns[0].style == "bold"

    assert table.columns[1].header == "Statements"
    assert table.columns[1].justify == "right"

    assert table.columns[2].header == "Missed"
    assert table.columns[2].justify == "right"

    assert table.columns[3].header == "Coverage"
    assert table.columns[3].justify == "right"

    assert table.columns[4].header == "Missing"
    assert table.columns[4].style == "red"


@test("`get_config` loads config from file if there is none in `config` argument")
def _(temp_config_plugins=temp_config_plugins):
    mock = MagicMock()
    mock.plugin_config = {}
    mock.config_path = "/tmp/temp_config.toml"
    assert get_config(mock) == {"something": 3}


@test("`get_config` loads config from `config` argument if there is one")
def _(temp_config_plugins=temp_config_plugins):
    mock = MagicMock()
    mock.plugin_config = {"coverage": {"test": 4}}
    mock.config_path = "/tmp/temp_config.toml"
    assert get_config(mock) == {"test": 4}
