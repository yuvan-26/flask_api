#!/usr/bin/env python
# coding: utf-8

# ## Visualisation

# In[9]:


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

@app.route('/plot', methods=['GET'])
def plot_chart():
    try:
        # Connect to MySQL database
        mydb = mysql.connector.connect(**config)

        # SQL query to fetch data
        sql_query = "SELECT Temperature, PH, Soil, Waterlevel, Space, Label FROM garden"

        # Load data from MySQL into a pandas DataFrame
        df = pd.read_sql(sql_query, mydb)

        # Close database connection
        mydb.close()

        # Log message
        logger.info('Data fetched successfully from the database.')

        # Plot interactive line chart
        fig = px.line(df, x='Label', y='PH', color='Label',
                      title='Distribution of PH of Garden Crops over Labels',
                      labels={'Label': 'Label', 'PH': 'PH Value'})

        # Alternatively, for a bar chart:
        # fig = px.bar(df, x='Label', y='PH', color='Label',
        #              title='Distribution of PH of Garden Crops over Labels',
        #              labels={'Label': 'Label', 'PH': 'PH Value'})

        # Increase figure size
        fig.update_layout(width=1000, height=1000)

        return jsonify(fig.to_json())

    except Exception as e:
        logger.error('An error occurred: %s', str(e))
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

