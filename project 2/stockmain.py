import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Stock Market Analysis Dashboard",
    layout="wide"
)
# HOME PAGE
st.title("📈 DATA DRIVEN STOCK ANALYSIS")

st.subheader("2,PROJECT DATA DRIVEN STOCK ANALYSIS")
st.write("DATA DRIVEN STOCK ANALYSIS")

st.sidebar.header("About Me")
st.sidebar.write("Dhanush DB")


# Database connection
conn = sqlite3.connect("stock1.db")
# FUNCTION TO RUN QUERY

def get_data(query):
    return pd.read_sql_query(query, conn)

# LOAD TABLES
try:
    df = pd.read_sql_query("SELECT * FROM stock_data", conn)   
except:
    df = pd.DataFrame()

# Sidebar2 Questions

question = st.selectbox(
    "Select Analysis",
    [
        "Volatility Analysis",
        "Cumulative Return Over Time",
        "Sector-wise Performance",
        "Stock Price Correlation",
        "Top 5 Gainers and Losers"
    ]
)

# --------------------------------------------------
# 1. Volatility Analysis
# --------------------------------------------------
if question == "Volatility Analysis":

    st.header("1️⃣ Volatility Analysis")

    query = """
    WITH daily_returns AS (
        SELECT
            Ticker,
            date,
            (close - LAG(close) OVER (
                PARTITION BY Ticker
                ORDER BY date
            )) /
            LAG(close) OVER (
                PARTITION BY Ticker
                ORDER BY date
            ) AS daily_return
        FROM stock_data
    ),
    stats AS (
        SELECT
            Ticker,
            AVG(daily_return) AS mean_return,
            COUNT(*) AS n
        FROM daily_returns
        WHERE daily_return IS NOT NULL
        GROUP BY Ticker
    )
    SELECT
        dr.Ticker,
        SQRT(
            SUM(
                (dr.daily_return - s.mean_return) *
                (dr.daily_return - s.mean_return)
            ) / s.n
        ) AS volatility
    FROM daily_returns dr
    JOIN stats s
    ON dr.Ticker=s.Ticker
    WHERE dr.daily_return IS NOT NULL
    GROUP BY dr.Ticker
    ORDER BY volatility DESC
    LIMIT 10;
    """

    df = get_data(query)

    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(df["Ticker"], df["volatility"])
    ax.set_title("Top 10 Most Volatile Stocks")
    ax.set_ylabel("Volatility")
    plt.xticks(rotation=45)

    st.pyplot(fig)

# --------------------------------------------------
elif question == "Cumulative Return Over Time":

    st.header("2️⃣ Cumulative Return Over Time")

    query = """
    WITH daily_returns AS (
        SELECT
            Ticker,
            date,
            (
                (close - LAG(close) OVER (
                    PARTITION BY Ticker
                    ORDER BY date
                ))
                /
                LAG(close) OVER (
                    PARTITION BY Ticker
                    ORDER BY date
                )
            ) * 100 AS daily_return
        FROM stock_data
    ),

    cumulative_returns AS (
        SELECT
            Ticker,
            date,
            SUM(
                COALESCE(daily_return,0)
            ) OVER (
                PARTITION BY Ticker
                ORDER BY date
                ROWS BETWEEN UNBOUNDED PRECEDING
                AND CURRENT ROW
            ) AS cumulative_return
        FROM daily_returns
    ),

    top5_stocks AS (
        SELECT Ticker
        FROM (
            SELECT
                Ticker,
                MAX(cumulative_return) AS final_return,
                ROW_NUMBER() OVER (
                    ORDER BY MAX(cumulative_return) DESC
                ) AS rank_num
            FROM cumulative_returns
            GROUP BY Ticker
        )
        WHERE rank_num <= 5
    )

    SELECT
        c.date,
        c.Ticker,
        ROUND(c.cumulative_return,2) AS cumulative_return
    FROM cumulative_returns c
    JOIN top5_stocks t
        ON c.Ticker = t.Ticker
    ORDER BY c.date;
    """

    df = get_data(query)

    st.subheader("Top 5 Performing Stocks")
    st.dataframe(df, use_container_width=True)

    df['date'] = pd.to_datetime(df['date'])

    fig, ax = plt.subplots(figsize=(12,6))

    for ticker in df['Ticker'].unique():

        stock = df[df['Ticker'] == ticker]

        ax.plot(
            stock['date'],
            stock['cumulative_return'],
            marker='*',
            label=ticker
        )

    ax.set_title(
        "Cumulative Return of Top 5 Performing Stocks"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return (%)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

# --------------------------------------------------
# 3. Sector Performance
# --------------------------------------------------
elif question == "Sector-wise Performance":

    st.header("3️⃣ Sector-wise Performance")

    query = """
    WITH stock_returns AS (
        SELECT
            Ticker,
            sector,
            (
                (MAX(close)-MIN(close))
                / MIN(close)
            )*100 AS yearly_return
        FROM stock_data
        GROUP BY Ticker, sector
    )

    SELECT
        sector,
        ROUND(
            AVG(yearly_return),2
        ) AS avg_yearly_return
    FROM stock_returns
    GROUP BY sector
    ORDER BY avg_yearly_return DESC;
    """

    df = get_data(query)

    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(15,6))

    ax.bar(
        df["sector"],
        df["avg_yearly_return"]
    )

    ax.set_title("Sector Performance")
    plt.xticks(rotation=45)

    st.pyplot(fig)

# --------------------------------------------------
# 4. Correlation
# --------------------------------------------------
elif question == "Stock Price Correlation":

    st.header("4️⃣ Stock Price Correlation")

    query = """
    SELECT
        date,
        Ticker,
        close
    FROM stock_data;
    """

    df = get_data(query)

    df = (
        df.groupby(
            ['date','Ticker']
        )['close']
        .mean()
        .reset_index()
    )

    pivot_df = df.pivot(
        index='date',
        columns='Ticker',
        values='close'
    )

    corr_matrix = pivot_df.corr()

    fig, ax = plt.subplots(figsize=(20,20))

    sns.heatmap(
    corr_matrix,
    annot=True,
    cmap='coolwarm',
    fmt='.1f',
    linewidths=0.5
    )

    ax.set_title("Correlation Matrix")

    st.pyplot(fig)

# --------------------------------------------------
# 5. Gainers & Losers
# --------------------------------------------------
elif question == "Top 5 Gainers and Losers":

    st.header("5️⃣ Top 5 Gainers and Losers by Month")

    query = """
    WITH monthly_returns AS (
        SELECT
            Ticker,
            month,
            ((MAX(close)-MIN(close))
            /MIN(close))*100
            AS monthly_return
        FROM stock_data
        GROUP BY Ticker, month
    ),

    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER(
                PARTITION BY month
                ORDER BY monthly_return DESC
            ) gain_rank,

            ROW_NUMBER() OVER(
                PARTITION BY month
                ORDER BY monthly_return ASC
            ) loss_rank
        FROM monthly_returns
    )

    SELECT month,Ticker,
           ROUND(monthly_return,2)
           AS monthly_return,
           'Top Gainer' AS category
    FROM ranked
    WHERE gain_rank<=5

    UNION ALL

    SELECT month,Ticker,
           ROUND(monthly_return,2),
           'Top Loser'
    FROM ranked
    WHERE loss_rank<=5;
    """

    df = get_data(query)

    st.dataframe(df)

    months = sorted(df['month'].unique())

    for month in months:

        st.subheader(f"Month {month}")

        month_df = df[df['month'] == month]

        fig, ax = plt.subplots(figsize=(8,5))

        colors = month_df['category'].map({
            'Top Gainer':'green',
            'Top Loser':'red'
        })

        ax.barh(
            month_df['Ticker'],
            month_df['monthly_return'],
            color=colors
        )

        ax.axvline(
            0,
            color='black',
            linestyle='--'
        )

        st.pyplot(fig)
# ---------------------------------
# FOOTER
# ---------------------------------
st.sidebar.markdown("---")
st.sidebar.write("Created by Dhanush DB")        