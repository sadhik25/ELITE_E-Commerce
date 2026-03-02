import urllib.request
import os

images = {
    'gown.jpg': 'https://images.unsplash.com/photo-1595777457583-95e2079ed3a5?w=800',
    'racket.jpg': 'https://images.unsplash.com/photo-1595435062232-132d75f280c7?w=800',
    'goggles.jpg': 'https://images.unsplash.com/photo-1582979512210-99b6a53386f9?w=800'
}

dest_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'product_images')

for filename, url in images.items():
    dest_path = os.path.join(dest_dir, filename)
    print(f"Downloading {filename} to {dest_path}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Success.")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
