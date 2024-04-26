import pandas as pd
import psycopg2
import os
#from getLatLong import get_lat_long
import re
from datetime import datetime
import math
import numpy as np

DBNAME=os.environ["DBNAME"]
DBPWD=os.environ["DBPWD"]
DBUSER=os.environ["DBUSER"]
DBPORT=os.environ["DBPORT"]
DBHOST=os.environ["DBHOST"]

# foe xlsx files, need to install openpyxl

# Read the Excel file into a DataFrame, skipping the first two rows
df = pd.read_csv('data/IN.csv')

df.shape[0] # get number of records

if df.iloc[1].isnull().all():
    df = df.drop(1)
    

# Rename the columns based on the third row
df.columns = df.iloc[0]

# Drop the first row since it's now redundant
df = df.drop(0)
print(df.columns)

# Rename the column with leading/trailing whitespaces
df.columns = ['pin','place','state', 
              'latitude','longitude', 
              'accuracy']

df.columns
df.head(3)


# pick the pin, state, city from the 'Premises address and store them in 
# 3 new columns - pin, state, city respectively

df['pin'] = df['pin'].str.split('/').str[1]
df['accuracy'] = df['accuracy'].fillna(0)


first_row = df.iloc[0]

# Create lists to store product and capacity values

df.to_csv('data/output_latlong.csv')

# df.columns
# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DBNAME,
    user=DBUSER,
    password=DBPWD,
    host=DBHOST,
    port=DBPORT
)

#Create a cursor
cur = conn.cursor()

# Iterate over each row in the DataFrame and insert into the database
for index, row in df.iterrows():
    cur.execute(
        "INSERT INTO lat_long (pin, place,state, latitude, longitude, accuracy) VALUES (%s, %s,%s, %s, %s, %s)",
        (row['pin'], row['place'], row['state'], row['latitude'], row['longitude'], row['accuracy'])
    )

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()

