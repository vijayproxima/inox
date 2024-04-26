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
df = pd.read_excel('data/Approvals_data_24_APR.xlsx', header=None, skiprows=3, usecols="A,C, D, E,F,G,M")

df.shape[0] # get number of records

if df.iloc[1].isnull().all():
    df = df.drop(1)
    

# Rename the columns based on the third row
df.columns = df.iloc[0]

# Drop the first row since it's now redundant
df = df.drop(0)
print(df.columns)

# Rename the column with leading/trailing whitespaces
df.columns = ['SrNo','Old License No','Approval No', 
              'Corespondance Address','Premises Address', 
              'Capacity with Product','Approval Date']

df.columns
df.head(3)


# pick the pin, state, city from the 'Premises address and store them in 
# 3 new columns - pin, state, city respectively

customer_name = df['Corespondance Address'].str.split('\n')
customer_name = customer_name.str[0].str.strip()
df['Customer_name'] = customer_name

# Define a regex pattern to match the pin
pin_pattern = r'Pin\s*:\s*(\d+)'

# Preprocess the Premises Address column
df['Premises Address'] = df['Premises Address'].str.replace(r'\n', ', ').str.strip()

# Define a function to extract the pin using the regex pattern
def extract_pin(address):
    match = re.search(pin_pattern, address)
    if match:
        return match.group(1)
    else:
        return None

# Extract pin from Premises Address column
df['Pin'] = df['Premises Address'].apply(extract_pin)

# Now split the cleaned Premises Address column into city and state
split_address = df['Premises Address'].str.split(',')
city = split_address.str[-2].str.strip()
state = split_address.str[-3].str.strip()

df['City'] = city
df['State'] = state

#df['latitude'],df['longitude'] = get_lat_long(str(pin))

df.drop(columns=['Old License No','Corespondance Address'],inplace=True,axis=1)

print(df.columns)

first_row = df.iloc[0]

# Create lists to store product and capacity values
df_final = pd.DataFrame()
for index, row in df.iterrows():
    if len(row['Capacity with Product'].split(',')) > 1:
        products = []
        capacities = []
        for item in row['Capacity with Product'].split(','):
            try:
                last_opening_bracket_index = item.rfind('(')
                product = item[:last_opening_bracket_index].strip()
                capacity = int(item[last_opening_bracket_index+1:].replace(')', '').strip())
                products.append(product)
                capacities.append(capacity)
            except ValueError:
                print(f"Error: Unable to unpack item '{item}'")
                continue
        for product, capacity in zip(products, capacities):
            new_row = row.copy()
            new_row['Product'] = product
            new_row['Capacity'] = capacity
            df_final = pd.concat([df_final, new_row.to_frame().T], ignore_index=True)
    else:
        try:
            last_opening_bracket_index = row['Capacity with Product'].rfind('(')
            product = row['Capacity with Product'][:last_opening_bracket_index].strip()
            capacity = int(row['Capacity with Product'][last_opening_bracket_index+1:].replace(')', '').strip())
            new_row = row.copy()
            new_row['Product'] = product
            new_row['Capacity'] = capacity
            df_final = pd.concat([df_final, new_row.to_frame().T], ignore_index=True)
        except ValueError:
            print(f"Error: Unable to unpack item '{row['Capacity with Product']}'")
            continue


# Display the DataFrame
print(df_final)
rows_with_blank_date = df[df['Approval Date'].isna()]
df_final.dropna(subset=['Approval Date'], inplace=True)

df_final.head(5)
df_final.shape[0]
df.head(2)
df =df_final.drop('Capacity with Product', axis=1)
df.to_csv('data/output_approvals.csv')
df.shape[0]
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
    # cur.execute("SELECT COUNT(*) FROM inox_customers_approvals WHERE approval_no = %s", (row['Approval No'],))
    # count = cur.fetchone()[0]
    
    # # If the count is greater than 0, skip inserting the record
    # if count > 0:
    #     continue
    address = re.sub(r'\s+', ' ', row['Premises Address']).strip()
    # Update the address in the DataFrame
    df.at[index, 'Premises Address'] = address
    cur.execute(
        "INSERT INTO inox_customers_approvals (approval_no, premises_address,customer_name, approval_date, city, state, pin, product_name, capacity) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s)",
        (row['Approval No'], row['Premises Address'], row['Customer_name'], row['Approval Date'], row['City'], row['State'], row['Pin'], row['Product'], row['Capacity'])
    )

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()

# for index, row in df.iterrows():
#     cur.execute("SELECT COUNT(*) FROM inox_customers_approvals WHERE approval_no = %s", (row['Approval No'],))
#     count = cur.fetchone()[0]
    
#     # If the count is greater than 0, skip inserting the record
#     if count > 0:
#         continue
#     address = re.sub(r'\s+', ' ', row['Premises Address']).strip()
#        # Convert the date string to a date object if it's not 'nan'
#     #df['Approval Date'] = df['Approval Date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').strftime('%Y-%m-%d') if pd.notnull(x) else np.nan)
#     df['Approval Date'] = df['Approval Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%Y-%m-%d') if pd.notnull(x) else np.nan)

#     # Update the address in the DataFrame
#     df.at[index, 'Premises Address'] = address
#     cur.execute(
#         "INSERT INTO inox_customers_approvals (approval_no, premises_address, approval_date, customer_name, city, state, pin, product_name, capacity) VALUES (%s, %s, COALESCE(NULLIF(NULLIF(%s, '')::date, '1900-01-01'), '1900-01-01'), %s, %s, %s,  NULLIF(%s, ''), %s, NULLIF(%s, ''))",
#         (row['Approval No'], row['Premises Address'],  row['Approval Date'],row['Customer_name'], row['City'], row['State'], row['Pin'], row['Product'], row['Capacity'])
#     )

# # Commit the changes and close the connection
# conn.commit()
# cur.close()
# conn.close()
