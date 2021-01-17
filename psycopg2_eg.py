# Import the python driver for PostgreSQL
import psycopg2

# Create a connection credentials to the PostgreSQL database
try:
    connection = psycopg2.connect(
        user="morris",
        password="1205",
        host="localhost",
        port="5432",
        database="hedge_fund"
    )

    # Create a cursor connection object to a PostgreSQL instance and print the connection properties.
    cursor = connection.cursor()
    # print(connection.get_dsn_parameters(), "\n")

    # Display the PostgreSQL version installed
    # cursor.execute("SELECT version();")
    # record = cursor.fetchone()
    # print(f"You are connected into the - {record} \n")
    # cursor.close()
    # connection.close()
    # Handle the error throws by the command that is useful when using python while working with PostgreSQL
    # db.execute("INSERT INTO staff (person_id, lastname) VALUES ({person_id}, '{lastname}') ".format(person_id=50, lastname="O'Reilly".replace("'", "''")))
    cursor.execute("SELECT {fund} FROM {table} WHERE {fund} LIKE {fmt};".format(fund="\"Fund\"", table="hedge_fund_pool.\"2020-06-09-05_fund_id\"", fmt="\'%Point72%\'"))
    record = cursor.fetchall()
    print(record)

except(Exception, psycopg2.Error) as error:
    print("Error connecting to PostgreSQL database", error)
    connection = None

# Close the database connection
finally:
    if (connection != None):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is now closed")
