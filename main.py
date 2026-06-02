import streamlit as st
import pandas as pd
import sqlite3


# PAGE CONFIG

st.set_page_config(
    page_title="Restaurant Analytics",
    layout="wide"
)


# DATABASE CONNECTION

conn = sqlite3.connect("uber.db")


# FUNCTION TO RUN QUERY

def get_data(query):
    return pd.read_sql_query(query, conn)


# LOAD TABLES

try:
    df1 = pd.read_sql_query("SELECT * FROM uber_eats", conn)
    df2 = pd.read_sql_query("SELECT * FROM order_list", conn)
except:
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()


# SIDEBAR

page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "DataFrames", "SQL Queries"]
)


# HOME PAGE

if page == "Home":

    st.title("🍔 Uber Eats Analytics Dashboard")

    st.subheader("1,Project UBER EATS")
    st.write("Uber Eats Restaurant Analysis")

    st.subheader("About Me")
    st.write("Dhanush DB")

# DATAFRAME PAGE

elif page == "DataFrames":

    st.title("📊 DataFrames")

    option = st.selectbox(
        "Choose DataFrame",
        ["uber_eats", "order_list"]
    )

    if option == "uber_eats":
        st.dataframe(df1)

    elif option == "order_list":
        st.dataframe(df2)

# SQL QUERIES PAGE

elif page == "SQL Queries":

    st.title("📋 SQL Query Results")

    queries={

        "1,Which Bangalore locations have the highest average restaurant ratings?":
        """
        SELECT location,
               AVG(rate) AS avg_rating
        FROM uber_eats
        GROUP BY location
        ORDER BY avg_rating DESC LIMIT 1;
        """,

        "2,Which cuisines are most common in Bangalore?":
        """
        SELECT cuisines,
               COUNT(*) AS cuisine_count
        FROM uber_eats
        GROUP BY cuisines
        ORDER BY cuisine_count DESC LIMIT 1;
        """,

        "3,Which locations are over-saturated with restaurants?":
        """
        SELECT location,
               COUNT(*) AS restaurant_count
        FROM uber_eats
        GROUP BY location
        ORDER BY restaurant_count DESC;
        """,

        "4,What price range delivers the best customer satisfaction?":
        """
        SELECT
            "approx_cost(for two people)" AS price_range,
            AVG(rate) AS average_rating
        FROM uber_eats
        GROUP BY "approx_cost(for two people)"
        ORDER BY average_rating DESC;
        """,

        "5,Does online ordering improve restaurant rating?":
        """
        SELECT
               CASE 
                  WHEN online_order = 'Yes' THEN 'Online Ordering' 
                  ELSE 'No Online Ordering' 
               END AS online_order_status, 
               AVG(rate) as average_rating 
        FROM uber_eats 
        GROUP BY online_order_status
        ORDER BY average_rating DESC;
        """,

        "6,Which location have low rating?":
        """
        SELECT location, rate
        FROM uber_eats
        WHERE rate =
        (
            SELECT MIN(rate)
            FROM uber_eats
            
        )
        ORDER BY rate ASC
        LIMIT 1;
        """,

        "7, which restuarent have more order value ?":
        """
        SELECT restaurant_name,
               order_value
        FROM order_list
        WHERE order_value =
        (
            SELECT MAX(order_value)
            FROM order_list
            
        )
        ORDER BY order_value DESC
        LIMIT 1;
        """,

        "8. Restaurant Total Revenue ?":
        """
        SELECT restaurant_name,
               SUM(order_value) AS total_revenue
        FROM order_list
        GROUP BY restaurant_name
        ORDER BY total_revenue DESC;
        """,

        "9. Highest Single Order By Restaurant?":
        """
        SELECT restaurant_name,
               MAX(order_value) AS highest_order
        FROM order_list
        GROUP BY restaurant_name
        ORDER BY highest_order DESC;
        """,

        "10. Payment Method Usage":
        """
        SELECT payment_method,
               COUNT(*) AS usage_count
        FROM order_list
        GROUP BY payment_method
        ORDER BY usage_count DESC;
        """
    }

    selected_query = st.selectbox(
        "Select Query",
        list(queries.keys())
    )

    st.subheader("SQL Query")

    st.code(
        queries[selected_query],
        language="sql"
    )

    result = get_data(
        queries[selected_query]
    )

    st.subheader("Output")

    st.dataframe(result)

# ---------------------------------
# FOOTER
# ---------------------------------
st.sidebar.markdown("---")
st.sidebar.write("Created by Dhanush DB")