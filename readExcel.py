import pandas as pd
import psycopg2
import os


DBNAME=os.environ["DBNAME"]
DBPWD=os.environ["DBPWD"]
DBUSER=os.environ["DBUSER"]
DBPORT=os.environ["DBPORT"]
DBHOST=os.environ["DBHOST"]

# foe xlsx files, need to install openpyxl

# Read the Excel file into a DataFrame, skipping the first two rows
df = pd.read_excel('data/shortReport.xlsx', header=None, skiprows=3, usecols="A,C, D, E,F,G,M,O")

df.shape[0]

if df.iloc[1].isnull().all():
    df = df.drop(1)
    

# Rename the columns based on the third row
df.columns = df.iloc[0]

# Drop the first row since it's now redundant
df = df.drop(0)
print(df.columns)

# Rename the column with leading/trailing whitespaces
df.columns = ['SrNo','Old License No','New License No', 
              'Corespondance Address','Premises Address', 
              'Capacity with Product','Grant Date','Expiry Date']

df.columns
df.head(3)

import re
# pick the pin, state, city from the 'Premises address and store them in 
# 3 new columns - pin, state, city respectively

df.drop(columns=['Old License No','Corespondance Address'],inplace=True,axis=1)
split_address = df['Premises Address'].str.split(',')
city = split_address.str[-3].str.strip()
state = split_address.str[-2].str.strip()
pin = split_address.str[-1].str.extract(r'Pin\s*:\s*(\d+)')
df['City'] = city
df['State'] = state
df['Pin'] = pin
print(df.columns)

first_row = df.iloc[0]

# Create lists to store product and capacity values
df_final = pd.DataFrame()
for index, row in df.iterrows():
    if len(row['Capacity with Product'].split(',')) > 1:
        products = []
        capacities = []
        for item in row['Capacity with Product'].split(','):
            product, capacity = item.strip().split('(')
            products.append(product.strip())
            capacities.append(int(capacity.replace(')', '').strip()))
        for product, capacity in zip(products, capacities):
            new_row = row.copy()
            new_row['Product'] = product
            new_row['Capacity'] = capacity
            df_final = pd.concat([df_final, new_row.to_frame().T], ignore_index=True)
    else:
        product, capacity = row['Capacity with Product'].strip().split('(')
        new_row = row.copy()
        new_row['Product'] = product.strip()
        new_row['Capacity'] = int(capacity.replace(')', '').strip())
        df_final = pd.concat([df_final, new_row.to_frame().T], ignore_index=True)

# Display the DataFrame
print(df_final)

df_final.head(5)
df.head(10)
df =df_final.drop('Capacity with Product', axis=1)
df.to_csv('data/output.csv')

df.columns
# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DBNAME,
    user=DBUSER,
    password=DBPWD,
    host=DBHOST,
    port=DBPORT
)

# Create a cursor
cur = conn.cursor()

# Iterate over each row in the DataFrame and insert into the database
for index, row in df.iterrows():
    cur.execute(
        "INSERT INTO inox_customers (new_licence_no, premises_address, grant_date, expiry_date, city, state, pin, product_name, capacity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (row['New License No'], row['Premises Address'], row['Grant Date'], row['Expiry Date'], row['City'], row['State'], row['Pin'], row['Product'], row['Capacity'])
    )

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()
