import pymysql
import boto3
import json
from prettytable import PrettyTable
import os

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PW = os.environ['DB_PW']
DB_NAME = os.environ['DB_NAME']

DEFAULT_QUERY = "SELECT * FROM customer_statement"

# Database connection function
def connect_to_database(host, user, password, database):
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PW,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_customer_transations(sql=DEFAULT_QUERY):
    print("Connecting to connect to %s" % DB_HOST)
    connection = connect_to_database(DB_HOST, DB_USER, DB_PW, DB_NAME)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    results = query_bank_statement(connection)

    # Print the results
    for row in results:
        print(row)

    # Close the connection
    connection.close()

def prettyprint(data):
    if not data:
        return "No data available."

    # Extract headers from the first dictionary
    headers = data[0].keys()

    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = headers

    # Add rows to the table
    for item in data:
        table.add_row(item.values())

    # Return the string representation of the table
    print(table.get_string())

def main():
        result = execute_query()
        prettyprint(result)

if __name__ == "__main__":
    main()
