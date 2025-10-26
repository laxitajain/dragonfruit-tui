import pytest
from src.harlequin.nl_to_sql_enhanced import translate_nl_to_sql_enhanced, get_supported_patterns


class TestEnhancedNL2SQL:
    """Test suite for enhanced natural language to SQL translation."""

    def test_basic_select_all_variations(self):
        """Test various ways to express 'select all'."""
        queries = [
            "show all users",
            "display all users", 
            "get all users",
            "find all users",
            "list all users",
            "show users"
        ]
        expected = "SELECT * FROM users;"
        
        for query in queries:
            assert translate_nl_to_sql_enhanced(query) == expected

    def test_select_columns_variations(self):
        """Test column selection with different verbs."""
        queries = [
            "get name, email from users",
            "find name, email from users", 
            "show name, email from users"
        ]
        expected = "SELECT name, email FROM users;"
        
        for query in queries:
            assert translate_nl_to_sql_enhanced(query) == expected

    def test_where_conditions_variations(self):
        """Test WHERE clauses with different verbs."""
        queries = [
            "list users where age > 25",
            "find users where age > 25",
            "get users where age > 25", 
            "show users where age > 25"
        ]
        expected = "SELECT * FROM users WHERE age > 25;"
        
        for query in queries:
            assert translate_nl_to_sql_enhanced(query) == expected

    def test_ordering_variations(self):
        """Test ORDER BY with different directions."""
        # Default ordering
        assert translate_nl_to_sql_enhanced("show users ordered by name") == "SELECT * FROM users ORDER BY name;"
        
        # Ascending
        queries = [
            "show users ordered by name ascending",
            "show users ordered by name asc"
        ]
        expected = "SELECT * FROM users ORDER BY name ASC;"
        for query in queries:
            assert translate_nl_to_sql_enhanced(query) == expected
            
        # Descending  
        queries = [
            "show users ordered by name descending",
            "show users ordered by name desc"
        ]
        expected = "SELECT * FROM users ORDER BY name DESC;"
        for query in queries:
            assert translate_nl_to_sql_enhanced(query) == expected

    def test_group_by(self):
        """Test GROUP BY functionality."""
        assert translate_nl_to_sql_enhanced("show users grouped by department") == "SELECT * FROM users GROUP BY department;"

    def test_group_by_with_having(self):
        """Test GROUP BY with HAVING clause."""
        result = translate_nl_to_sql_enhanced("show users grouped by department having count > 5")
        assert "GROUP BY department HAVING" in result

    def test_group_by_with_order(self):
        """Test GROUP BY with ORDER BY."""
        result = translate_nl_to_sql_enhanced("show users grouped by department ordered by count")
        assert "GROUP BY department ORDER BY count" in result

    def test_aggregation_functions(self):
        """Test various aggregation functions."""
        # Count all
        count_queries = [
            "count all from users",
            "how many users"
        ]
        expected = "SELECT COUNT(*) FROM users;"
        for query in count_queries:
            assert translate_nl_to_sql_enhanced(query) == expected

        # Count distinct
        assert translate_nl_to_sql_enhanced("count distinct email from users") == "SELECT COUNT(DISTINCT email) FROM users;"

        # Sum
        sum_queries = [
            "sum salary from employees",
            "total salary from employees"
        ]
        expected = "SELECT SUM(salary) FROM employees;"
        for query in sum_queries:
            assert translate_nl_to_sql_enhanced(query) == expected

        # Average
        avg_queries = [
            "average age from users",
            "mean age from users"
        ]
        expected = "SELECT AVG(age) FROM users;"
        for query in avg_queries:
            assert translate_nl_to_sql_enhanced(query) == expected

        # Max/Min
        assert translate_nl_to_sql_enhanced("max salary from employees") == "SELECT MAX(salary) FROM employees;"
        assert translate_nl_to_sql_enhanced("min age from users") == "SELECT MIN(age) FROM users;"

    def test_join_operations(self):
        """Test different types of joins."""
        join_types = ["inner", "left", "right", "full", "outer", "cross"]
        
        for join_type in join_types:
            query = f"show users {join_type} join orders on user_id = user_id"
            result = translate_nl_to_sql_enhanced(query)
            assert f"{join_type.upper()} JOIN" in result
            assert "ON user_id = user_id" in result

    def test_enhanced_conditions(self):
        """Test enhanced condition parsing."""
        # LIKE conditions
        assert "LIKE" in translate_nl_to_sql_enhanced("find users where name like 'John%'")
        assert "NOT LIKE" in translate_nl_to_sql_enhanced("find users where name not like 'John%'")

        # IN conditions
        assert "IN" in translate_nl_to_sql_enhanced("find users where status in ('active', 'pending')")
        assert "NOT IN" in translate_nl_to_sql_enhanced("find users where status not in ('inactive')")

        # BETWEEN conditions
        assert "BETWEEN" in translate_nl_to_sql_enhanced("find users where age between 18 and 65")
        assert "NOT BETWEEN" in translate_nl_to_sql_enhanced("find users where age not between 0 and 17")

        # NULL conditions
        assert "IS NULL" in translate_nl_to_sql_enhanced("find users where email is null")
        assert "IS NOT NULL" in translate_nl_to_sql_enhanced("find users where email is not null")

    def test_logical_operators(self):
        """Test logical operators (AND, OR, NOT)."""
        # AND conditions
        result = translate_nl_to_sql_enhanced("find users where age > 18 and status = 'active'")
        assert "AND" in result

        # OR conditions  
        result = translate_nl_to_sql_enhanced("find users where name like 'A%' or name like 'B%'")
        assert "OR" in result

        # NOT conditions
        result = translate_nl_to_sql_enhanced("find users where not (age < 18)")
        assert "NOT" in result

    def test_enhanced_operators(self):
        """Test enhanced comparison operators."""
        operators = ["=", "!=", "<>", ">", "<", ">=", "<="]
        
        for op in operators:
            query = f"find users where age {op} 25"
            result = translate_nl_to_sql_enhanced(query)
            assert op in result

    def test_error_handling(self):
        """Test error handling for invalid queries."""
        invalid_queries = [
            "invalid query syntax",
            "show users where invalid condition",
            "non-existent command"
        ]
        
        for query in invalid_queries:
            result = translate_nl_to_sql_enhanced(query)
            assert result.startswith("-- Error translating")

    def test_supported_patterns(self):
        """Test that get_supported_patterns returns expected content."""
        patterns = get_supported_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert "Basic Queries:" in patterns
        assert "Aggregations:" in patterns
        assert "Joins:" in patterns

    def test_case_insensitivity(self):
        """Test that queries work regardless of case."""
        queries = [
            "SHOW ALL USERS",
            "Get Name, Email From Users", 
            "FIND users WHERE age > 25"
        ]
        
        expected_results = [
            "SELECT * FROM users;",
            "SELECT Name, Email FROM Users;",
            "SELECT * FROM users WHERE age > 25;"
        ]
        
        for query, expected in zip(queries, expected_results):
            assert translate_nl_to_sql_enhanced(query) == expected

    def test_complex_queries(self):
        """Test complex queries combining multiple features."""
        # Complex WHERE with multiple conditions
        query = "find users where age > 18 and status = 'active' and name like 'A%'"
        result = translate_nl_to_sql_enhanced(query)
        assert "WHERE" in result
        assert "AND" in result
        assert "LIKE" in result

        # GROUP BY with HAVING and ORDER BY
        query = "show users grouped by department having count > 5 ordered by count desc"
        result = translate_nl_to_sql_enhanced(query)
        assert "GROUP BY" in result
        assert "HAVING" in result
        assert "ORDER BY" in result
        assert "DESC" in result


if __name__ == "__main__":
    pytest.main([__file__])

