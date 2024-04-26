import pandas as pd

# Load the dataset containing city/state to pincode mappings
data = pd.read_csv('indian_pincode_dataset.csv')  # Replace with your dataset

def get_pincode(city, state):
    try:
        pincode = data[(data['City'] == city) & (data['State'] == state)]['Pincode'].iloc[0]
        return pincode
    except IndexError:
        return None  # Return None if city/state combination not found

# Example usage:
city = 'Mumbai'
state = 'Maharashtra'
pincode = get_pincode(city, state)
if pincode:
    print(f"The pincode of {city}, {state} is {pincode}")
else:
    print(f"Pincode not found for {city}, {state}")
