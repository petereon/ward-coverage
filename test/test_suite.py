import pytest
from ward_coverage.hook_impl import get_preformatted_table, preprocess_missing_lines, render_table


@pytest.mark.parametrize(
    "lines, result",
    [([1, 2, 3, 5, 9], "1-3, 5, 9"), ([122, 123, 188, 189, 2000], "122-123, 188-189, 2000")],
)
def test_preprocess_missing_lines(lines, result):
    assert preprocess_missing_lines(lines) == result


def test_get_preformatted_table():
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
