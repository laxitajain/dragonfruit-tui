from pathlib import Path
from lark import Lark, Transformer
from typing import List, Union
import sys

import duckdb
import re

def get_schema_info(db_path: str):
    """Extract {table: [columns]} mapping from the DuckDB database."""
    conn = duckdb.connect(db_path, read_only=True)
    tables = [
        row[0]
        for row in conn.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
              AND table_type='BASE TABLE';
        """).fetchall()
    ]

    schema = {}
    for table in tables:
        cols = [
            row[0]
            for row in conn.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """).fetchall()
        ]
        schema[table] = cols
    conn.close()
    return schema


def load_dynamic_grammar(grammar_path: Path, db_path: str) -> str:
    """Load base grammar and inject table/column literals based on DB schema."""
    base_grammar = grammar_path.read_text()
    schema = get_schema_info(db_path)

    if not schema:
        print("âš ï¸ No tables found in database â€” using dummy placeholders.")
        return re.sub(r"table: CNAME", 'table: "dummy_table"', base_grammar)

    # Build literal rules
    table_literals = " | ".join(f'"{t}"' for t in schema.keys())
    all_columns = sorted({col for cols in schema.values() for col in cols})
    column_literals = " | ".join(f'"{c}"' for c in all_columns)

    # Replace table and column rules
    grammar = re.sub(r"\btable\s*:\s*CNAME\b", f'table: TABLE_NAME\nTABLE_NAME: {table_literals}', base_grammar, flags=re.MULTILINE)
    grammar = re.sub(r"\bcolumn\s*:\s*CNAME\b", f'column: COLUMN_NAME\nCOLUMN_NAME: {column_literals}', grammar, flags=re.MULTILINE)


    # Exclude table/column names from FILLER
    keywords = set(schema.keys()) | {c for cols in schema.values() for c in cols}
    if keywords:
        # Negative lookahead so filler doesn't match schema words
        pattern = "|".join(re.escape(k) for k in keywords)
        filler_regex = rf"(?!(?:{pattern})\b)[A-Za-z]+"
        grammar = re.sub(r"FILLER\s*:\s*/\[A-Za-z\]\+\//", f'FILLER: /{filler_regex}/', grammar, flags=re.IGNORECASE)


    print("ðŸ§  Injected tables:", list(schema.keys()))
    print("âœ… Injected schema into grammar successfully.")
    return grammar


# Load enhanced grammar
grammar_path = Path(__file__).parent / "nl_sql_enhanced.lark"
nl_grammar = grammar_path.read_text()


class EnhancedNL2SQL(Transformer):
    """Enhanced transformer for natural language to SQL conversion."""
    
    def start(self, args):
        """Top-level rule: unwrap the SQL string."""
        return args[0]

    def _strip_fillers(self, args):
        """Remove filler subtrees and return only plain tokens or strings."""
        cleaned = []
        for a in args:
            if hasattr(a, "data") and a.data == "filler":
                # skip filler subtrees
                continue
            if isinstance(a, list):
                cleaned.extend(self._strip_fillers(a))
            else:
                cleaned.append(str(a))
        return cleaned


    # Basic SELECT operations
    def select_all(self, args):
        """Handle 'show all table' patterns."""
        table = args[0]
        return f"SELECT * FROM {table};"
    # def select_all(self, args):
    #     print("DEBUG select_all args (raw):", args)
    #     args = self._strip_fillers(args)
    #     print("DEBUG select_all args (cleaned):", args)

    #     if not args:
    #         return "SELECT * FROM unknown_table;"
    #     table = args[-1]  # last argument after stripping fillers
    #     return f"SELECT * FROM {table};"



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

    def select_with(self, args):
        """Handle 'table with condition' patterns."""
        table, cond = args
        return f"SELECT * FROM {table} WHERE {cond};"

    def condition(self, args):
        """Handle general conditions, including logical operators."""
        return args[0]

    def simple_condition(self, args):
        """Handle simple conditions like 'column OP value'."""
        if len(args) == 3:
            col, op, val = args
            return f"{col} {op} {val}"
        elif len(args) == 1:
            return str(args[0])
        else:
            return " ".join(str(a) for a in args)

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

    def select_all(self, args):
        print("DEBUG select_all args:", args)
        if not args:
            return "SELECT * FROM unknown_table;"
        table = args[0]
        return f"SELECT * FROM {table};"


default_db_path = str(Path(__file__).parent / "example.db")
if len(sys.argv) > 1:
    DB_PATH = Path(sys.argv[1]).resolve()
else:
    DB_PATH = default_db_path
dynamic_grammar = load_dynamic_grammar(grammar_path, DB_PATH)
# Create enhanced parser
enhanced_parser = Lark(dynamic_grammar, start="start", parser="lalr", transformer = EnhancedNL2SQL())

# enhanced_parser = Lark(
#     nl_grammar,
#     parser="earley",          # â† This enables Earley parser (no reduce/reduce issues)
#     lexer="dynamic_complete",       # â† Allows overlapping token types like FILLER/CNAME
#     propagate_positions=True, # Optional: helpful for debugging
#     maybe_placeholders=True,  # Optional: allows missing optional tokens
#             # â† Optional but recommended for natural language
# )


def translate_nl_to_sql(text: str) -> str:
    """Convert natural language into an SQL query string using enhanced grammar."""
    try:
        result = enhanced_parser.parse(text.lower())
        # Convert Tree to string if needed
        if hasattr(result, 'children') and len(result.children) == 1:
            return str(result.children[0])
        return str(result)
    except Exception as e:
        # Provide more helpful error messages
        error_msg = f"-- Error translating '{text}': {str(e)}"
        return error_msg

# def translate_nl_to_sql(text: str) -> str:
#     """Convert natural language into an SQL query string using enhanced grammar."""
#     try:
#         tree = enhanced_parser.parse(text.lower())
#         print("ðŸŒ³ Parse tree:")
#         print(tree.pretty())
#         result = transformer.transform(tree)
#         if isinstance(result, str):
#             return result
#         return str(result)
#     except Exception as e:
#         return f"-- Error translating '{text}': {e}"


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

#----------------------v2 (duckdb integration: dynamic schema reading)

# from pathlib import Path
# from typing import List, Union
# import duckdb
# from lark import Lark, Transformer


# # ============================================================
# # ENHANCED TRANSFORMER (unchanged)
# # ============================================================
# class EnhancedNL2SQL(Transformer):
#     """Enhanced transformer for natural language to SQL conversion."""

#     def start(self, args): return args[0]

#     # --- SELECT patterns ---
#     def select_all(self, args): return f"SELECT * FROM {args[0]};"
#     def select_columns(self, args): cols, table = args; return f"SELECT {', '.join(cols)} FROM {table};"
#     def select_where(self, args): table, cond = args; return f"SELECT * FROM {table} WHERE {cond};"
#     def select_where_natural(self, args): table, cond = args; return f"SELECT * FROM {table} WHERE {cond};"
#     def select_with(self, args): table, cond = args; return f"SELECT * FROM {table} WHERE {cond};"
#     def select_order(self, args):
#         table, column, *order = args
#         return f"SELECT * FROM {table} ORDER BY {column} {order[0] if order else ''};".strip()
#     def select_group(self, args): table, col = args; return f"SELECT * FROM {table} GROUP BY {col};"
#     def select_group_having(self, args): table, col, cond = args; return f"SELECT * FROM {table} GROUP BY {col} HAVING {cond};"
#     def select_group_order(self, args):
#         table, gcol, ocol, *order = args
#         return f"SELECT * FROM {table} GROUP BY {gcol} ORDER BY {ocol} {order[0] if order else ''};".strip()

#     # --- Aggregation ---
#     def count_all(self, args): return f"SELECT COUNT(*) FROM {args[0]};"
#     def count_distinct(self, args): col, table = args; return f"SELECT COUNT(DISTINCT {col}) FROM {table};"
#     def sum_column(self, args): col, table = args; return f"SELECT SUM({col}) FROM {table};"
#     def avg_column(self, args): col, table = args; return f"SELECT AVG({col}) FROM {table};"
#     def max_column(self, args): col, table = args; return f"SELECT MAX({col}) FROM {table};"
#     def min_column(self, args): col, table = args; return f"SELECT MIN({col}) FROM {table};"

#     # --- Joins ---
#     def select_join(self, args):
#         left, join_type, right, cond = args
#         return f"SELECT * FROM {left} {join_type.upper()} JOIN {right} ON {cond};"
#     def select_join_simple(self, args):
#         left, right, cond = args
#         return f"SELECT * FROM {left} JOIN {right} ON {cond};"

#     # --- Subquery ---
#     def select_with_subquery(self, args):
#         table, column, subquery = args
#         return f"SELECT * FROM {table} WHERE {column} IN ({subquery});"

#     # --- Conditions (and/natural/others) ---
#     def and_condition(self, args): l, r = args; return f"({l}) AND ({r})"
#     def or_condition(self, args): l, r = args; return f"({l}) OR ({r})"
#     def not_condition(self, args): return f"NOT ({args[0]})"
#     def paren_condition(self, args): return f"({args[0]})"
#     def simple_condition(self, args): return " ".join(str(a) for a in args)
#     def join_condition(self, args): l, r = args; return f"{l} = {r}"

#     # --- Natural operators ---
#     def natural_greater_than(self, args): c, v = args; return f"{c} > {v}"
#     def natural_less_than(self, args): c, v = args; return f"{c} < {v}"
#     def natural_equal_to(self, args): c, v = args; return f"{c} = {v}"
#     def natural_not_equal_to(self, args): c, v = args; return f"{c} != {v}"
#     def natural_greater_equal(self, args): c, v = args; return f"{c} >= {v}"
#     def natural_less_equal(self, args): c, v = args; return f"{c} <= {v}"
#     def natural_like(self, args): c, p = args; return f"{c} LIKE {p}"
#     def natural_not_like(self, args): c, p = args; return f"{c} NOT LIKE {p}"
#     def natural_in(self, args): c, v = args; return f"{c} IN ({', '.join(v)})"
#     def natural_not_in(self, args): c, v = args; return f"{c} NOT IN ({', '.join(v)})"
#     def natural_between(self, args): c, s, e = args; return f"{c} BETWEEN {s} AND {e}"
#     def natural_not_between(self, args): c, s, e = args; return f"{c} NOT BETWEEN {s} AND {e}"
#     def natural_is_null(self, args): return f"{args[0]} IS NULL"
#     def natural_is_not_null(self, args): return f"{args[0]} IS NOT NULL"
#     def natural_and_condition(self, args): l, r = args; return f"({l}) AND ({r})"
#     def natural_or_condition(self, args): l, r = args; return f"({l}) OR ({r})"
#     def natural_not_condition(self, args): return f"NOT ({args[0]})"
#     def natural_paren_condition(self, args): return f"({args[0]})"

#     # --- Misc helpers ---
#     def ascending(self, _): return "ASC"
#     def asc(self, _): return "ASC"
#     def descending(self, _): return "DESC"
#     def desc(self, _): return "DESC"
#     def columns(self, args): return [str(c) for c in args]
#     def table(self, args):
#         """Extract table name safely."""
#         if not args:
#             return "unknown_table"
#         return str(args[0])

#     def column(self, args):
#         """Extract column name safely."""
#         if not args:
#             return "unknown_column"
#         return str(args[0])
#     def select_all(self, args):
#         """Handle 'show all table' patterns."""
#         if not args:
#             return "SELECT * FROM unknown_table;"

#         # Find the first non-tree token that looks like a table
#         for a in args:
#             if isinstance(a, str) and a.lower() != "all":
#                 table = a
#                 break
#         else:
#             table = "unknown_table"

#         return f"SELECT * FROM {table};"


#     def values(self, args): return [str(v) for v in args]
#     def value(self, args): return str(args[0])
#     def subquery(self, args): return args[0]
#     def join_type(self, args): return str(args[0])
#     def order(self, args): return str(args[0])

# -----------------------v3-----------------------------------------------------
# nl_to_sql_dynamic.py
# from pathlib import Path
# from typing import List, Tuple, Dict
# import duckdb
# import re
# from lark import Lark, Transformer, Tree, Token

# # ---------------------------
# # Transformer (schema-aware)
# # ---------------------------
# class EnhancedNL2SQL(Transformer):
#     def __init__(self, schema: Dict[str, List[str]] = None):
#         super().__init__()
#         self.schema = schema or {}

#     # Helper utilities (schema-aware)
#     def _all_columns_set(self):
#         return {c for cols in self.schema.values() for c in cols}

#     def _extract_table(self, args):
#         # first prefer explicit table literals that exist in schema
#         for a in args:
#             if isinstance(a, str) and a in self.schema:
#                 return a
#         # fallback: any string token that isn't a filler keyword
#         for a in args:
#             if isinstance(a, str) and a.lower() not in ("all", "from", "with", "where", "show", "get", "find", "list", "please", "me", "you"):
#                 return a
#         return "unknown_table"

#     def _extract_column(self, args):
#         all_cols = self._all_columns_set()
#         for a in args:
#             if isinstance(a, str) and a in all_cols:
#                 return a
#         for a in args:
#             if isinstance(a, str) and a.lower() not in ("all", "from", "where"):
#                 return a
#         return "unknown_column"

#     def _extract_condition(self, args):
#         if args:
#             last = args[-1]
#             return last if isinstance(last, str) else "1=1"
#         return "1=1"

#     def _extract_columns_list(self, args):
#         for a in args:
#             if isinstance(a, list):
#                 return a
#         return [self._extract_column(args)]

#     # top-level
#     def start(self, args):
#         # Lark returns a single child (the command) typically
#         return args[0]

#     # SELECTs
#     def select_all(self, args):
#         table = self._extract_table(args)
#         return f"SELECT * FROM {table};"

#     def select_columns(self, args):
#         cols = self._extract_columns_list(args)
#         table = self._extract_table(args)
#         return f"SELECT {', '.join(cols)} FROM {table};"

#     def select_where(self, args):
#         table = self._extract_table(args)
#         cond = self._extract_condition(args)
#         return f"SELECT * FROM {table} WHERE {cond};"

#     def select_with(self, args):
#         table = self._extract_table(args)
#         cond = self._extract_condition(args)
#         return f"SELECT * FROM {table} WHERE {cond};"

#     def select_where_natural(self, args):
#         table = self._extract_table(args)
#         cond = self._extract_condition(args)
#         return f"SELECT * FROM {table} WHERE {cond};"

#     def select_order(self, args):
#         table = self._extract_table(args)
#         column = self._extract_column(args)
#         order = ""
#         if args and isinstance(args[-1], str):
#             last = str(args[-1]).upper()
#             if last.startswith("ASC"): order = "ASC"
#             if last.startswith("DESC"): order = "DESC"
#         return f"SELECT * FROM {table} ORDER BY {column} {order};".strip()

#     def select_group(self, args):
#         table = self._extract_table(args)
#         col = self._extract_column(args)
#         return f"SELECT * FROM {table} GROUP BY {col};"

#     def select_group_having(self, args):
#         table = self._extract_table(args)
#         col = self._extract_column(args)
#         cond = self._extract_condition(args)
#         return f"SELECT * FROM {table} GROUP BY {col} HAVING {cond};"

#     def select_group_order(self, args):
#         table = self._extract_table(args)
#         columns = [a for a in args if isinstance(a, str)]
#         group_col = columns[-2] if len(columns) >= 2 else "unknown_col"
#         order_col = columns[-1] if columns else "unknown_col"
#         order = ""
#         return f"SELECT * FROM {table} GROUP BY {group_col} ORDER BY {order_col} {order};"

#     # Aggregations
#     def count_all(self, args):
#         table = self._extract_table(args)
#         return f"SELECT COUNT(*) FROM {table};"

#     def count_distinct(self, args):
#         col = self._extract_column(args)
#         table = self._extract_table(args)
#         return f"SELECT COUNT(DISTINCT {col}) FROM {table};"

#     def sum_column(self, args):
#         col = self._extract_column(args)
#         table = self._extract_table(args)
#         return f"SELECT SUM({col}) FROM {table};"

#     def avg_column(self, args):
#         col = self._extract_column(args)
#         table = self._extract_table(args)
#         return f"SELECT AVG({col}) FROM {table};"

#     def max_column(self, args):
#         col = self._extract_column(args)
#         table = self._extract_table(args)
#         return f"SELECT MAX({col}) FROM {table};"

#     def min_column(self, args):
#         col = self._extract_column(args)
#         table = self._extract_table(args)
#         return f"SELECT MIN({col}) FROM {table};"

#     # Joins
#     def select_join(self, args):
#         left = self._extract_table(args[:1])
#         right = self._extract_table(args[1:])
#         # join type might be present as a token
#         jt = None
#         for a in args:
#             if isinstance(a, str) and a.lower() in ("inner", "left", "right", "full", "outer", "cross"):
#                 jt = a
#                 break
#         jt = jt or "INNER"
#         cond = self._extract_condition(args)
#         return f"SELECT * FROM {left} {jt.upper()} JOIN {right} ON {cond};"

#     def select_join_simple(self, args):
#         left = self._extract_table(args[:1])
#         right = self._extract_table(args[1:])
#         cond = self._extract_condition(args)
#         return f"SELECT * FROM {left} JOIN {right} ON {cond};"

#     # Subquery
#     def select_with_subquery(self, args):
#         table = self._extract_table(args)
#         column = self._extract_column(args)
#         subquery = args[-1] if args else ""
#         return f"SELECT * FROM {table} WHERE {column} IN ({subquery});"

#     # Conditions
#     def and_condition(self, args): return f"({args[0]}) AND ({args[1]})"
#     def or_condition(self, args): return f"({args[0]}) OR ({args[1]})"
#     def not_condition(self, args): return f"NOT ({args[0]})"
#     def paren_condition(self, args): return f"({args[0]})"

#     def simple_condition(self, args):
#         if len(args) >= 3:
#             return f"{args[0]} {args[1]} {args[2]}"
#         return " ".join(map(str, args))

#     # Natural conditions
#     def natural_greater_than(self, args): return f"{args[0]} > {args[1]}"
#     def natural_less_than(self, args): return f"{args[0]} < {args[1]}"
#     def natural_equal_to(self, args): return f"{args[0]} = {args[1]}"
#     def natural_not_equal_to(self, args): return f"{args[0]} != {args[1]}"
#     def natural_greater_equal(self, args): return f"{args[0]} >= {args[1]}"
#     def natural_less_equal(self, args): return f"{args[0]} <= {args[1]}"
#     def natural_like(self, args): return f"{args[0]} LIKE {args[1]}"
#     def natural_not_like(self, args): return f"{args[0]} NOT LIKE {args[1]}"
#     def natural_in(self, args): return f"{args[0]} IN ({', '.join(args[1])})"
#     def natural_not_in(self, args): return f"{args[0]} NOT IN ({', '.join(args[1])})"
#     def natural_between(self, args): return f"{args[0]} BETWEEN {args[1]} AND {args[2]}"
#     def natural_not_between(self, args): return f"{args[0]} NOT BETWEEN {args[1]} AND {args[2]}"
#     def natural_is_null(self, args): return f"{args[0]} IS NULL"
#     def natural_is_not_null(self, args): return f"{args[0]} IS NOT NULL"

#     # Basic elements
#     def columns(self, args): return [str(c) for c in args]
#     def table(self, args):
#         """Handle literal tables or tokens."""
#         if not args:
#             return "unknown_table"
#         first = args[0]
#         if isinstance(first, Token):
#             return str(first)
#         if isinstance(first, Tree) and first.children:
#             return str(first.children[0])
#         return str(first)

#     def column(self, args):
#         """Handle literal columns or tokens."""
#         if not args:
#             return "unknown_column"
#         first = args[0]
#         if isinstance(first, Token):
#             return str(first)
#         if isinstance(first, Tree) and first.children:
#             return str(first.children[0])
#         return str(first)

#     def join_condition(self, args):
#         if len(args) >= 2:
#             return f"{args[0]} = {args[1]}"
#         return "1=1"
#     def value(self, args): return str(args[0])
#     def values(self, args): return [str(v) for v in args]
#     def order(self, args):
#         if args:
#             v = str(args[0]).upper()
#             if v.startswith("ASC"): return "ASC"
#             if v.startswith("DESC"): return "DESC"
#         return ""

# # ---------------------------
# # Schema extraction from DuckDB
# # ---------------------------
# def get_schema_info(db_path: str) -> Dict[str, List[str]]:
#     conn = duckdb.connect(db_path, read_only=True)
#     # get tables (exclude system)
#     rows = conn.execute("""
#         SELECT table_name
#         FROM information_schema.tables
#         WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
#           AND table_type='BASE TABLE';
#     """).fetchall()
#     tables = [r[0] for r in rows]
#     schema = {}
#     for t in tables:
#         cols_rows = conn.execute(f"""
#             SELECT column_name
#             FROM information_schema.columns
#             WHERE table_name = '{t}'
#             ORDER BY ordinal_position;
#         """).fetchall()
#         schema[t] = [r[0] for r in cols_rows]
#     conn.close()
#     return schema

# # ---------------------------
# # Grammar injection
# # ---------------------------
# def _quote_literal(s: str) -> str:
#     # escape double quotes inside identifier (rare) and wrap
#     return '"' + s.replace('"', '\\"') + '"'

# def load_dynamic_grammar(db_path: str) -> Tuple[str, Dict[str, List[str]]]:
#     grammar_path = Path(__file__).parent / "op_lark1.lark"
#     base_grammar = grammar_path.read_text()
#     schema = get_schema_info(db_path)

#     if not schema:
#         # replace CNAME placeholders robustly
#         new_grammar = re.sub(r"\btable\s*:\s*CNAME\b", 'table: "dummy_table"', base_grammar, flags=re.MULTILINE)
#         new_grammar = re.sub(r"\bcolumn\s*:\s*CNAME\b", 'column: "dummy_column"', new_grammar, flags=re.MULTILINE)
#         return new_grammar, {}

#     # build literal sets (sorted for determinism)
#     table_literals = " | ".join(_quote_literal(t) for t in sorted(schema.keys()))
#     all_cols = sorted({c for cols in schema.values() for c in cols})
#     column_literals = " | ".join(_quote_literal(c) for c in all_cols)

#     # robustly replace the placeholders
#     new_grammar = re.sub(r"\btable\s*:\s*CNAME\b", f"table: {table_literals}", base_grammar, flags=re.MULTILINE)
#     new_grammar = re.sub(r"\bcolumn\s*:\s*CNAME\b", f"column: {column_literals}", new_grammar, flags=re.MULTILINE)

#     # debug snippet: show the injected lines
#     injected_lines = []
#     for i, line in enumerate(new_grammar.splitlines()):
#         if line.strip().startswith("table:") or line.strip().startswith("column:"):
#             injected_lines.append((i+1, line.rstrip()))
#     print("ðŸ§  Injected tables:", sorted(schema.keys()))
#     print("âœ… Injected schema into grammar successfully.")
#     print("ðŸ”Ž Grammar snippet (table/column lines):")
#     for ln, text in injected_lines:
#         print(f"  {ln}: {text}")
#     return new_grammar, schema

# # ---------------------------
# # Build parser
# # ---------------------------
# def build_nl_parser(db_path: str) -> Tuple[Lark, Dict[str, List[str]]]:
#     grammar_text, schema = load_dynamic_grammar(db_path)
#     # For overlapping tokens / literals, use earley + dynamic_complete
#     parser = Lark(
#         grammar_text,
#         start="start",
#         parser="earley",
#         lexer="dynamic_complete",
#         propagate_positions=False,
#         maybe_placeholders=False,
#     )
#     print(f"âœ… Built NL parser from {db_path}")
#     # small sanity lex/parse debug: show tokens for a sample
#     try:
#         sample = "show all users"
#         print("ðŸ” sample lex tokens for:", sample)
#         for tok in parser.lex(sample):
#             print("   ", tok)
#     except Exception as e:
#         print("âš ï¸ tokenization debug failed:", e)
#     return parser, schema

# # ---------------------------
# # Global parser
# # ---------------------------
# DB_PATH = str(Path(__file__).parent / "example.db")
# enhanced_parser, current_schema = build_nl_parser(DB_PATH)

# def update_parser_for_connection(db_path: str):
#     global enhanced_parser, current_schema
#     enhanced_parser, current_schema = build_nl_parser(db_path)
#     print(f"ðŸ”„ Parser reloaded for {db_path}")

# # ---------------------------
# # Translate function
# # ---------------------------
# def translate_nl_to_sql(text: str) -> str:
#     try:
#         # lower() only for matching in grammar; if you want to preserve case for string literals, adjust accordingly
#         raw = text.lower()
#         tree = enhanced_parser.parse(raw)
#         print("ðŸŒ³ Parse tree:")
#         try:
#             print(tree.pretty())
#         except Exception:
#             print(repr(tree))
#         transformer = EnhancedNL2SQL(current_schema)
#         result = transformer.transform(tree)
#         # If transformer returned a simple string
#         if isinstance(result, str):
#             return result
#         # Lark often returns Tree/Token; handle both
#         if hasattr(result, "children") and len(result.children) == 1:
#             return str(result.children[0])
#         return str(result)
#     except Exception as e:
#         return f"-- Error translating '{text}': {e}"

# def get_supported_patterns() -> List[str]:
#     return [
#         "show all users",
#         "get name, email from users",
#         "find users where age > 25",
#         "show users ordered by name",
#     ]

# # ---------------------------
# # quick local test if run directly
# # ---------------------------
# print("\nðŸ” Lexing 'show all users'")
# for token in enhanced_parser.lex("show all users"):
#     print(f"{token.type:10} {token.value}")

if __name__ == "__main__":
    q = "show all users"
    print("\nðŸ” Query:", q)
    print(translate_nl_to_sql(q))
