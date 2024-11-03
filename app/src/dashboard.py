import streamlit as st
import get_data 
from datetime import datetime as dt
import altair as alt
import numpy as np
st.set_page_config(page_title="Home Solar Production", layout='wide')
st.title("HOME SOLAR DATA")
st.subheader("Daily updated energy generation from residential solar panel", divider='gray')

# Load and process the data from the database
data, data_hourly = get_data.load_data()

kwh_total, kwh_current, last_update = st.columns(3)

with kwh_total:
    total = sum(data['total'])
    total = f"{total:,.0f}"
    st.metric("**Total kwh**", total)

with kwh_current:
    # Filtrar apenas os registros do mês e ano atuais
    current_month = dt.now().month
    current_year = dt.now().year    
    current_month_data = data[(data['prod_date'].dt.month == current_month) & (data['prod_date'].dt.year == current_year)]
    current_month_kwh = current_month_data['total'].sum()
    current_month_kwh = f"{current_month_kwh:,.00f}"
    st.metric("**Current month kwh**", current_month_kwh)

with last_update:
    max_date = data['prod_date'].max().strftime('%A, %Y-%m-%d ')
    st.metric("**Latest data entry**", max_date)

monthly_barchart, weekly_linechart = st.columns(2)

with monthly_barchart:
    st.subheader("Monthly kwh")
    
    monthly_data = data.resample('ME', on='prod_date').sum(numeric_only=True).reset_index()
    monthly_data['formatted_date'] = monthly_data['prod_date'].dt.strftime('%b/%y')
    
    chart = alt.Chart(monthly_data).mark_bar(color='#e76f51').encode(
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
        dy=-5,
        color='#e76f51',
        fontWeight='bold'
    ).encode(
        text=alt.Text('total:Q', format='.0f') 
    )
    
    chart = chart + text
    chart = chart.configure_axis(grid=False)
    
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
    
with weekly_linechart:
    st.subheader("Weekly kwh")

    weekly_data = data.resample('W', on='prod_date').sum(numeric_only=True).reset_index()

    chart2 = alt.Chart(weekly_data).mark_area(color='#e76f51').encode(
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
    st.subheader("Daily heatmap kwh")
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
    st.subheader("Daylight hourly heatmap kwh")
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

st.write(heatmap_data2)

    #t.write(weekly_data)

    # # Pivot the DataFrame for the heatmap
    # heatmap_data = df.pivot_table(values='total', index=df['prod_date'].dt.strftime('%b'), columns=df['prod_date'].dt.year, fill_value=0)

    # # Reset index for Altair
    # heatmap_data_reset = heatmap_data.reset_index()

    # # Create the heatmap
    # heatmap = alt.Chart(heatmap_data_reset).mark_rect().encode(
    #     x=alt.X('year:O', title='Year'),
    #     y=alt.Y('month:O', title='Month'),
    #     color=alt.Color('total:Q', scale=alt.Scale(scheme='blues'), title='Total Production (kWh)')
    # ).properties(
    #     title='Heatmap of Total Production by Month and Year',
    #     width=800,
    #     height=400
    # )

    # # Add text labels to the heatmap
    # heatmap_text = heatmap.mark_text(baseline='middle', color='white').encode(
    #     text=alt.Text('total:Q', format='.0f')
    # )

    # # Combine heatmap and text
    # return heatmap + heatmap_text

# st.altair_chart(heatmap, use_container_width=False)