import sqlite3
import os
import config

def seed_complete_elite_catalog():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        cursor = conn.cursor()
        
        products = [
            # --- TOYS (Educational, Robotics, Collectibles) ---
            ('Galileo Refractor Telescope', 'Complete astronomy kit for youth. 70mm aperture with smartphone adapter.', 'Toys', 5499, 'toy_telescope.jpg', 1),
            ('Solar Powered Mars Rover', 'Build-your-own robotics kit. Educational STEM toy for future engineers.', 'Toys', 2899, 'toy_rover.jpg', 0),
            ('Magnetic Architectural Tiles', '100-piece 3D building set for creative construction.', 'Toys', 3500, 'toy_tiles.jpg', 1),
            ('Handcrafted Wooden Train Set', 'Sustainable birch wood tracks and locomotives. Artisan finish.', 'Toys', 4200, 'toy_train.jpg', 0),
            ('Interactive AI Storyteller', 'Smart companion with voice recognition and 500+ built-in tales.', 'Toys', 6800, 'toy_storyteller.jpg', 0),
            
            # --- SPORTS (Equipment, Gym, Tennis) ---
            ('Titanium Tennis Racket Pro', 'Carbon-fiber frame with vibration dampening technology.', 'Sports', 14500, 'sports_racket.jpg', 1),
            ('Elite Yoga & Pilates Mat', 'Non-slip natural rubber with alignment lines. Extra thick 6mm.', 'Sports', 2499, 'sports_mat.jpg', 0),
            ('Professional Basketball 7#', 'Advanced moisture-wicking surface for ultimate grip.', 'Sports', 1899, 'sports_ball.jpg', 0),
            ('Adjustable Smart Dumbbell', 'Compact weight system from 2kg to 24kg. Commercial grade.', 'Sports', 12999, 'sports_dumbbell.jpg', 1),
            ('Hydro-Pro Swimming Goggles', 'Anti-fog wide-view lenses with secure silicone seal.', 'Sports', 1200, 'sports_goggles.jpg', 0),

            # --- FOOTWEAR (Sneakers, Formal, Casual) ---
            ('Velocity Pro Running Shoes', 'Nitrogen-infused foam for maximum energy return. Sizes: 7, 8, 9, 10, 11.', 'Footwear', 6500, 'footwear_running.jpg', 1),
            ('Hand-Burnished Oxford Brogues', 'Genuine Italian calfskin leather. Artisan hand-finish. Sizes: 8, 9, 10.', 'Footwear', 8999, 'footwear_formal.jpg', 0),
            ('City-Walk Suede Loafers', 'Soft water-resistant suede with memory foam insole. Sizes: 7, 8, 9, 10.', 'Footwear', 4599, 'footwear_loafers.jpg', 0),
            ('Hiking Trail-Blazer Boots', 'Waterproof GORE-TEX lining with Vibram outsoles. Sizes: 8, 9, 10, 11.', 'Footwear', 12500, 'footwear_boots.jpg', 1),
            ('Canvas Retro High-Tops', 'Classic streetwear silhouette with reinforced vulcanized soles. Sizes: 6-11.', 'Footwear', 2800, 'footwear_hightop.jpg', 0),

            # --- ELECTRONICS (Home, Personal, Office) ---
            ('Zenith Ultra-Wide Monitor', '49-inch curved workstation with 5K resolution and 120Hz.', 'Electronics', 85000, 'elec_monitor.jpg', 1),
            ('Stream-Master Mic Pro', 'Studio-quality condenser microphone for professional recording.', 'Electronics', 15999, 'elec_mic.jpg', 0),
            ('Aura Ambient Smart Lamp', 'Voice-controlled LED with 16 million colors and sleep timer.', 'Electronics', 4200, 'elec_lamp.jpg', 0),
            ('Core-X Portable SSD 2TB', 'Ultra-fast 2000MB/s transfer speeds. Impact resistant shell.', 'Electronics', 18500, 'elec_ssd.jpg', 1),
            ('Neo-Pad Wireless Charger', 'Triple-device charging station with MagSafe compatibility.', 'Electronics', 3500, 'elec_charger.jpg', 0),

            # --- KITCHEN (Appliances & Tools) ---
            ('Nu-Wave Induction Cooktop', 'Precise temperature control with touch-glass interface.', 'Kitchen', 5999, 'kitchen_cooktop.jpg', 0),
            ('Artisan French Press 1L', 'Mirror-finished stainless steel with triple filtration.', 'Kitchen', 3200, 'kitchen_press.jpg', 0)
        ]
        
        query = "INSERT INTO products (name, description, category, price, image, is_bestseller) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(query, products)
        
        conn.commit()
        print(f"Successfully added {cursor.rowcount} artisan products across all categories.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error seeding catalog: {e}")

if __name__ == '__main__':
    seed_complete_elite_catalog()
