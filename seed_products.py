import sqlite3
import os
import config

def insert_products():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        cursor = conn.cursor()
        
        products = [
            ('Digital Air Fryer', 'Premium 5L Air Fryer with touch screen and 8 presets.', 'Kitchen', 4999, 'air_fryer.jpg'),
            ('Espresso Coffee Maker', 'Automatic coffee machine with milk frother.', 'Kitchen', 8999, 'coffee_maker.jpg'),
            ('Performance Running Shoes', 'Lightweight and breathable shoes for athletes.', 'Footwear', 2499, 'shoes.jpg'),
            ('Classic Leather Boots', 'High-quality brown leather boots for casual wear.', 'Footwear', 3499, 'boots.jpg')
        ]
        
        query = "INSERT INTO products (name, description, category, price, image) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(query, products)
        
        conn.commit()
        print(f"Successfully inserted {cursor.rowcount} products.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    insert_products()
