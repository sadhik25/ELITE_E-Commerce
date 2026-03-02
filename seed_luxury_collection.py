import sqlite3
import os
import config

def seed_luxury_collection():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        cursor = conn.cursor()
        
        products = [
            # Fashion - Detailed with Sizes
            ('Oxford Button-Down Shirt', 'Premium 100% Egyptian cotton. Available Sizes: S, M, L, XL. Color: Classic White.', 'Fashion', 2499, 'shirt_oxford.jpg', 1),
            ('Slim-Fit Indigo Denims', 'High-stretch artisan denim with reinforced stitching. Sizes: 30, 32, 34, 36.', 'Fashion', 3299, 'jeans_indigo.jpg', 0),
            ('Floral Summer Midi Dress', 'Breathable linen blend, perfect for artisan outings. Sizes: XS, S, M, L.', 'Fashion', 4500, 'dress_floral.jpg', 1),
            ('Cashmere Turtleneck Sweater', 'Ultra-soft Mongolian cashmere for pure luxury. Sizes: M, L, XL.', 'Fashion', 5999, 'sweater_cashmere.jpg', 0),
            ('Structured Wool Blazer', 'Italian wool blend with silk lining. Elite fit. Sizes: 38, 40, 42, 44.', 'Fashion', 8999, 'blazer_wool.jpg', 1),
            ('High-Rise Tailored Trousers', 'Precision cut for a sophisticated silhouette. Sizes: 28, 30, 32.', 'Fashion', 3800, 'trousers_tailored.jpg', 0),
            ('Silk Wrap Evening Gown', 'Hand-finished pure mulberry silk. Adjustable fit. One Size (Fits S-L).', 'Fashion', 12500, 'gown_silk.jpg', 1),
            ('Premium Leather Biker Jacket', 'Top-grain lambskin leather. Handcrafted finish. Sizes: S, M, L.', 'Fashion', 15999, 'jacket_leather.jpg', 1),
            ('Organic Cotton Chino Shorts', 'Sustainable luxury for weekend leisure. Sizes: 30, 32, 34, 36.', 'Fashion', 1899, 'shorts_chino.jpg', 0),
            ('Graphic Urban Tee', 'Heavyweight 300GSM cotton with artisan print. Oversized Fit: S, M, L.', 'Fashion', 1499, 'tee_urban.jpg', 0),
            
            # Electronics
            ('Noise-Canceling Elite Buds', 'Active ANC with 40h battery and spatial audio support.', 'Electronics', 12999, 'buds_anc.jpg', 1),
            ('Mechanical Workstation Pro', 'Ultra-responsive switches with RGB backlight and macros.', 'Electronics', 7500, 'keyboard_pro.jpg', 0),
            ('Curved Gaming Monitor 34"', '4K UHD, 144Hz refresh rate for immersive experience.', 'Electronics', 45000, 'monitor_4k.jpg', 1),
            
            # Kitchen
            ('Precision Sous Vide Cooker', 'Restaurant-quality results at home. App-controlled.', 'Kitchen', 11999, 'kitchen_sousvide.jpg', 0),
            ('Artisan Stand Mixer', 'Metallic finish, 10-speed professional mixing power.', 'Kitchen', 25000, 'mixer_artisan.jpg', 1),
            
            # Sports
            ('Pro Carbon Tennis Racket', 'Ultra-lightweight carbon fiber for explosive power.', 'Sports', 18500, 'racket_carbon.jpg', 0),
            ('Artisan Leather Punching Bag', 'Hand-stitched genuine leather for elite training.', 'Sports', 9500, 'punching_bag.jpg', 0),
            
            # Toys
            ('Programmable Robotics Kit', 'Advanced STEM learning with AI integration.', 'Toys', 8400, 'toy_robot.jpg', 1),
            
            # Furniture
            ('Ergonomic Executive Throne', 'Top-tier lumbar support with premium leather finish.', 'Furniture', 22000, 'chair_executive.jpg', 1),
            ('Minimalist Marble Coffee Table', 'Genuine Italian marble with gold-finished legs.', 'Furniture', 14500, 'table_marble.jpg', 0)
        ]
        
        query = "INSERT INTO products (name, description, category, price, image, is_bestseller) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(query, products)
        
        conn.commit()
        print(f"Successfully added {cursor.rowcount} premium products to the catalog.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error seeding products: {e}")

if __name__ == '__main__':
    seed_luxury_collection()
