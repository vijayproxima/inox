import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import Error
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

# Function to update database with data from Excel file
def update_database(file_path):


    # foe xlsx files, need to install openpyxl
    df = pd.read_excel(file_path, header=None, skiprows=3, usecols="A,C, D, E,F,G,M")

    df.shape[0] # get number of records

    if df.iloc[1].isnull().all():
        df = df.drop(1)
        

    # Rename the columns based on the third row
    df.columns = df.iloc[0]

    # Drop the first row since it's now redundant
    df = df.drop(0)
    #print(df.columns)

    # Rename the column with leading/trailing whitespaces
    df.columns = ['SrNo','Old License No','Approval No', 
                'Corespondance Address','Premises Address', 
                'Capacity with Product','Approval Date']

    #df.columns
    #df.head(3)


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

    #print(df.columns)

    #first_row = df.iloc[0]

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
    #print(df_final)
    #rows_with_blank_date = df[df['Approval Date'].isna()]
    df_final.dropna(subset=['Approval Date'], inplace=True)

    #df_final.head(5)
    #df_final.shape[0]
    #df.head(2)
    df =df_final.drop('Capacity with Product', axis=1)
    df.to_csv('data/output_approvals.csv')
    #df.shape[0]
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
    cur.execute("SELECT COUNT(*) from inox_customers_approvals")
    initial_count = cur.fetchone()[0]
    # Iterate over each row in the DataFrame and insert into the database
    for index, row in df.iterrows():

        address = re.sub(r'\s+', ' ', row['Premises Address']).strip()
        # Update the address in the DataFrame
        df.at[index, 'Premises Address'] = address
        
        if initial_count == 0:
            cur.execute(
            "INSERT INTO inox_customers_approvals (approval_no, premises_address,customer_name, approval_date, city, state, pin, product_name, capacity) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s)",
            (row['Approval No'], row['Premises Address'], row['Customer_name'], row['Approval Date'], row['City'], row['State'], row['Pin'], row['Product'], row['Capacity'])
        )
            
        else:
            cur.execute(
                """
                INSERT INTO inox_customers_approvals (approval_no, premises_address, customer_name, approval_date, city, state, pin, product_name, capacity) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (approval_no, product_name) DO NOTHING
                """,
                (row['Approval No'], row['Premises Address'], row['Customer_name'], row['Approval Date'], row['City'], row['State'], row['Pin'], row['Product'], row['Capacity'])
            )

        # Commit the changes and close the connection
    cur.execute("SELECT COUNT(*) from inox_customers_approvals")
    final_count = cur.fetchone()[0]
    num_new_records = final_count - initial_count
    st.write(f"Number of new records added: {num_new_records}")
    
    conn.commit()
    cur.close()
    conn.close()
    #st.write("data inserted successfully")
        

# Function to fetch first 10 records from the database
def fetch_records():
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=DBUSER,
        password=DBPWD,
        host=DBHOST,
        port=DBPORT
    )
    cur = conn.cursor()
    cur.execute("SELECT approval_no, customer_name, approval_date, city, state, pin, product_name, capacity FROM inox_customers_approvals LIMIT 5")
    records = cur.fetchall()
    #st.write("records retrieved")
    columns = [desc[0] for desc in cur.description]  # Get column names
    df_temp = pd.DataFrame(records, columns=columns)  # Convert to DataFrame
    cur.close()
    conn.close()
    return df_temp.reset_index() # Reset index to ensure we have access to the record's index


# Function to update a specific customer record
def update_customer(record):
    st.title("Update New Customer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Information")
        customer_name = st.text_input("Customer Name", max_chars=250, value=record['customer_name'])
        approval_no = st.text_input("Approval No", max_chars=50, value=record['approval_no'])
        rtkm = st.number_input("Round Trip KM", step=1.0)
        inox_ap_concern_region = st.selectbox("Inox AP Concern Region", ["East", "North", "MP", "Gujarat"])
        known_to_inoxap = st.selectbox("Known to InoxAP", ["Yes", "No"])
    
    with col2:
        #st.subheader("Additional Information")
        potential_supplier = st.text_area("Potential Supplier", max_chars=250)
        industry_segment = st.selectbox("Industry Segment", ["Iron Steel Making", "Rolling Mills", "Automobile", "Glass"])
        type_of_customer = st.selectbox("Type of Customer", ["Gas Manufacturing Company", "Onsite Customer", "Bulk Liquid Consumer"])
        project_type = st.selectbox("Project Type", ["Green Field", "Brown Field"])
        estimated_volume = st.number_input("Estimated Volume (In Sm3/Month)", step=1.0)
        site_condition = st.selectbox("Site Condition", ["VIST Foundation Ready", "VIST Foundation Not Ready", "VIST Already Installed"])
        site_photo = st.file_uploader("Site Photographs (Upload image [size < 1 MB])", type=["jpg", "jpeg", "png"])
    
    reason_for_loss = st.text_area("Reason for Business Loss to InoxAP")
    
    # Remarks with date
    remarks = st.text_area("Remarks")
    if st.button("Add Remark"):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        remarks += f"\n{current_time}: {remarks}"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update", key="update_btn"):
            # Logic to update the customer data
            st.success("Customer Updated Successfully!")
    
    with col2:
        if st.button("Cancel", key="cancel_btn"):
            st.warning("Operation Cancelled")

# Main function to run the Streamlit app
def main():
    st.title("Inox Customers Management App")

    # Page selection
    page = st.sidebar.selectbox("Select Page", ["Upload", "Get Customer Data"])

    if page == "Upload":
        st.header("Upload Excel File")
        file = st.file_uploader("Upload Excel File", type=["xlsx"])
        if file:
            progress_bar = st.progress(0)
            update_database(file)
            progress_bar.progress(100)
            st.success("Database updated successfully!")
            #st.write("data INSERTED")

    elif page == "Get Customer Data":
        st.header("Customer Records")
        records = fetch_records()
        #print(records)
        for index, record in records.iterrows():
            st.write(f"Record {index+1}")
            st.write(record)
            if st.button(f"Update Record {index+1}"):
                update_customer(record)
        #st.table(records)

        # Display update link for each record
        #for index, record in records.iterrows():
   

if __name__ == "__main__":
    main()
