import snowflake.snowpark as snowpark
from snowflake.snowpark.functions import month,year,col,to_char,sum
import streamlit as st
import plotly.express as px
import pandas as pd
from snowflake.snowpark.context import get_active_session
session = get_active_session()

st.title("Sales Analysis")
st.write(f"Welcome, {st.user.user_name}!")

df_sales = session.table('snowflake_learning_db.sales_analysis.sales_data')
df_sales = df_sales.with_column('YEAR-MONTH', to_char(col("date"), "YYYY-MM"))
# df_sales.schema

df_sales_per_product = (
    df_sales.group_by('product')
                .agg(sum('sales').as_('total_sales'))
                .sort('total_sales', ascending=False)
)
# df_sales_per_product

fig = px.bar(
    df_sales_per_product,
    x="PRODUCT",
    y="TOTAL_SALES",
    title="Product Sales Leaderboard",
)
st.plotly_chart(fig, use_container_width=True)

df_monthly_sales = (
    df_sales.group_by('YEAR-MONTH')
            .agg(sum('sales').as_('total_sales'))
            .sort('YEAR-MONTH')
)
# df_monthly_sales

fig = px.line(
    df_monthly_sales,
    x='YEAR-MONTH',
    y='TOTAL_SALES',
    title='MONTHLY TREND ANALYSIS',
    markers=True
)
fig.update_xaxes(type="category")   # force categorical axis

st.plotly_chart(fig, use_container_width=True)

df_monthly_sales_per_region = (
    df_sales.group_by('YEAR-MONTH', 'REGION')
            .agg(sum('sales').as_('total_sales'))
            .sort('YEAR-MONTH')
)

df_monthly_sales_per_region_pd = df_monthly_sales_per_region.to_pandas()
selected_regions = st.multiselect(
    "Filter by region",
    options=df_monthly_sales_per_region_pd["REGION"].unique(),
    default=df_monthly_sales_per_region_pd["REGION"].unique(),
)

filtered = df_monthly_sales_per_region_pd[df_monthly_sales_per_region_pd["REGION"].isin(selected_regions)]

total = filtered["TOTAL_SALES"].sum()
st.metric("Total Revenue", f"${total:,.0f}")

fig = px.bar(
    filtered,
    x="YEAR-MONTH",
    y="TOTAL_SALES",
    color="REGION",
    barmode="group",
    title="Monthly Revenue by Region"
)
fig.update_xaxes(type="category")   # force categorical axis
st.plotly_chart(fig, use_container_width=True)