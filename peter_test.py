import logging
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

# Create a Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection parameters
config = {
    'user': 'dbmasteruser',
    'password': '$Cedl!I[+B2#s-G+cRRR<(iLUHw^r+M}',
    'host': 'ls-b22c7f51d64ab84dab595cb78afe070f9cec2aa9.ctyoosgii0nz.ap-southeast-2.rds.amazonaws.com',
    'database': 'bulblos',
    'port': 3306
}

@app.route('/plant_data', methods=['GET'])
def get_plant_data():
    try:
        # Connect to MySQL database
        mydb = mysql.connector.connect(**config)

        # SQL query to fetch all data from the plant_data table
        sql_query = "SELECT * FROM plant_data"

        # Load data from MySQL into a pandas DataFrame
        df = pd.read_sql(sql_query, mydb)

        # Close database connection
        mydb.close()

        # Convert DataFrame to JSON format
        plant_data_json = df.to_json(orient='records')

        logger.info('Plant data retrieved successfully')

        return jsonify(plant_data_json)

    except Exception as e:
        logger.error('An error occurred: %s', str(e))
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
