from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Table, MetaData, text
import pandas as pd
import os

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

db_user = 'root'
db_password = 'hoangduc1123'
db_host = 'localhost'
db_name = 'kafi'
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files['file']

    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .csv files are allowed.'}), 400
    filename = os.path.splitext(file.filename)[0]
    df = pd.read_csv(file)
    # Write CSV data to MySQL table
    df.to_sql(filename, con=engine, if_exists='replace', index=False)
    # Query the inserted data
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM `{filename}`")).fetchall()
        rows = [dict(row._mapping) for row in result]
        columns = list(rows[0].keys()) if rows else []
    return jsonify({'columns': list(columns), 'rows': rows, 'filename': filename})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)