# database_setup.py
import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect("company.db")
cursor = conn.cursor()

# Drop tables if they already exist (for re-running the script)
cursor.execute("DROP TABLE IF EXISTS Employees")
cursor.execute("DROP TABLE IF EXISTS Departments")

# Create Employees table
cursor.execute("""
    CREATE TABLE Employees (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Department TEXT,
        Salary INTEGER,
        Hire_Date TEXT
    )
""")

# Create Departments table
cursor.execute("""
    CREATE TABLE Departments (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Manager TEXT
    )
""")

# Insert sample data into Employees
employees = [
    (1, 'Alice', 'Sales', 50000, '2021-01-15'),
    (2, 'Bob', 'Engineering', 70000, '2020-06-10'),
    (3, 'Charlie', 'Marketing', 60000, '2022-03-20')
]
cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?, ?)", employees)

# Insert sample data into Departments
departments = [
    (1, 'Sales', 'Alice'),
    (2, 'Engineering', 'Bob'),
    (3, 'Marketing', 'Charlie')
]
cursor.executemany("INSERT INTO Departments VALUES (?, ?, ?)", departments)

# Commit and close the connection
conn.commit()
conn.close()

print("Database created and sample data inserted into company.db.")
