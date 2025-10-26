# Quick Reference: Enhanced NL-to-SQL Grammar

## Most Common Patterns

### Basic Queries

| Input                        | Output                                |
| ---------------------------- | ------------------------------------- |
| `show all users`             | `SELECT * FROM users;`                |
| `get name, email from users` | `SELECT name, email FROM users;`      |
| `find users where age > 25`  | `SELECT * FROM users WHERE age > 25;` |

### Natural Language Variations

- **Show/Display/Get/Find/List** - All work for basic queries
- **All** - Optional in most contexts
- **Case insensitive** - Works with any capitalization

### Enhanced Operators

| Operator | Example     | SQL         |
| -------- | ----------- | ----------- |
| `=`      | `age = 25`  | `age = 25`  |
| `!=`     | `age != 25` | `age != 25` |
| `<>`     | `age <> 25` | `age <> 25` |
| `>`      | `age > 25`  | `age > 25`  |
| `<`      | `age < 25`  | `age < 25`  |
| `>=`     | `age >= 25` | `age >= 25` |
| `<=`     | `age <= 25` | `age <= 25` |

### String Patterns

| Input                      | Output                     |
| -------------------------- | -------------------------- |
| `name like 'John%'`        | `name LIKE 'John%'`        |
| `name not like 'John%'`    | `name NOT LIKE 'John%'`    |
| `email like '%@gmail.com'` | `email LIKE '%@gmail.com'` |

### IN Conditions

| Input                             | Output                            |
| --------------------------------- | --------------------------------- |
| `status in ('active', 'pending')` | `status IN ('active', 'pending')` |
| `department in ('IT', 'HR')`      | `department IN ('IT', 'HR')`      |

### BETWEEN Conditions

| Input                             | Output                            |
| --------------------------------- | --------------------------------- |
| `age between 18 and 65`           | `age BETWEEN 18 AND 65`           |
| `salary between 50000 and 100000` | `salary BETWEEN 50000 AND 100000` |

### NULL Handling

| Input               | Output              |
| ------------------- | ------------------- |
| `email is null`     | `email IS NULL`     |
| `phone is not null` | `phone IS NOT NULL` |

### Logical Operators

| Input                              | Output                                 |
| ---------------------------------- | -------------------------------------- |
| `age > 18 and status = 'active'`   | `(age > 18) AND (status = 'active')`   |
| `name like 'A%' or name like 'B%'` | `(name LIKE 'A%') OR (name LIKE 'B%')` |
| `not (age < 18)`                   | `NOT (age < 18)`                       |

### Ordering

| Input                          | Output                 |
| ------------------------------ | ---------------------- |
| `ordered by name`              | `ORDER BY name`        |
| `ordered by age ascending`     | `ORDER BY age ASC`     |
| `ordered by salary descending` | `ORDER BY salary DESC` |

### Aggregations

| Input                       | Output                               |
| --------------------------- | ------------------------------------ |
| `count all from users`      | `SELECT COUNT(*) FROM users;`        |
| `how many users`            | `SELECT COUNT(*) FROM users;`        |
| `sum salary from employees` | `SELECT SUM(salary) FROM employees;` |
| `average age from users`    | `SELECT AVG(age) FROM users;`        |
| `max salary from employees` | `SELECT MAX(salary) FROM employees;` |
| `min age from users`        | `SELECT MIN(age) FROM users;`        |

### GROUP BY

| Input                                    | Output                                 |
| ---------------------------------------- | -------------------------------------- |
| `grouped by department`                  | `GROUP BY department`                  |
| `grouped by department having count > 5` | `GROUP BY department HAVING count > 5` |

### JOINs

| Input                                               | Output                                              |
| --------------------------------------------------- | --------------------------------------------------- |
| `inner join orders on user_id = user_id`            | `INNER JOIN orders ON user_id = user_id`            |
| `left join profiles on users.id = profiles.user_id` | `LEFT JOIN profiles ON users.id = profiles.user_id` |
| `right join orders on users.id = orders.user_id`    | `RIGHT JOIN orders ON users.id = orders.user_id`    |
| `full join orders on users.id = orders.user_id`     | `FULL JOIN orders ON users.id = orders.user_id`     |

## Complex Examples

### Multi-condition WHERE

```
find users where age > 18 and status = 'active' and department = 'IT'
→ SELECT * FROM users WHERE (age > 18) AND (status = 'active') AND (department = 'IT');
```

### Complex Logical Expression

```
find users where (age > 18 and status = 'active') or (age > 21 and status = 'pending')
→ SELECT * FROM users WHERE ((age > 18) AND (status = 'active')) OR ((age > 21) AND (status = 'pending'));
```

### JOIN with WHERE

```
show users inner join orders on users.id = orders.user_id where orders.amount > 100
→ SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id WHERE orders.amount > 100;
```

## Error Handling

Invalid queries return helpful error messages:

```
invalid query syntax
→ -- Error translating 'invalid query syntax': ...
```

## Tips

1. **Use natural language** - The grammar supports many variations
2. **Case doesn't matter** - Works with any capitalization
3. **Parentheses help** - Use them for complex logical expressions
4. **Be specific** - More specific queries often work better
5. **Test incrementally** - Start with simple queries and add complexity

## Supported Features

✅ **Basic SELECT operations**
✅ **Column selection**
✅ **WHERE conditions**
✅ **Enhanced operators** (=, !=, <>, >, <, >=, <=)
✅ **String patterns** (LIKE, NOT LIKE)
✅ **IN conditions** (IN, NOT IN)
✅ **BETWEEN conditions** (BETWEEN, NOT BETWEEN)
✅ **NULL handling** (IS NULL, IS NOT NULL)
✅ **Logical operators** (AND, OR, NOT)
✅ **Ordering** (ORDER BY, ASC, DESC)
✅ **Aggregations** (COUNT, SUM, AVG, MAX, MIN)
✅ **GROUP BY** (with HAVING)
✅ **JOINs** (INNER, LEFT, RIGHT, FULL, CROSS)
✅ **Error handling** with helpful messages
✅ **Case insensitive** parsing

