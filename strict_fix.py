import sqlite3
import os
import config
import os

def strict_fix():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Starting Strict Database Cleanup ---")

    # 1. Clean whitespace from all categories
    cursor.execute("UPDATE products SET category = TRIM(category)")
    print(f"Cleaned whitespace: {cursor.rowcount} rows affected.")

    # 2. Re-Categorize Products properly
    re_categorization = [
        # Electronics to Laptops/Accessories/Mobiles
        ("MacBook Pro 14 M3 Chip", "Laptops"),
        ("Asus ROG Strix G16", "Laptops"),
        ("HP Spectre x360", "Laptops"),
        ("iPhone 16 Pro", "Mobiles"),
        ("Samsung Galaxy S24 Ultra", "Mobiles"),
        ("Pixel 8 Pro", "Mobiles"),
        ("Fastrack Reflex Beat Smartwatch", "Accessories"),
        ("Apple Watch Series 9", "Accessories"),
        ("Nike Air Max 270 Sneakers", "Footwear"),
        ("Adidas Duramo Slide Sandals", "Footwear"),
    ]

    for name_partial, new_cat in re_categorization:
        cursor.execute("UPDATE products SET category = ? WHERE name LIKE ?", (new_cat, f"%{name_partial}%"))
        if cursor.rowcount > 0:
            print(f"Moved '{name_partial}' into '{new_cat}'")

    # 3. Fix Images (Using best available files for categories)
    # Available good images: 
    # sony_main.png, nike_main.png, shoes.jpg, coffee_maker.jpg, sofa.jpg, teddy.jpg, toy_car.jpg, iphone16.webp
    
    img_fix = {
        'Electronics': 'sony_main.png', 
        'Mobiles': 'iphone16.webp',
        'Footwear': 'shoes.jpg',
        'Sports': 'shoes.jpg', # Fallback for now
        'Kitchen': 'coffee_maker.jpg',
        'Furniture': 'sofa.jpg',
        'Toys': 'teddy.jpg',
        'Laptops': 'sony_main.png', # Placeholder
        'Accessories': 'watch.png', # Wait, watch.png is broken (7 bytes)
        'Fashion': 'shirt.png' # shirt.png is broken (7 bytes)
    }

    # Since some are broken, let's use the ones we KNOW are good:
    # Mobiles -> iphone16.webp (12k) - GOOD
    # Footwear -> nike_main.png (31k) or shoes.jpg (53k) - GOOD
    # Kitchen -> coffee_maker.jpg (67k) - GOOD
    # Furniture -> sofa.jpg (38k) - GOOD
    # Toys -> teddy.jpg (81k) or toy_car.jpg (39k) - GOOD
    # Electronics -> sony_main.png (21k) - GOOD
    
    cursor.execute("UPDATE products SET image = 'iphone16.webp' WHERE category = 'Mobiles'")
    cursor.execute("UPDATE products SET image = 'sony_main.png' WHERE category IN ('Electronics', 'Laptops', 'Accessories')")
    cursor.execute("UPDATE products SET image = 'nike_main.png' WHERE category = 'Footwear'")
    cursor.execute("UPDATE products SET image = 'shoes.jpg' WHERE category = 'Sports'")
    cursor.execute("UPDATE products SET image = 'coffee_maker.jpg' WHERE category = 'Kitchen'")
    cursor.execute("UPDATE products SET image = 'sofa.jpg' WHERE category = 'Furniture'")
    cursor.execute("UPDATE products SET image = 'teddy.jpg' WHERE category = 'Toys'")
    cursor.execute("UPDATE products SET image = 'nike_main.png' WHERE category = 'Fashion'") # Better than broken shirt.png

    print("Images updated for all categories.")

    # 4. Specific product image fix
    cursor.execute("UPDATE products SET image = 'toy_car.jpg' WHERE name LIKE '%Car%' OR name LIKE '%Truck%'")
    cursor.execute("UPDATE products SET image = 'nike_main.png' WHERE name LIKE '%Nike%' OR name LIKE '%Shirt%' OR name LIKE '%T-shirt%'")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("--- Cleanup Done ---")

if __name__ == '__main__':
    strict_fix()
