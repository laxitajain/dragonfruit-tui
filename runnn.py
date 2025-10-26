import duckdb

# Create a DuckDB connection (this will create sample.db file)
con = duckdb.connect('sample.db')

# Create emp table
con.execute("""
CREATE TABLE emp (
    emp_id INTEGER PRIMARY KEY,
    name VARCHAR,
    age INTEGER,
    department VARCHAR,
    salary DOUBLE,
    join_date DATE
);
""")

# Insert some sample records
con.execute("""
INSERT INTO emp VALUES
(1, 'Aarav Sharma', 29, 'Engineering', 85000.0, '2020-03-15'),
(2, 'Neha Verma', 34, 'Human Resources', 65000.0, '2018-07-10'),
(3, 'Rohan Mehta', 26, 'Marketing', 55000.0, '2021-01-12'),
(4, 'Isha Patel', 31, 'Finance', 78000.0, '2019-11-01'),
(5, 'Karan Singh', 40, 'Management', 120000.0, '2015-06-20');
""")

# Commit and close
con.close()

print("✅ sample.db created successfully with table 'emp'")
