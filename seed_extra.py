import sqlite3
import os
import config

def seed_more_products():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        cursor = conn.cursor()
        
        products = [
            ('Remote Control Car', 'High-speed RC car with rechargeable batteries.', 'Toys', 1499, 'toy_car.jpg'),
            ('Building Blocks Set', '500-piece creative building blocks for kids.', 'Toys', 899, 'blocks.jpg'),
            ('Plush Teddy Bear', 'Soft and cuddly brown teddy bear.', 'Toys', 499, 'teddy.jpg'),
            ('Modern Sofa Set', 'Premium 3-seater sofa with velvet finish.', 'Furniture', 12999, 'sofa.jpg'),
            ('Study Table', 'Ergonomic wooden study table for students.', 'Furniture', 3499, 'table.jpg')
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
    seed_more_products()
