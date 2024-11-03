import streamlit as st
import get_data 
from datetime import datetime as dt
import altair as alt
import numpy as np
import pandas as pd 
import os
import sys 
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"../")

# HEADERS
st.set_page_config(page_title="Home Solar Production", layout='wide')
st.title("HOME SOLAR DATA")
st.subheader("Daily updated energy generation from residential solar panel", divider='gray')

# GETTING THE DATA
data, data_hourly = get_data.load_data()

# BIG NUMBERS
kWh_total, kWh_current, last_update = st.columns([1,4,1])

with kWh_total:
    total = sum(data['total'])
    total = f"{total:,.0f}"
    st.metric("**Total kWh**", total)

with kWh_current:
    current_month = dt.now().month
    current_year = dt.now().year    
    current_month_data = data[(data['prod_date'].dt.month == current_month) & (data['prod_date'].dt.year == current_year)]
    current_month_kWh = current_month_data['total'].sum()
    current_month_kWh = f"{current_month_kWh:,.00f}"
    st.metric("**Current month kWh**", current_month_kWh)

with last_update:
    max_date = data['prod_date'].max().strftime('%A, %Y-%m-%d ')
    st.metric("**Latest data entry**", max_date)

# CHARTS

monthly_barchart, weekly_linechart = st.columns(2)

with monthly_barchart:
    st.subheader("Monthly kWh")
    
    monthly_data = data.resample('ME', on='prod_date').sum(numeric_only=True).reset_index()
    monthly_data['formatted_date'] = monthly_data['prod_date'].dt.strftime('%b/%y')
    
    chart = alt.Chart(monthly_data).mark_bar(color='#FF4C00').encode(
        x=alt.X('formatted_date:N',
                sort=alt.SortField(field='date', order='ascending'),
                title='',
                axis=alt.Axis(labelAngle=-90)),
        y=alt.Y('total:Q', title=None, axis=None)
    ).properties(
        title="",
        width=800,
        height=400
    )
    text = chart.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        color='#e76f51',
        fontWeight='bold',
        fontSize=15
    ).encode(
        text=alt.Text('total:Q', format='.0f') 
    )
    
    chart = chart + text
    chart = chart.configure_axis(grid=False)

    st.altair_chart(chart, use_container_width=True)

with weekly_linechart:
    st.subheader("Weekly kWh")

    weekly_data = data.resample('W', on='prod_date').sum(numeric_only=True).reset_index()

    chart2 = alt.Chart(weekly_data).mark_area(color='#FF4C00').encode(
        x=alt.X('prod_date:T',
                sort=alt.SortField(field='date', order='ascending'),
                title='',
                axis=alt.Axis(labelAngle=-90, format='%b/%Y')),
        y=alt.Y('total:Q', title=None)
    ).properties(
        title="",
        width=800,
        height=400
    )
    
    chart2 = chart2.configure_axis(grid=False)
    st.altair_chart(chart2, use_container_width=True)

st.divider()

daily_heatmap, hourly_heatmap = st.columns(2)


with daily_heatmap:
    st.subheader("Daily heatmap kWh")
    data['day'] = data['prod_date'].dt.day
    data['month_year'] = data['prod_date'].dt.strftime('%b/%Y') 
    data['month_year_sort'] = data['prod_date'].dt.to_period('M').dt.to_timestamp()
    
    heatmap_data = data.groupby(['day', 'month_year', 'month_year_sort'], as_index=False).agg({'total': 'sum'})
    
    chart3 = alt.Chart(heatmap_data).mark_rect().encode(
        alt.X("month_year:O",
            sort=alt.SortField(field='month_year_sort', order='ascending')
            ).axis(labelAngle=-90, title=None),
        alt.Y("day:O", title=None),
        alt.Color("sum(total):Q", scale=alt.Scale(scheme='blueorange'),title=''),
    ).properties(
        title="",
        width=800,
        height=600
    )
    st.altair_chart(chart3, use_container_width=True)

with hourly_heatmap:
    st.subheader("Daylight hourly heatmap kWh")
    data_hourly['hour'] = data_hourly['prod_datehour'].dt.hour
    data_hourly['month_year'] = data_hourly['prod_datehour'].dt.strftime('%b/%Y') 
    data_hourly['month_year_sort'] = data_hourly['prod_datehour'].dt.to_period('M').dt.to_timestamp()

    heatmap_data2 = data_hourly.groupby(['hour', 'month_year', 'month_year_sort'], as_index=False).agg({'energy_value': 'mean'})
    heatmap_data2 = heatmap_data2.replace(0, np.nan)
    
    chart4 = alt.Chart(heatmap_data2).mark_rect().encode(
        alt.X("month_year:O",
            sort=alt.SortField(field='month_year_sort', order='ascending')
            ).axis(labelAngle=-90, title=None),
        alt.Y("hour:O", title=None),
        alt.Color("mean(energy_value):Q", scale=alt.Scale(scheme='blueorange'),title=''),
    ).properties(
        title="",
        width=800,
        height=600
    )
    st.altair_chart(chart4, use_container_width=True)

st.divider()

summer, autumn, winter, spring = st.columns(4)

seasons = {
    "season": [
        "Winter","Spring", "Summer", "Autumn", "Winter",
        "Spring", "Summer", "Autumn", "Winter",
        "Spring", "Summer", "Autumn", "Winter",
        "Spring", "Summer"
    ],
    "date": [
        "2021-06-21","2021-09-22", "2021-12-21", "2022-03-20", "2022-06-21",
        "2022-09-23", "2022-12-21", "2023-03-20", "2023-06-21",
        "2023-09-23", "2023-12-21", "2024-03-20", "2024-06-21",
        "2024-09-22", "2024-12-21"
    ]
}
df_estacoes = pd.DataFrame(seasons)
df_estacoes['date'] = pd.to_datetime(df_estacoes['date'])

df_estacoes = df_estacoes.sort_values(by='date').reset_index(drop=True)
data = data.sort_values(by='prod_date').reset_index(drop=True)

df_resultado = pd.merge_asof(
    data, 
    df_estacoes, 
    left_on='prod_date', 
    right_on='date', 
    direction='backward'
)
summer, autumn, winter, spring = st.columns(4)

with summer:
    st.subheader("Summer")
    
    filter_summer = ['Summer']
    data_summer = df_resultado[df_resultado['season'].isin(filter_summer)]
    data_summer['month'] = data_summer['prod_date'].dt.month_name()
    data_summer = (
        data_summer
        .groupby('month')
        .agg(total=('total', 'mean'))  # Calcula a média da geração diária de kWh
        .reset_index()
    )

    month_order = ['December', 'January', 'February', 'March']

    # Create the Altair bar chart
    chart5 = alt.Chart(data_summer).mark_bar(color='#99582A').encode(
        x=alt.X('month:O',  # Change to ordinal for discrete months
                sort=month_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=15)),
        y=alt.Y('total:Q', title=None, axis=None)  # Display the average kWh
    ).properties(
        title="Average daily kWh",
        width=800,
        height=400
    )
    
    # Add text labels to show exact values
    text = chart5.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        color='#99582A',
        fontWeight='bold',
        fontSize=15
    ).encode(
        text=alt.Text('total:Q', format='.1f')
    )
    
    # Combine the bar chart with text labels
    chart5 = chart5 + text
    chart5 = chart5.configure_axis(grid=False)
    
    # Display the chart in Streamlit
    st.altair_chart(chart5, use_container_width=True)

with autumn:
    st.subheader("Autumn")
    
    filter_summer = ['Autumn']
    data_summer = df_resultado[df_resultado['season'].isin(filter_summer)]
    data_summer['month'] = data_summer['prod_date'].dt.month_name()
    data_summer = (
        data_summer
        .groupby('month')
        .agg(total=('total', 'mean')) 
        .reset_index()
    )

    month_order = ['March', 'April', 'May', 'June']

    # Create the Altair bar chart
    chart6 = alt.Chart(data_summer).mark_bar(color='#F5BC00').encode(
        x=alt.X('month:O', 
                sort=month_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=15)),
        y=alt.Y('total:Q', title=None, axis=None) 
    ).properties(
        title="Average daily kWh",
        width=800,
        height=400
    )
    
    text = chart6.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        color='#F5BC00',
        fontWeight='bold',
        fontSize=15
    ).encode(
        text=alt.Text('total:Q', format='.1f')
    )
    
    chart6 = chart6 + text
    chart6 = chart6.configure_axis(grid=False)

    st.altair_chart(chart6, use_container_width=True)

with winter:
    st.subheader("Winter")
    
    filter_summer = ['Winter']
    data_summer = df_resultado[df_resultado['season'].isin(filter_summer)]
    data_summer['month'] = data_summer['prod_date'].dt.month_name()
    data_summer = (
        data_summer
        .groupby('month')
        .agg(total=('total', 'mean')) 
        .reset_index()
    )

    month_order = ['June', 'July', 'August', 'September']

    chart7 = alt.Chart(data_summer).mark_bar(color='#219ebc').encode(
        x=alt.X('month:O',  
                sort=month_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=15)),
        y=alt.Y('total:Q', title=None, axis=None)  
    ).properties(
        title="Average daily kWh",
        width=800,
        height=400
    )
    
    text = chart7.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        color='#219ebc',
        fontWeight='bold',
        fontSize=15
    ).encode(
        text=alt.Text('total:Q', format='.1f')
    )
    
    chart7 = chart7 + text
    chart7 = chart7.configure_axis(grid=False)
    
    st.altair_chart(chart7, use_container_width=True)

with spring:
    st.subheader("Spring")
    
    filter_summer = ['Spring']
    data_summer = df_resultado[df_resultado['season'].isin(filter_summer)]
    data_summer['month'] = data_summer['prod_date'].dt.month_name()
    data_summer = (
        data_summer
        .groupby('month')
        .agg(total=('total', 'mean'))
        .reset_index()
    )

    month_order = ['September', 'October', 'November', 'September']

    chart8 = alt.Chart(data_summer).mark_bar(color='#588157').encode(
        x=alt.X('month:O', 
                sort=month_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=15)),
        y=alt.Y('total:Q', title=None, axis=None) 
    ).properties(
        title="Average daily kWh",
        width=800,
        height=400
    )
    
    text = chart8.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        color='#588157',
        fontWeight='bold',
        fontSize=15
    ).encode(
        text=alt.Text('total:Q', format='.1f')
    )
    
    chart8 = chart8 + text
    chart8 = chart8.configure_axis(grid=False)

    st.altair_chart(chart8, use_container_width=True)