import requests
from bs4 import BeautifulSoup
import csv

# URL of the page you want to scrape
url = 'https://gamersguildaz.com/collections/board-games?page=87'

# Make a request to the page
response = requests.get(url)
# List to save the data of each game
games_data = []

# Base URL without the page number
base_url = 'https://gamersguildaz.com/collections/board-games?page='

# List to save the data of all the games
all_games_data = []

# Iterate over each page from 1 to 87
for page in range(1, 88):
    print('Scrapping page ' + str(page))
    # Build the URL for the current page
    url = f'{base_url}{page}'
    
    # Make a request to the page
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the ul element that contains the games
        games_list = soup.find('ul', {'data-section-id': 'template--20135255867597__main-collection'})
        # Check if the list of games was found
        if games_list:
            # Find all li elements within the ul with the specified class
            games = games_list.find_all('li')
            # Iterate over each game to get the prices
            for game in games:
                # Find the element with the price inside <div class="static">
                price_info = game.find('div', class_='static').find('p', class_='price')
                product_link_element = game.select_one('div:nth-child(2) > h3 > a')
                # Try to find the element indicating stock and that the product is out of stock
                stock_info_out_of_stock = game.find('p', class_='stock overlay-error list-hide')
                # Try to find the element indicating stock and that the product is in stock
                stock_info_in_stock = game.find('p', class_='stock overlay-valid list-hide')
                
                # Determine the stock status based on the presence of the above elements
                if stock_info_out_of_stock and "Out of stock" in stock_info_out_of_stock.text:
                    in_stock = 'No'
                elif stock_info_in_stock:
                    in_stock = 'Yes'
                else:
                    in_stock = 'Unknown'  # In case none of the two are found

                if price_info and product_link_element:
                    old_price_element = price_info.find('span', class_='old-price')
                    old_price = old_price_element.text.strip() if old_price_element else None
                    current_price = price_info.text.strip()
                    if old_price_element:
                        current_price = current_price.replace(old_price_element.text, '').strip()
                    
                    # Extract the URL and the product name
                    product_url = product_link_element['href']
                    product_name = product_link_element.text.strip()
                    
                    # Save the data in a dictionary
                    game_data = {
                        'product': product_name,
                        'url': 'https://gamersguildaz.com' + product_url,
                        'old_price': old_price,
                        'current_price': current_price,
                        'stock': in_stock
                    }
                    
                    # Add the dictionary to the list of games
                    games_data.append(game_data)
                    all_games_data.append(game_data)
        else:
            print(f'Error accessing the page: Status code {response.status_code}')
    else:
        print(f'Error accessing the page: Status code {response.status_code}')

# Name of the CSV file where the data will be saved
filename = 'gamersguild_games.csv'

# Create and write to the CSV file
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['product', 'old_price', 'current_price', 'url', 'stock'])
    writer.writeheader()
    for game in all_games_data:
        writer.writerow(game)

print(f'Data successfully saved in {filename}')
