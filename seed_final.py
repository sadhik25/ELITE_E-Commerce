import sqlite3
import os
import config

def seed_final():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    cursor = conn.cursor()

    # 1. Add Rating Columns
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN rating FLOAT DEFAULT 4.5")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN rating_count INT DEFAULT 120")
    except:
        pass

    # 2. Add New Categories & Products
    new_products = [
        # Mobiles
        ("iPhone 16 Pro Max", "Experience the pinnacle of mobile technology with the iPhone 16 Pro Max. Featuring a stunning titanium design and the powerful A18 chip.", "Mobiles", 129999.0, "iphone_pro.png", 4.9, 850),
        ("Samsung Galaxy S24 Ultra", "The ultimate Android experience. AI-powered camera and sleek titanium frame.", "Mobiles", 114999.0, "iphone_pro.png", 4.8, 720), # Reusing iphone_pro as a placeholder for high-end mobile
        
        # Laptops
        ("Dell XPS 13 Plus", "Masterfully crafted from premium materials, the XPS 13 Plus is the most powerful 13-inch laptop in its class.", "Laptops", 145000.0, "dell_laptop.png", 4.7, 340),
        ("MacBook Pro M3", "The most advanced chips ever built for a personal computer.", "Laptops", 169999.0, "dell_laptop.png", 4.9, 560),
        
        # Accessories
        ("Luxury Leather Watch", "Handcrafted premium leather watch with Swiss movement.", "Accessories", 12500.0, "watch.png", 4.6, 180),
        ("Classic Brown Leather Belt", "Genuine Italian leather belt for a formal look.", "Accessories", 2500.0, "watch.png", 4.5, 90), # Reuse watch or something until better
        
        # Fashion (Specific items)
        ("Premium Slim Fit Shirt", "100% Cotton premium slim fit shirt for all occasions.", "Fashion", 2499.0, "shirt.png", 4.4, 210),
        ("Regular Fit Denim Pants", "Classic blue denim jeans with a modern fit.", "Fashion", 3999.0, "pants.png", 4.3, 350),
        ("Oversized Graphic T-Shirt", "Cool streetwear oversized t-shirt with minimalist design.", "Fashion", 1299.0, "tshirt.png", 4.5, 420),
        ("Cotton Casual Shirt", "Breathable cotton casual shirt ideal for summer.", "Fashion", 1899.0, "shirt.png", 4.2, 115),
        ("Slim Denim Jeans", "Trendy slim fit denim jeans for a sharp look.", "Fashion", 3499.0, "pants.png", 4.4, 235),
    ]

    for p in new_products:
        cursor.execute("""
            INSERT INTO products (name, description, category, price, image, rating, rating_count, added_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (p[0], p[1], p[2], p[3], p[4], p[5], p[6], 1)) # Assuming admin_id 1 exists

    # 3. Update existing products to have unique-ish images and ratings
    updates = [
        ("Sony WH-1000XM5", "sony_main.png", 4.8),
        ("Nike Air Max 270", "nike_main.png", 4.7),
        ("Spalding NBA Official Game Basketball", "toy_car.jpg", 4.5), # Basketball... use toy car or something better?
        ("MacBook Pro 14 M3", "dell_laptop.png", 4.9),
        ("Fastrack Reflex Beat", "watch.png", 4.0),
        ("Presstige Iris", "coffee_maker.jpg", 4.3),
        ("Sofa", "sofa.jpg", 4.6),
        ("Teddy Bear", "teddy.jpg", 4.8),
        ("Luxury Recliner Sofa", "sofa.jpg", 4.7)
    ]

    for name_part, img, rate in updates:
        cursor.execute("UPDATE products SET image=?, rating=? WHERE name LIKE ?", (img, rate, f"%{name_part}%"))

    # Cleanup: If any product still has 'nike_main.png' but is not Footwear, change it.
    cursor.execute("UPDATE products SET image='shirt.png' WHERE category='Fashion' AND image='nike_main.png'")
    cursor.execute("UPDATE products SET image='pants.png' WHERE category='Fashion' AND name LIKE '%Pants%'")
    cursor.execute("UPDATE products SET image='shirt.png' WHERE category='Fashion' AND name LIKE '%Shirt%'")

    conn.commit()
    cursor.close()
    conn.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_final()
