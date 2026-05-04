import os
import requests
import sys

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"✅ {dest_path} already exists. Skipping.")
        return True
    
    print(f"⏳ Downloading {url} to {dest_path}...")
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Successfully downloaded {dest_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def main():
    weights_to_download = [
        {
            "name": "OpenFashionCLIP",
            "url": "https://github.com/aimagelab/open-fashion-clip/releases/download/v1.0/openfashionclip.pt",
            "dest": "backend/ai_models/openfashionclip.pt"
        },
        {
            "name": "SAM 2 (tiny)",
            "url": "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_tiny.pt",
            "dest": "backend/ai_models/sam2.pt"
        }
    ]
    
    print("🚀 Starting AI Model Weights Downloader...")
    
    success_count = 0
    for weight in weights_to_download:
        if download_file(weight["url"], weight["dest"]):
            success_count += 1
            
    print(f"\n✨ Completed! {success_count}/{len(weights_to_download)} models ready.")
    
    if success_count < len(weights_to_download):
        print("⚠️ Some downloads failed. Please check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
