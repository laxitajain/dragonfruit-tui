import pytest
from src.harlequin.nl_to_sql import translate_nl_to_sql


def test_select_all():
    assert translate_nl_to_sql("show all users") == "SELECT * FROM users;"

def test_select_columns():
    assert translate_nl_to_sql("get name, email from users") == "SELECT name, email FROM users;"

def test_select_where():
    assert translate_nl_to_sql("list orders where amount > 100") == "SELECT * FROM orders WHERE amount > 100;"

def test_select_order_default():
    assert translate_nl_to_sql("show users ordered by age") == "SELECT * FROM users ORDER BY age;"

def test_select_order_asc():
    assert translate_nl_to_sql("show users ordered by age in ascending order") == "SELECT * FROM users ORDER BY age ASC;"

def test_select_order_desc():
    assert translate_nl_to_sql("show users ordered by age in descending order") == "SELECT * FROM users ORDER BY age DESC;"

def test_select_group():
    assert translate_nl_to_sql("show users grouped by department") == "SELECT * FROM users GROUP BY department;"

def test_select_join():
    assert translate_nl_to_sql("show users join orders on user_id = user_id") == "SELECT * FROM users JOIN orders ON user_id = user_id;"
