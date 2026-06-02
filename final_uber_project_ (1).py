import pandas as pd


#import data uber_eats
uber_data=pd.read_csv('D:/vscodeprograms/Uber_Eats_data.csv')

#Datashape
uber_data.shape

#DELITE DUPLICATE VALUE
uber_data.drop_duplicates(uber_data)

#value counts
uber_data['name'].value_counts()

#ONLY ASSIGNMENT COLUMNS
x=uber_data.drop(columns=['dish_liked', 'votes' ,'phone' ,'rest_type','listed_in(type)','listed_in(city)'])

#IN  DATA FRAME
uber_final=pd.DataFrame(x)

uber_final.shape

uber_final.value_counts()

uber_final.head(10)

uber_final.isnull().sum()

"""REMOVE DUPLICATE DATA FOR ASSIGNMENT FEATURES"""

final_ans=uber_final.drop_duplicates(uber_final)

final_ans.shape

uber_final.value_counts()

final_ans['rate'] = final_ans['rate'].astype(str).str.replace('/5', '').str.strip()
print(final_ans['rate'].head())

final_ans.head()

"""### order data jeson"""

order=pd.read_json('D:/vscodeprograms/orders.json')

order.head()

order.shape

order.drop_duplicates(order)

order.value_counts(['restaurant_name','order_value'])

order.isnull().sum()

"""update the two dats in sql"""

import sqlite3

connection=sqlite3.connect('uber.db')
cursor=connection.cursor()

#uber_final table
cursor.execute("""CREATE TABLE IF NOT EXISTS uber_eats(
    name VARCHAR(50),
    online_order VARCHAR(50),
    book_table VARCHAR(50),
    rate FLOAT,
    location VARCHAR(50),
    cuisines VARCHAR(50),
    "approx_cost(for two people)" INT
)""")
connection.commit()
print("Table 'uber_eats' created successfully in SQLite!")

data_list =final_ans.values.tolist()
query = """
    INSERT INTO uber_eats(name,online_order,book_table,rate,location,cuisines,"approx_cost(for two people)")
    VALUES (?,?,?,?,?,?,?);
"""
cursor.executemany(query, data_list)
cursor.connection.commit()
print("Uber_final data inserted successfully into 'uber_final' table!")

cursor.execute("""CREATE TABLE IF NOT EXISTS order_list (order_id VARCHAR(50),
restaurant_name VARCHAR(50),
order_date DATE,
order_value INT,
discount_used VARCHAR(50),
payment_method VARCHAR(50)
)""")
connection.commit()
print("Table 'uber' created successfully in SQLite!")

data_list = order.values.tolist()
query = """
    INSERT INTO order_list (order_id, restaurant_name, order_date,
    order_value, discount_used, payment_method)
    VALUES (?,?,?,?,?,?);
"""
connection.executemany(query, data_list)
connection.commit()
print("Order data inserted successfully using to_list()")

"""quarys SQL"""

query = "SELECT * FROM uber_eats"
cursor.execute(query)
results = cursor.fetchall()
uber_eats_table=pd.DataFrame(results)
print(uber_eats_table)

query = "SELECT * FROM order_list"
cursor.execute(query)
results = cursor.fetchall()
order_table=pd.DataFrame(results)
print(order_table)

#uber_eats and order_list

#1,Which Bangalore locations have the highest average restaurant ratings?
from tabulate import tabulate

query1 = "SELECT location, AVG(rate) AS avg_rating  FROM uber_eats GROUP BY location ORDER BY AVG(rate) DESC LIMIT 1;"
cursor.execute(query1)
result1 = cursor.fetchall()

# Define table headers
headers = ["LOCATION", "RATING"]

# Print the result as a table
print(tabulate(result1, headers=headers, tablefmt="grid"))

#2,Which cuisines are most common in Bangalore?
from tabulate import tabulate

query1 = "SELECT cuisines, COUNT(*) AS cuisines_cout FROM uber_eats GROUP BY cuisines ORDER BY cuisines_cout DESC LIMIT 1;"
cursor.execute(query1)
result1 = cursor.fetchall()

headers = ["CUISINES","COUNTS"]

print(tabulate(result1, headers=headers, tablefmt="grid"))

#3,Which locations are over-saturated with restaurants?
from tabulate import tabulate

query1 = "SELECT location, COUNT(*)name  FROM uber_eats GROUP BY location ORDER BY name DESC  LIMIT 1;"
cursor.execute(query1)
result1 = cursor.fetchall()

headers = [ "LOCATION"," RESTAURANTS"]

print(tabulate(result1, headers=headers, tablefmt="grid"))

#4,What price range delivers the best customer satisfaction?
from tabulate import tabulate

query2 = """SELECT "approx_cost(for two people)",AVG(rate) AS average_rating FROM uber_eats GROUP BY "approx_cost(for two people)" ORDER BY average_rating DESC LIMIT 1;"""
cursor.execute(query2)
result2 = cursor.fetchall()

headers = ["Approximate Cost (for two people)", "Average Rating"]

print(tabulate(result2, headers=headers, tablefmt="grid"))

#5,Does online ordering improve restaurant rating?
query2=""" SELECT
               CASE
                  WHEN online_order = 'Yes' THEN 'Online Ordering'
                  ELSE 'No Online Ordering'
               END AS online_order_status,
                AVG(rate) as average_rating
            FROM uber_eats
            GROUP BY online_order_status
            ORDER BY average_rating DESC;"""
cursor.execute(query2)
result1= cursor.fetchall()
print(tabulate (result1, headers=["Online Order Status","Average Rating"], tablefmt="grid"))

#6,Which location have low rating ?
query2=""" SELECT location , rate FROM uber_eats WHERE rate = (SELECT MIN (rate) FROM uber_eats ORDER BY rate ASC LIMIT 1 );"""
cursor.execute(query2)
result=cursor.fetchall()
print(result)

#7, which restuarent have more order value ?
query= """SELECT restaurant_name, order_value FROM order_list  WHERE order_value = (SELECT MAX (order_value) FROM order_list ORDER BY order_value ASC LIMIT 1);"""
cursor.execute(query)
result=cursor.fetchall()
print(result)

#8. Restaurant and Total Revenue ?
query="""SELECT restaurant_name,SUM(order_value) AS total_revenue FROM order_list GROUP BY restaurant_name ORDER BY total_revenue DESC;"""
cursor.execute(query)
result=cursor.fetchall()
print([result])

#9, which restuarent have more order value?
query= """SELECT  restaurant_name , MAX(order_value) FROM order_list ;"""
cursor.execute(query)
result=cursor.fetchall()
print(result)

#10. Payment Method Usage?
query= """SELECT payment_method, COUNT(*) AS usage_count FROM order_list GROUP BY payment_method ORDER BY usage_count DESC;"""
cursor.execute(query)
result=cursor.fetchall()
print(result)

#