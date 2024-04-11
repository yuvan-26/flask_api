#!/usr/bin/env python
# coding: utf-8

# ## GRAPH

# In[ ]:


get_ipython().system('jupyter nbextension enable --py widgetsnbextension')
from ipywidgets import interact, SelectMultiple


import logging
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import plotly.express as px
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection parameterss
config = {
    'user': 'dbmasteruser',
    'password': '$Cedl!I[+B2#s-G+cRRR<(iLUHw^r+M}',
    'host': 'ls-b22c7f51d64ab84dab595cb78afe070f9cec2aa9.ctyoosgii0nz.ap-southeast-2.rds.amazonaws.com',
    'database': 'bulblos',
    'port': 3306
}

mydb = mysql.connector.connect(**config)

# SQL query to fetch the data
sql_query = "SELECT Temperature, PH, Soil, Waterlevel, Space, Label FROM garden"

# Load data from MySQL into a pandas DataFrame
df = pd.read_sql(sql_query, mydb)

# Close database connection
mydb.close()

# Separate the numeric and categorical columns
numeric_cols = df.select_dtypes(include=['number']).columns
categorical_cols = df.select_dtypes(exclude=['number']).columns

# Define a custom aggregation dictionary
aggregations = {**{nc: 'mean' for nc in numeric_cols}, **{cc: lambda x: pd.Series.mode(x)[0] for cc in categorical_cols}}

# Group by the 'Label' without setting it as an index and apply the aggregation
grouped_df = df.groupby('Label', as_index=False).agg(aggregations)
df = grouped_df


df['Space Category'] = pd.qcut(df['Space'], 5, labels=[
    'Very Low Space',
    'Low Space',
    'Medium Space',
    'High Space',
    'Very High Space'
])

def update_plot(temperature_min_value, temperature_max_value):
    filtered_df = df[
        (df['Temperature'] >= temperature_min_value) & (df['Temperature'] <= temperature_max_value)
    ]
    
    filtered_df = filtered_df.sort_values(["Waterlevel", "Space Category"])
    
    fig = px.scatter(
        filtered_df, 
        labels={
            "x": "Space Category",
            "y": "Waterlevel",
            'Label': 'Label'
        },
        x='Space Category',
        y='Waterlevel',
        color='Soil', 
        size='PH', 
        hover_data=['Label', 'Space Category'],
        category_orders={
            "Waterlevel": ["Low", "Moderate", "High"], 
            "Space Category": ['Very Low Space', 'Low Space', 'Medium Space', 'High Space', 'Very High Space']
        },
        opacity=0.7,
        text='Label'
    )
    
    fig.update_yaxes(range=[-1, 3])
    fig.update_xaxes(range=[-0.5, 5])
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_layout(
        legend_title_side="top",
        transition_duration=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_layout(width=1300, height=600)
    fig.update_traces(textposition='top center', textfont=dict(size=10))
    
    # Convert Plotly figure to JSON
    fig_json = fig.to_json()
    
    return json.loads(fig_json)

@app.route('/plot', methods=['GET'])
def plot_chart():
    try:
        # Connect to MySQL database
        mydb = mysql.connector.connect(**config)

        # SQL query to fetch the data
        sql_query = "SELECT Temperature, PH, Soil, Waterlevel, Space, Label FROM garden"

        # Load data from MySQL into a pandas DataFrame
        df = pd.read_sql(sql_query, mydb)

        # Close database connection
        mydb.close()

        # Log test message
        logger.info('Data fetched successfully from the database.')
        
        # Call update_plot function with sample temperature values
        temperature_min_value = 0  # Set your desired minimum temperature value
        temperature_max_value = 30  # Set your desired maximum temperature value
        plot_data = update_plot(temperature_min_value, temperature_max_value)
        
        return jsonify(plot_data)

    except Exception as e:
        logger.error('An error occurred: %s', str(e))
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

