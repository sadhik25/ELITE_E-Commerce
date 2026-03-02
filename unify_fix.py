import sqlite3
import os
import config

def unify_fix():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    cursor = conn.cursor()

    print("--- Starting Unify Fix (Assigning better images) ---")

    # Mapping keywords to downloaded images
    image_assignment = [
        ("%Laptop%", "laptop.jpg"),
        ("%MacBook%", "laptop.jpg"),
        ("%Dell XPS%", "laptop.jpg"),
        ("%Spectre%", "laptop.jpg"),
        ("%Jacket%", "jacket.jpg"),
        ("%Gown%", "gown.jpg"),
        ("%Dress%", "gown.jpg"),
        ("%Shirt%", "shirt.jpg"),
        ("%T-shirt%", "shirt.jpg"),
        ("%Watch%", "watch.jpg"),
        ("%Smartwatch%", "watch.jpg"),
        ("%Racket%", "racket.jpg"),
        ("%Goggles%", "goggles.jpg"),
        ("%Dumbbell%", "smart_device.jpg"), # Not perfect but better than shoes
        ("%Device%", "smart_device.jpg"),
        ("%SSD%", "smart_device.jpg")
    ]

    for name_pattern, img_file in image_assignment:
        cursor.execute("UPDATE products SET image = ? WHERE name LIKE ?", (img_file, name_pattern))
        if cursor.rowcount > 0:
            print(f"Updated {cursor.rowcount} products matching {name_pattern} to {img_file}")

    # Fallback to category defaults if nothing else matched
    # (Ensure we don't have shoes in everything)
    
    # Fashion category should have a mix, if still 'nike_main.png', let's use shirt or jacket
    cursor.execute("UPDATE products SET image = 'shirt.jpg' WHERE category = 'Fashion' AND image = 'nike_main.png'")
    
    # Laptops category should have laptop.jpg
    cursor.execute("UPDATE products SET image = 'laptop.jpg' WHERE category = 'Laptops'")
    
    # Mobiles category 
    cursor.execute("UPDATE products SET image = 'iphone16.webp' WHERE category = 'Mobiles'")

    # Accessories
    cursor.execute("UPDATE products SET image = 'watch.jpg' WHERE category = 'Accessories'")

    conn.commit()
    cursor.close()
    conn.close()
    print("--- Unify Fix Done ---")

if __name__ == '__main__':
    unify_fix()
