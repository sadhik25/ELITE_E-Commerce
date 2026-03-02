import sqlite3
import os
import config

def fix_all_images():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    cursor = conn.cursor()

    print("--- Starting Detailed Image Fix ---")

    # 1. Broad Category Defaults (Safe Fallbacks)
    category_defaults = {
        'Electronics': 'sony_main.png',
        'Laptops': 'dell_laptop.png',
        'Mobiles': 'iphone_pro.png',
        'Fashion': 'shirt.jpg',
        'Footwear': 'nike_main.png',
        'Kitchen': 'coffee_maker.jpg',
        'Furniture': 'sofa.jpg',
        'Toys': 'teddy.jpg',
        'Sports': 'sports.jpg',
        'Accessories': 'watch.jpg'
    }

    for cat, img in category_defaults.items():
        cursor.execute("UPDATE products SET image = ? WHERE category = ?", (img, cat))
        print(f"Updated {cat} -> {img} ({cursor.rowcount} rows)")

    # 2. Keyword Specific Fixes (More accurate)
    keyword_fixes = [
        ('%Jacket%', 'jacket.jpg'),
        ('%Blazer%', 'jacket.jpg'),
        ('%Dress%', 'gown.jpg'),
        ('%Gown%', 'gown.jpg'),
        ('%T-shirt%', 'shirt.jpg'),
        ('%Shirt%', 'shirt.jpg'),
        ('%Shoes%', 'shoes.jpg'),
        ('%Sneaker%', 'shoes.jpg'),
        ('%Running%', 'nike_main.png'),
        ('%Formal%', 'shoes.jpg'),
        ('%Oxford%', 'shoes.jpg'),
        ('%Boot%', 'shoes.jpg'),
        ('%Loafer%', 'shoes.jpg'),
        ('%Monitor%', 'sony_main.png'),
        ('%Mic%', 'sony_main.png'),
        ('%SSD%', 'dell_laptop.png'),
        ('%Charger%', 'iphone_pro.png'),
        ('%Racket%', 'racket.jpg'),
        ('%Telescope%', 'sports.jpg'),
        ('%Rover%', 'toy_car.jpg'),
        ('%Toy%', 'teddy.jpg'),
        ('%Storyteller%', 'teddy.jpg'),
        ('%Basketball%', 'sports.jpg'),
        ('%Yoga%', 'sports.jpg'),
        ('%Goggles%', 'goggles.jpg')
    ]

    for pattern, img in keyword_fixes:
        cursor.execute("UPDATE products SET image = ? WHERE name LIKE ?", (img, pattern))
        if cursor.rowcount > 0:
            print(f"Refined Match: {pattern} -> {img} ({cursor.rowcount} rows)")

    conn.commit()
    cursor.close()
    conn.close()
    print("--- Image Fix Complete ---")

if __name__ == '__main__':
    fix_all_images()
