import pandas as pd
from sqlalchemy import create_engine
import os

DBNAME=os.environ["DBNAME"]
DBPWD=os.environ["DBPWD"]
DBUSER=os.environ["DBUSER"]
DBPORT=os.environ["DBPORT"]
DBHOST=os.environ["DBHOST"]

# Connect to your PostgreSQL database
engine = create_engine(f'postgresql://{DBUSER}:{DBPWD}@{DBHOST}:{DBPORT}/{DBNAME}')

# Read the CSV file into a DataFrame
df = pd.read_csv('data/IN.csv').drop(columns=['accuracy'])

# Insert records into the PostgreSQL table
df.to_sql('pin_lat_long_places', engine, if_exists='append', index=False)
