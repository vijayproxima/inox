import requests
from bs4 import BeautifulSoup

# URL of the website containing the tabular data
url = 'https://online.peso.gov.in/PublicDomain/SearchOption.aspx'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(response.text)
    # Find the table containing the data
    table = soup.find('table')

    if table:
        # Initialize a list to store the data
        data = []

        # Iterate over rows in the table
        for row in table.find_all('tr'):
            # Initialize a list to store data for each row
            row_data = []

            # Iterate over cells in the row
            for cell in row.find_all(['th', 'td']):
                # Append the text content of the cell to the row data list
                row_data.append(cell.get_text(strip=True))

            # Append the row data to the main data list
            data.append(row_data)

        # Print the scraped data
        for row in data:
            print(row)
    else:
        print('Table not found on the webpage.')
else:
    print('Failed to retrieve webpage. Status code:', response.status_code)
