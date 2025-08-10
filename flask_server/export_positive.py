import pandas as pd
import pymysql

# connects to the MySQL database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='qian010529',   
    database='perfume_db',
    charset='utf8mb4'
)

# Execute the query and save it as a CSV file
query = "SELECT name AS product_title, description, positive_rate FROM products"
df = pd.read_sql(query, conn)
df.to_csv("fragrance_with_positive.csv", index=False)

conn.close()
print("successfully exported fragrance_with_positive.csv")
