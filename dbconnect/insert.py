import json
from dbconnect.connect import get_connection

# Function to insert product data into MySQL
def insert_product(product_data):

    # Get database connection
    connection = get_connection()

    # Create cursor
    cursor = connection.cursor()

    query = """
        INSERT INTO laptopdetails
        (url, product_name, price, availability, features, specifications)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        product_data["url"],
        product_data["product_name"],
        product_data["price"],
        product_data["availability"],
        product_data["features"],
        product_data["specifications"]
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()
    connection.close()