import sqlite3
import os
import config

def final_strict_fix():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    cursor = conn.cursor()

    # 1. Update Laptops
    cursor.execute("UPDATE products SET image = 'laptop.jpg' WHERE category = 'Laptops' OR name LIKE '%Laptop%' OR name LIKE '%MacBook%' OR name LIKE '%Dell XPS%'")

    # 2. Update Fashion
    cursor.execute("UPDATE products SET image = 'jacket.jpg' WHERE name LIKE '%Jacket%' OR name LIKE '%Blazer%' OR name LIKE '%Coat%'")
    cursor.execute("UPDATE products SET image = 'gown.jpg' WHERE name LIKE '%Gown%' OR name LIKE '%Dress%'")
    cursor.execute("UPDATE products SET image = 'shirt.jpg' WHERE name LIKE '%Shirt%' OR name LIKE '%T-shirt%' OR (category = 'Fashion' AND image = 'nike_main.png')")

    # 3. Update Sports
    cursor.execute("UPDATE products SET image = 'racket.jpg' WHERE name LIKE '%Racket%'")
    cursor.execute("UPDATE products SET image = 'goggles.jpg' WHERE name LIKE '%Goggles%'")
    # Basketball, Fitness, etc. -> sports.jpg
    cursor.execute("UPDATE products SET image = 'sports.jpg' WHERE category = 'Sports' AND image = 'shoes.jpg'")
    cursor.execute("UPDATE products SET image = 'sports.jpg' WHERE name LIKE '%Basketball%' OR name LIKE '%Yoga%' OR name LIKE '%Mat%' OR name LIKE '%Bag%'")

    # 4. Mobiles
    cursor.execute("UPDATE products SET image = 'iphone16.webp' WHERE category = 'Mobiles' OR name LIKE '%iPhone%' OR name LIKE '%Galaxy%'")

    # 5. Accessories
    cursor.execute("UPDATE products SET image = 'watch.jpg' WHERE category = 'Accessories' OR name LIKE '%Watch%'")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    final_strict_fix()
