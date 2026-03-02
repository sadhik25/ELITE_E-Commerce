import urllib.request
import os

images = {
    'laptop.jpg': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80',
    'jacket.jpg': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80',
    'gown.jpg': 'https://images.unsplash.com/photo-1539008835279-434680970221?auto=format&fit=crop&w=800&q=80',
    'shirt.jpg': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80',
    'watch.jpg': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80',
    'racket.jpg': 'https://images.unsplash.com/photo-1622279457486-62dcc4a497c8?auto=format&fit=crop&w=800&q=80',
    'goggles.jpg': 'https://images.unsplash.com/photo-1551848243-568eb707849e?auto=format&fit=crop&w=800&q=80',
    'smart_device.jpg': 'https://images.unsplash.com/photo-1550009158-9ebf69173e03?auto=format&fit=crop&w=800&q=80'
}

dest_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'product_images')

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

for filename, url in images.items():
    dest_path = os.path.join(dest_dir, filename)
    print(f"Downloading {filename} to {dest_path}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Success.")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
