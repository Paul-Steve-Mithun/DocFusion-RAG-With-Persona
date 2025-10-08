"""
Upload DocFusion logo to Cloudinary for use in emails
Run this once to get the logo URL, then update email_service.py
"""
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_logo():
    """Upload the DocFusion logo to Cloudinary"""
    logo_path = "../frontend/src/assets/DocFusion.png"
    
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found at: {logo_path}")
        return None
    
    print("📤 Uploading logo to Cloudinary...")
    
    try:
        # Upload with a specific public_id so it's easy to reference
        result = cloudinary.uploader.upload(
            logo_path,
            public_id="docfusion_logo",
            folder="docfusion",
            overwrite=True,
            resource_type="image",
            transformation=[
                {"width": 200, "height": 200, "crop": "fit"},  # Resize for email
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        
        logo_url = result['secure_url']
        print(f"\n✅ Logo uploaded successfully!")
        print(f"\n📋 Logo URL: {logo_url}")
        print(f"\n🔗 Public ID: {result['public_id']}")
        print(f"📏 Size: {result['width']}x{result['height']}px")
        print(f"📦 Format: {result['format']}")
        print(f"\n💡 Add this to your .env file:")
        print(f"LOGO_URL={logo_url}")
        print(f"\n🎯 Next step: Update email_service.py to use this URL")
        
        return logo_url
        
    except Exception as e:
        print(f"❌ Failed to upload logo: {e}")
        return None

if __name__ == "__main__":
    print("🚀 DocFusion Logo Uploader\n")
    
    # Check Cloudinary config
    if not all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET")
    ]):
        print("❌ Cloudinary credentials not found in .env file")
        print("Please add: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
        exit(1)
    
    upload_logo()

