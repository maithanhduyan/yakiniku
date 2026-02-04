"""
Download menu images from web sources and save to backend/static/images/menu
Run: cd backend && python scripts/download_images.py
"""
import os
import requests
from pathlib import Path

# Images directory
IMAGES_DIR = Path(__file__).parent.parent / "static" / "images" / "menu"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Image sources (using free stock images)
# Using Unsplash and Pexels images that are free to use
IMAGE_SOURCES = {
    # Meat
    "harami.jpg": "https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400&q=80",
    "tan.jpg": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400&q=80",
    "kalbi.jpg": "https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400&q=80",
    "kalbi_regular.jpg": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&q=80",
    "rosu.jpg": "https://images.unsplash.com/photo-1546833998-877b37c2e5c6?w=400&q=80",
    "rosu_regular.jpg": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?w=400&q=80",
    "horumon.jpg": "https://images.unsplash.com/photo-1432139509613-5c4255815697?w=400&q=80",
    "tokusenmori.jpg": "https://images.unsplash.com/photo-1594041680534-e8c8cdebd659?w=400&q=80",
    "buta_kalbi.jpg": "https://images.unsplash.com/photo-1623653387945-2fd25214f8fc?w=400&q=80",
    "tori_momo.jpg": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400&q=80",
    
    # Drinks
    "beer.jpg": "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400&q=80",
    "beer_bottle.jpg": "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400&q=80",
    "highball.jpg": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400&q=80",
    "lemon_sour.jpg": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400&q=80",
    "umeshu.jpg": "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400&q=80",
    "makgeolli.jpg": "https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=400&q=80",
    "shochu.jpg": "https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=400&q=80",
    "oolong.jpg": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80",
    "cola.jpg": "https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=400&q=80",
    "orange.jpg": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&q=80",
    
    # Salad
    "choregi.jpg": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80",
    "caesar.jpg": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400&q=80",
    "namul.jpg": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&q=80",
    "kimchi.jpg": "https://images.unsplash.com/photo-1498579150354-977475b7ea0b?w=400&q=80",
    
    # Rice & Noodles
    "rice.jpg": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400&q=80",
    "rice_large.jpg": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400&q=80",
    "bibimbap.jpg": "https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400&q=80",
    "reimen.jpg": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80",
    "kuppa.jpg": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&q=80",
    
    # Side dishes
    "wakame.jpg": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&q=80",
    "tail_soup.jpg": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&q=80",
    "edamame.jpg": "https://images.unsplash.com/photo-1564894809611-1742fc40ed80?w=400&q=80",
    "nori.jpg": "https://images.unsplash.com/photo-1519984388953-d2406bc725e1?w=400&q=80",
    "chijimi.jpg": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&q=80",
    
    # Desserts
    "vanilla_ice.jpg": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&q=80",
    "annin.jpg": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80",
    "sherbet.jpg": "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400&q=80",
    
    # Set menus
    "teishoku.jpg": "https://images.unsplash.com/photo-1580822184713-fc5400e7fe10?w=400&q=80",
    "teishoku_premium.jpg": "https://images.unsplash.com/photo-1594041680534-e8c8cdebd659?w=400&q=80",
    "ladies_course.jpg": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&q=80",
}


def download_image(filename: str, url: str):
    """Download image from URL and save to file."""
    filepath = IMAGES_DIR / filename
    
    if filepath.exists():
        print(f"⏭️  Skip (exists): {filename}")
        return True
    
    try:
        print(f"⬇️  Downloading: {filename}...", end=" ")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        print(f"✅ ({len(response.content) // 1024}KB)")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n🖼️  Downloading menu images...\n")
    print(f"📁 Target directory: {IMAGES_DIR}\n")
    
    success = 0
    failed = 0
    
    for filename, url in IMAGE_SOURCES.items():
        if download_image(filename, url):
            success += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {success} downloaded, {failed} failed")
    print(f"📁 Images saved to: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
