# datatier.py
# Executes SQL queries against the given database.
# Zarak Khan
import sqlite3

##################################################################
#
# select_one_row:
#
# Executes a SQL SELECT query and returns the first row.
# If no row is found, returns an empty tuple. In case of an error,
# prints an error message and returns None.
#
def select_one_row(dbConn, sql, parameters=None):
    try:
        # Create a cursor object to interact with the database.
        cursor = dbConn.cursor()
        # Execute the SQL query with or without parameters.
        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)
        # Retrieve the first row from the query result.
        row = cursor.fetchone()
        # Return the row if found; otherwise, return an empty tuple.
        return row if row is not None else ()
    except Exception as e:
        # Print a specific error message and return None.
        print("select_one_row failed:", e)
        return None

##################################################################
#
# select_n_rows:
#
# Executes a SQL SELECT query and returns all rows as a list.
# If no rows are found, returns an empty list. In case of an error,
# prints an error message and returns None.
#
def select_n_rows(dbConn, sql, parameters=None):
    try:
        # Create a cursor object for executing SQL commands.
        cursor = dbConn.cursor()
        # Execute the query, using parameters if provided.
        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)
        # Fetch all rows from the result set.
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        # Print error message and return None on failure.
        print("select_n_rows failed:", e)
        return None

##################################################################
#
# perform_action:
#
# Executes a SQL action query (INSERT, UPDATE, or DELETE) and returns 
# the number of rows affected. A return value of 0 means no rows were changed.
# In case of an error, prints an error message and returns -1.
#
def perform_action(dbConn, sql, parameters=None):
    try:
        # Create a cursor to execute the SQL command.
        cursor = dbConn.cursor()
        # Execute the action query, with parameters if provided.
        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)
        # Commit the transaction to save changes to the database.
        dbConn.commit()
        # Return the number of rows modified.
        return cursor.rowcount
    except Exception as e:
        # Print error message and return -1 if an error occurs.
        print("perform_action failed:", e)
        return -1