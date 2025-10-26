# create_duckdb.py

import duckdb

def create_example_db():
    # Connect to (or create) example.db
    conn = duckdb.connect("example.db")

    # Create a sample table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER,
            name VARCHAR,
            age INTEGER
        )
    """)

    # Insert some sample data
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
    conn.execute("INSERT INTO users VALUES (3, 'Charlie', 35)")

    # Commit and close
    conn.close()
    print("✅ example.db created with table `users`.")

if __name__ == "__main__":
    create_example_db()
