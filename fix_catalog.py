import sqlite3
import os
import config

def fix_catalog_issues():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Update images to use existing files for now
        image_map = {
            'Electronics': 'sony_main.png',
            'Fashion': 'nike_main.png',
            'Footwear': 'shoes.jpg',
            'Kitchen': 'coffee_maker.jpg',
            'Sports': 'shoes.jpg',
            'Toys': 'teddy.jpg',
            'Furniture': 'sofa.jpg'
        }
        
        for cat, img in image_map.items():
            cursor.execute("UPDATE products SET image = ? WHERE category = ? AND image NOT IN ('coffee_maker.jpg', 'iphone16.webp', 'nike_main.png', 'shoes.jpg', 'sofa.jpg', 'sony_main.png', 'teddy.jpg', 'toy_car.jpg')", (img, cat))
            print(f"Updated {cursor.rowcount} products in {cat} to use {img}")

        # 2. Check and fix category whitespace/casing
        cursor.execute("SELECT DISTINCT category FROM products")
        categories = cursor.fetchall()
        for cat_row in categories:
            original = cat_row['category']
            cleaned = original.strip()
            if original != cleaned:
                cursor.execute("UPDATE products SET category = ? WHERE category = ?", (cleaned, original))
                print(f"Cleaned whitespace for category: '{original}' -> '{cleaned}'")

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error fixing catalog: {e}")

if __name__ == '__main__':
    fix_catalog_issues()
