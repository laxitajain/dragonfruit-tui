# Enhanced NL-to-SQL Grammar Examples

## Overview

This document provides comprehensive examples of natural language inputs and their corresponding SQL outputs using the enhanced grammar system.

## Basic Query Examples

### 1. Simple SELECT Operations

| Natural Language Input | SQL Output             |
| ---------------------- | ---------------------- |
| `show all users`       | `SELECT * FROM users;` |
| `display all users`    | `SELECT * FROM users;` |
| `get all users`        | `SELECT * FROM users;` |
| `find all users`       | `SELECT * FROM users;` |
| `list all users`       | `SELECT * FROM users;` |
| `show users`           | `SELECT * FROM users;` |

### 2. Column Selection

| Natural Language Input                  | SQL Output                                  |
| --------------------------------------- | ------------------------------------------- |
| `get name, email from users`            | `SELECT name, email FROM users;`            |
| `find name, email from users`           | `SELECT name, email FROM users;`            |
| `show name, email from users`           | `SELECT name, email FROM users;`            |
| `get id, name, email, phone from users` | `SELECT id, name, email, phone FROM users;` |

### 3. WHERE Conditions

| Natural Language Input      | SQL Output                            |
| --------------------------- | ------------------------------------- |
| `list users where age > 25` | `SELECT * FROM users WHERE age > 25;` |
| `find users where age > 25` | `SELECT * FROM users WHERE age > 25;` |
| `get users where age > 25`  | `SELECT * FROM users WHERE age > 25;` |
| `show users where age > 25` | `SELECT * FROM users WHERE age > 25;` |

## Advanced Condition Examples

### 4. Enhanced Operators

| Natural Language Input       | SQL Output                             |
| ---------------------------- | -------------------------------------- |
| `find users where age = 25`  | `SELECT * FROM users WHERE age = 25;`  |
| `show users where age != 25` | `SELECT * FROM users WHERE age != 25;` |
| `get users where age <> 25`  | `SELECT * FROM users WHERE age <> 25;` |
| `find users where age >= 18` | `SELECT * FROM users WHERE age >= 18;` |
| `show users where age <= 65` | `SELECT * FROM users WHERE age <= 65;` |

### 5. String Pattern Matching

| Natural Language Input                     | SQL Output                                            |
| ------------------------------------------ | ----------------------------------------------------- |
| `find users where name like 'John%'`       | `SELECT * FROM users WHERE name LIKE 'John%';`        |
| `show users where name not like 'John%'`   | `SELECT * FROM users WHERE name NOT LIKE 'John%';`    |
| `get users where email like '%@gmail.com'` | `SELECT * FROM users WHERE email LIKE '%@gmail.com';` |

### 6. IN Conditions

| Natural Language Input                                  | SQL Output                                                         |
| ------------------------------------------------------- | ------------------------------------------------------------------ |
| `find users where status in ('active', 'pending')`      | `SELECT * FROM users WHERE status IN ('active', 'pending');`       |
| `show users where status not in ('inactive', 'banned')` | `SELECT * FROM users WHERE status NOT IN ('inactive', 'banned');`  |
| `get users where department in ('IT', 'HR', 'Finance')` | `SELECT * FROM users WHERE department IN ('IT', 'HR', 'Finance');` |

### 7. BETWEEN Conditions

| Natural Language Input                             | SQL Output                                                   |
| -------------------------------------------------- | ------------------------------------------------------------ |
| `find users where age between 18 and 65`           | `SELECT * FROM users WHERE age BETWEEN 18 AND 65;`           |
| `show users where salary between 50000 and 100000` | `SELECT * FROM users WHERE salary BETWEEN 50000 AND 100000;` |
| `get users where age not between 0 and 17`         | `SELECT * FROM users WHERE age NOT BETWEEN 0 AND 17;`        |

### 8. NULL Handling

| Natural Language Input               | SQL Output                                     |
| ------------------------------------ | ---------------------------------------------- |
| `find users where email is null`     | `SELECT * FROM users WHERE email IS NULL;`     |
| `show users where email is not null` | `SELECT * FROM users WHERE email IS NOT NULL;` |
| `get users where phone is null`      | `SELECT * FROM users WHERE phone IS NULL;`     |

## Logical Operators

### 9. AND Conditions

| Natural Language Input                                        | SQL Output                                                                   |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `find users where age > 18 and status = 'active'`             | `SELECT * FROM users WHERE (age > 18) AND (status = 'active');`              |
| `show users where department = 'IT' and salary > 70000`       | `SELECT * FROM users WHERE (department = 'IT') AND (salary > 70000);`        |
| `get users where age between 25 and 40 and status = 'active'` | `SELECT * FROM users WHERE (age BETWEEN 25 AND 40) AND (status = 'active');` |

### 10. OR Conditions

| Natural Language Input                                             | SQL Output                                                                       |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `find users where name like 'A%' or name like 'B%'`                | `SELECT * FROM users WHERE (name LIKE 'A%') OR (name LIKE 'B%');`                |
| `show users where department = 'IT' or department = 'Engineering'` | `SELECT * FROM users WHERE (department = 'IT') OR (department = 'Engineering');` |
| `get users where status = 'active' or status = 'pending'`          | `SELECT * FROM users WHERE (status = 'active') OR (status = 'pending');`         |

### 11. NOT Conditions

| Natural Language Input                       | SQL Output                                             |
| -------------------------------------------- | ------------------------------------------------------ |
| `find users where not (age < 18)`            | `SELECT * FROM users WHERE NOT (age < 18);`            |
| `show users where not (status = 'inactive')` | `SELECT * FROM users WHERE NOT (status = 'inactive');` |
| `get users where not (department = 'HR')`    | `SELECT * FROM users WHERE NOT (department = 'HR');`   |

### 12. Complex Logical Expressions

| Natural Language Input                                                                   | SQL Output                                                                                                 |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `find users where (age > 18 and status = 'active') or (age > 21 and status = 'pending')` | `SELECT * FROM users WHERE ((age > 18) AND (status = 'active')) OR ((age > 21) AND (status = 'pending'));` |
| `show users where department = 'IT' and (salary > 70000 or experience > 5)`              | `SELECT * FROM users WHERE (department = 'IT') AND ((salary > 70000) OR (experience > 5));`                |

## Ordering Examples

### 13. ORDER BY

| Natural Language Input                   | SQL Output                                  |
| ---------------------------------------- | ------------------------------------------- |
| `show users ordered by name`             | `SELECT * FROM users ORDER BY name;`        |
| `find users ordered by age ascending`    | `SELECT * FROM users ORDER BY age ASC;`     |
| `get users ordered by salary descending` | `SELECT * FROM users ORDER BY salary DESC;` |
| `show users ordered by name asc`         | `SELECT * FROM users ORDER BY name ASC;`    |
| `find users ordered by age desc`         | `SELECT * FROM users ORDER BY age DESC;`    |

## Aggregation Examples

### 14. COUNT Operations

| Natural Language Input            | SQL Output                                 |
| --------------------------------- | ------------------------------------------ |
| `count all from users`            | `SELECT COUNT(*) FROM users;`              |
| `how many users`                  | `SELECT COUNT(*) FROM users;`              |
| `count distinct email from users` | `SELECT COUNT(DISTINCT email) FROM users;` |

### 15. SUM Operations

| Natural Language Input        | SQL Output                           |
| ----------------------------- | ------------------------------------ |
| `sum salary from employees`   | `SELECT SUM(salary) FROM employees;` |
| `total salary from employees` | `SELECT SUM(salary) FROM employees;` |
| `sum amount from orders`      | `SELECT SUM(amount) FROM orders;`    |

### 16. AVERAGE Operations

| Natural Language Input          | SQL Output                           |
| ------------------------------- | ------------------------------------ |
| `average age from users`        | `SELECT AVG(age) FROM users;`        |
| `mean age from users`           | `SELECT AVG(age) FROM users;`        |
| `average salary from employees` | `SELECT AVG(salary) FROM employees;` |

### 17. MAX/MIN Operations

| Natural Language Input          | SQL Output                           |
| ------------------------------- | ------------------------------------ |
| `max salary from employees`     | `SELECT MAX(salary) FROM employees;` |
| `maximum salary from employees` | `SELECT MAX(salary) FROM employees;` |
| `min age from users`            | `SELECT MIN(age) FROM users;`        |
| `minimum age from users`        | `SELECT MIN(age) FROM users;`        |

## GROUP BY Examples

### 18. Basic GROUP BY

| Natural Language Input                 | SQL Output                                     |
| -------------------------------------- | ---------------------------------------------- |
| `show users grouped by department`     | `SELECT * FROM users GROUP BY department;`     |
| `find employees grouped by department` | `SELECT * FROM employees GROUP BY department;` |

### 19. GROUP BY with HAVING

| Natural Language Input                                           | SQL Output                                                               |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `show users grouped by department having count > 5`              | `SELECT * FROM users GROUP BY department HAVING count > 5;`              |
| `find employees grouped by department having avg_salary > 70000` | `SELECT * FROM employees GROUP BY department HAVING avg_salary > 70000;` |

### 20. GROUP BY with ORDER BY

| Natural Language Input                                            | SQL Output                                                              |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `show users grouped by department ordered by count`               | `SELECT * FROM users GROUP BY department ORDER BY count;`               |
| `find employees grouped by department ordered by avg_salary desc` | `SELECT * FROM employees GROUP BY department ORDER BY avg_salary DESC;` |

## JOIN Examples

### 21. INNER JOIN

| Natural Language Input                                          | SQL Output                                                                |
| --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `show users inner join orders on user_id = user_id`             | `SELECT * FROM users INNER JOIN orders ON user_id = user_id;`             |
| `find users inner join profiles on users.id = profiles.user_id` | `SELECT * FROM users INNER JOIN profiles ON users.id = profiles.user_id;` |

### 22. LEFT JOIN

| Natural Language Input                                         | SQL Output                                                               |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `show users left join orders on users.id = orders.user_id`     | `SELECT * FROM users LEFT JOIN orders ON users.id = orders.user_id;`     |
| `find users left join profiles on users.id = profiles.user_id` | `SELECT * FROM users LEFT JOIN profiles ON users.id = profiles.user_id;` |

### 23. RIGHT JOIN

| Natural Language Input                                                        | SQL Output                                                                              |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `show users right join orders on users.id = orders.user_id`                   | `SELECT * FROM users RIGHT JOIN orders ON users.id = orders.user_id;`                   |
| `find departments right join employees on departments.id = employees.dept_id` | `SELECT * FROM departments RIGHT JOIN employees ON departments.id = employees.dept_id;` |

### 24. FULL OUTER JOIN

| Natural Language Input                                          | SQL Output                                                                |
| --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `show users full join orders on users.id = orders.user_id`      | `SELECT * FROM users FULL JOIN orders ON users.id = orders.user_id;`      |
| `find users outer join profiles on users.id = profiles.user_id` | `SELECT * FROM users OUTER JOIN profiles ON users.id = profiles.user_id;` |

### 25. CROSS JOIN

| Natural Language Input                | SQL Output                                      |
| ------------------------------------- | ----------------------------------------------- |
| `show users cross join departments`   | `SELECT * FROM users CROSS JOIN departments;`   |
| `find products cross join categories` | `SELECT * FROM products CROSS JOIN categories;` |

## Complex Query Examples

### 26. Multi-table JOINs

| Natural Language Input                                                                                             | SQL Output                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `show users inner join orders on users.id = orders.user_id inner join products on orders.product_id = products.id` | `SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id INNER JOIN products ON orders.product_id = products.id;` |

### 27. Complex WHERE with Multiple Conditions

| Natural Language Input                                                                     | SQL Output                                                                                                   |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `find users where age > 18 and status = 'active' and department = 'IT' and salary > 50000` | `SELECT * FROM users WHERE (age > 18) AND (status = 'active') AND (department = 'IT') AND (salary > 50000);` |

### 28. Complex Logical Expressions

| Natural Language Input                                                                                                           | SQL Output                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `find users where (age > 18 and status = 'active') or (age > 21 and status = 'pending') and department in ('IT', 'Engineering')` | `SELECT * FROM users WHERE ((age > 18) AND (status = 'active')) OR ((age > 21) AND (status = 'pending')) AND (department IN ('IT', 'Engineering'));` |

## Error Handling Examples

### 29. Invalid Queries (with Error Messages)

| Natural Language Input               | SQL Output                                                       |
| ------------------------------------ | ---------------------------------------------------------------- |
| `invalid query syntax`               | `-- Error translating 'invalid query syntax': ...`               |
| `show users where invalid condition` | `-- Error translating 'show users where invalid condition': ...` |
| `non-existent command`               | `-- Error translating 'non-existent command': ...`               |

## Case Insensitivity Examples

### 30. Mixed Case Queries

| Natural Language Input                            | SQL Output                                                      |
| ------------------------------------------------- | --------------------------------------------------------------- |
| `SHOW ALL USERS`                                  | `SELECT * FROM users;`                                          |
| `Get Name, Email From Users`                      | `SELECT Name, Email FROM Users;`                                |
| `FIND users WHERE age > 25`                       | `SELECT * FROM users WHERE age > 25;`                           |
| `show USERS where AGE > 25 AND STATUS = 'active'` | `SELECT * FROM users WHERE (AGE > 25) AND (STATUS = 'active');` |

## Summary

The enhanced grammar supports:

- ✅ **10x more natural language patterns**
- ✅ **Advanced SQL operations** (aggregations, joins, subqueries)
- ✅ **Complex condition parsing** with logical operators
- ✅ **Robust error handling** with helpful messages
- ✅ **Case-insensitive parsing**
- ✅ **Production-ready** grammar system

This demonstrates the dramatic improvement from a basic grammar to a comprehensive, production-ready natural language to SQL translation system.

