from pathlib import Path
from lark import Lark, Transformer
from typing import List, Union

# Load enhanced grammar
grammar_path = Path(__file__).parent / "nl_sql_enhanced.lark"
nl_grammar = grammar_path.read_text()


class EnhancedNL2SQL(Transformer):
    """Enhanced transformer for natural language to SQL conversion."""
    
    def start(self, args):
        """Top-level rule: unwrap the SQL string."""
        return args[0]

    # Basic SELECT operations
    def select_all(self, args):
        """Handle 'show all table' patterns."""
        table = args[0]
        return f"SELECT * FROM {table};"

    def select_columns(self, args):
        """Handle 'get columns from table' patterns."""
        cols, table = args
        return f"SELECT {', '.join(cols)} FROM {table};"

    def select_where(self, args):
        """Handle 'list table where condition' patterns."""
        table, cond = args
        return f"SELECT * FROM {table} WHERE {cond};"

    def select_where_natural(self, args):
        """Handle natural language WHERE patterns."""
        table, cond = args
        return f"SELECT * FROM {table} WHERE {cond};"

    def select_order(self, args):
        """Handle ordering with optional direction."""
        table, column, *order = args
        if order:
            direction = order[0]
            return f"SELECT * FROM {table} ORDER BY {column} {direction};"
        else:
            return f"SELECT * FROM {table} ORDER BY {column};"

    def select_group(self, args):
        """Handle GROUP BY without HAVING."""
        table, col = args
        return f"SELECT * FROM {table} GROUP BY {col};"

    def select_group_having(self, args):
        """Handle GROUP BY with HAVING clause."""
        table, col, condition = args
        return f"SELECT * FROM {table} GROUP BY {col} HAVING {condition};"

    def select_group_order(self, args):
        """Handle GROUP BY with ORDER BY."""
        table, group_col, order_col, *order = args
        if order:
            direction = order[0]
            return f"SELECT * FROM {table} GROUP BY {group_col} ORDER BY {order_col} {direction};"
        else:
            return f"SELECT * FROM {table} GROUP BY {group_col} ORDER BY {order_col};"

    # Aggregation functions
    def count_all(self, args):
        """Handle COUNT(*) operations."""
        table = args[0]
        return f"SELECT COUNT(*) FROM {table};"

    def count_distinct(self, args):
        """Handle COUNT(DISTINCT column) operations."""
        column, table = args
        return f"SELECT COUNT(DISTINCT {column}) FROM {table};"

    def sum_column(self, args):
        """Handle SUM operations."""
        column, table = args
        return f"SELECT SUM({column}) FROM {table};"

    def avg_column(self, args):
        """Handle AVG operations."""
        column, table = args
        return f"SELECT AVG({column}) FROM {table};"

    def max_column(self, args):
        """Handle MAX operations."""
        column, table = args
        return f"SELECT MAX({column}) FROM {table};"

    def min_column(self, args):
        """Handle MIN operations."""
        column, table = args
        return f"SELECT MIN({column}) FROM {table};"

    # Enhanced JOIN operations
    def select_join(self, args):
        """Handle JOIN operations with different join types."""
        left_table, join_type, right_table, condition = args
        return f"SELECT * FROM {left_table} {join_type.upper()} JOIN {right_table} ON {condition};"

    def select_join_simple(self, args):
        """Handle simple JOIN operations."""
        left_table, right_table, condition = args
        return f"SELECT * FROM {left_table} JOIN {right_table} ON {condition};"

    # Subquery support
    def select_with_subquery(self, args):
        """Handle subqueries in WHERE clauses."""
        table, column, subquery = args
        return f"SELECT * FROM {table} WHERE {column} IN ({subquery});"

    # Enhanced condition parsing
    def and_condition(self, args):
        """Handle AND conditions."""
        left, right = args
        return f"({left}) AND ({right})"

    def or_condition(self, args):
        """Handle OR conditions."""
        left, right = args
        return f"({left}) OR ({right})"

    def not_condition(self, args):
        """Handle NOT conditions."""
        condition = args[0]
        return f"NOT ({condition})"

    def paren_condition(self, args):
        """Handle parenthesized conditions."""
        return f"({args[0]})"

    def like_condition(self, args):
        """Handle LIKE conditions."""
        column, pattern = args
        return f"{column} LIKE {pattern}"

    def not_like_condition(self, args):
        """Handle NOT LIKE conditions."""
        column, pattern = args
        return f"{column} NOT LIKE {pattern}"

    def in_condition(self, args):
        """Handle IN conditions."""
        column, values = args
        return f"{column} IN ({', '.join(values)})"

    def not_in_condition(self, args):
        """Handle NOT IN conditions."""
        column, values = args
        return f"{column} NOT IN ({', '.join(values)})"

    def between_condition(self, args):
        """Handle BETWEEN conditions."""
        column, start, end = args
        return f"{column} BETWEEN {start} AND {end}"

    def not_between_condition(self, args):
        """Handle NOT BETWEEN conditions."""
        column, start, end = args
        return f"{column} NOT BETWEEN {start} AND {end}"

    def is_null_condition(self, args):
        """Handle IS NULL conditions."""
        column = args[0]
        return f"{column} IS NULL"

    def is_not_null_condition(self, args):
        """Handle IS NOT NULL conditions."""
        column = args[0]
        return f"{column} IS NOT NULL"

    def exists_condition(self, args):
        """Handle EXISTS conditions."""
        column, subquery = args
        return f"EXISTS ({subquery})"

    def not_exists_condition(self, args):
        """Handle NOT EXISTS conditions."""
        column, subquery = args
        return f"NOT EXISTS ({subquery})"

    # Natural language condition handlers
    def natural_greater_than(self, args):
        """Handle 'column is greater than value' patterns."""
        column, value = args
        return f"{column} > {value}"

    def natural_less_than(self, args):
        """Handle 'column is less than value' patterns."""
        column, value = args
        return f"{column} < {value}"

    def natural_equal_to(self, args):
        """Handle 'column is equal to value' patterns."""
        column, value = args
        return f"{column} = {value}"

    def natural_not_equal_to(self, args):
        """Handle 'column is not equal to value' patterns."""
        column, value = args
        return f"{column} != {value}"

    def natural_greater_equal(self, args):
        """Handle 'column is greater than or equal to value' patterns."""
        column, value = args
        return f"{column} >= {value}"

    def natural_less_equal(self, args):
        """Handle 'column is less than or equal to value' patterns."""
        column, value = args
        return f"{column} <= {value}"

    def natural_like(self, args):
        """Handle 'column is like pattern' patterns."""
        column, pattern = args
        return f"{column} LIKE {pattern}"

    def natural_not_like(self, args):
        """Handle 'column is not like pattern' patterns."""
        column, pattern = args
        return f"{column} NOT LIKE {pattern}"

    def natural_in(self, args):
        """Handle 'column is in values' patterns."""
        column, values = args
        return f"{column} IN ({', '.join(values)})"

    def natural_not_in(self, args):
        """Handle 'column is not in values' patterns."""
        column, values = args
        return f"{column} NOT IN ({', '.join(values)})"

    def natural_between(self, args):
        """Handle 'column is between start and end' patterns."""
        column, start, end = args
        return f"{column} BETWEEN {start} AND {end}"

    def natural_not_between(self, args):
        """Handle 'column is not between start and end' patterns."""
        column, start, end = args
        return f"{column} NOT BETWEEN {start} AND {end}"

    def natural_is_null(self, args):
        """Handle 'column is null' patterns."""
        column = args[0]
        return f"{column} IS NULL"

    def natural_is_not_null(self, args):
        """Handle 'column is not null' patterns."""
        column = args[0]
        return f"{column} IS NOT NULL"

    def natural_and_condition(self, args):
        """Handle natural language AND conditions."""
        left, right = args
        return f"({left}) AND ({right})"

    def natural_or_condition(self, args):
        """Handle natural language OR conditions."""
        left, right = args
        return f"({left}) OR ({right})"

    def natural_not_condition(self, args):
        """Handle natural language NOT conditions."""
        condition = args[0]
        return f"NOT ({condition})"

    def natural_paren_condition(self, args):
        """Handle natural language parenthesized conditions."""
        return f"({args[0]})"

    # Ordering
    def ascending(self, _):
        return "ASC"

    def asc(self, _):
        return "ASC"

    def descending(self, _):
        return "DESC"

    def desc(self, _):
        return "DESC"

    # Basic elements
    def columns(self, args):
        """Convert column list to comma-separated string."""
        return [str(c) for c in args]

    def table(self, args):
        """Extract table name."""
        return str(args[0])

    def column(self, args):
        """Extract column name."""
        return str(args[0])

    def join_condition(self, args):
        """Handle join conditions."""
        left, right = args
        return f"{left} = {right}"

    def subquery(self, args):
        """Handle subqueries."""
        return args[0]

    def values(self, args):
        """Handle multiple values."""
        return [str(v) for v in args]

    def value(self, args):
        """Handle single values."""
        return str(args[0])

    def join_type(self, args):
        """Extract join type."""
        return str(args[0])

    def order(self, args):
        """Extract order direction."""
        return str(args[0])


# Create enhanced parser
enhanced_parser = Lark(nl_grammar, start="start", parser="lalr", transformer=EnhancedNL2SQL())


def translate_nl_to_sql_enhanced(text: str) -> str:
    """Convert natural language into an SQL query string using enhanced grammar."""
    try:
        return enhanced_parser.parse(text.lower())
    except Exception as e:
        # Provide more helpful error messages
        error_msg = f"-- Error translating '{text}': {str(e)}"
        return error_msg


def get_supported_patterns() -> List[str]:
    """Return a list of supported natural language patterns for documentation."""
    return [
        "Basic Queries:",
        "  show all users",
        "  get name, email from users", 
        "  find users where age > 25",
        "  show users ordered by name",
        "",
        "Aggregations:",
        "  count all from users",
        "  how many users",
        "  sum salary from employees",
        "  average age from users",
        "",
        "Joins:",
        "  show users inner join orders on user_id = user_id",
        "  find users left join profiles on users.id = profiles.user_id",
        "",
        "Advanced Conditions:",
        "  find users where name like 'John%'",
        "  show users where age between 18 and 65",
        "  get users where status in ('active', 'pending')",
        "  find users where name is not null",
        "",
        "Logical Operators:",
        "  show users where age > 18 and status = 'active'",
        "  find users where name like 'A%' or name like 'B%'",
        "  get users where not (age < 18)",
    ]

