import os
import psycopg2
from flask import Flask
from collective.models import Database

app = Flask(__name__)
app.config['DATABASE_URL'] = 'postgresql://pacollective:mynameispa@localhost/collective'

def init_db():
    with app.app_context():
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        cursor = conn.cursor()
        with open(os.path.join(os.path.dirname(__file__), 'collective', 'schema.sql'), 'r') as schema_file:
            schema_sql = schema_file.read()
        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized.")

if __name__ == "__main__":
    init_db()