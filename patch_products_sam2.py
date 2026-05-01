import re

with open("backend/api/products.py", "r") as f:
    content = f.read()

# Add endpoint without rembg or SAM 2 background removal directly to use the one in ai_processing
new_endpoint = """
@router.post("/upload-image-rmbg/{product_id}")
async def upload_product_image_rmbg(
    product_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    alt_text: str = Form(None),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    \"\"\"Upload a product image and automatically remove its background using SAM 2\"\"\"
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Authorize
    db_brand = get_brand(db, db_product.brand_id)
    if db_brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    upload_dir = "uploads/product_images"
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
    file_id = str(uuid.uuid4())
    raw_path = os.path.join(upload_dir, f"raw_{product_id}_{file_id}{file_ext}")
    final_path = raw_path

    # Save original file
    with open(raw_path, "wb+") as file_object:
        file_object.write(await file.read())

    # Background Removal with SAM 2 via ai_processing logic
    from ai_processing import AIProcessor
    processor = AIProcessor()

    if hasattr(processor, 'sam_3d_objects') and hasattr(processor.sam_3d_objects, 'remove_background'):
        processed_path = os.path.join(upload_dir, f"nobg_{product_id}_{file_id}.png")

        # We need to copy raw to processed so SAM can operate on it and save it
        import shutil
        shutil.copyfile(raw_path, processed_path)

        success = processor.sam_3d_objects.remove_background(processed_path)
        if success:
            final_path = processed_path
            try:
                os.remove(raw_path)
            except:
                pass
        else:
            try:
                os.remove(processed_path)
            except:
                pass

    db_image = ProductImage(
        id=str(uuid.uuid4()),
        product_id=product_id,
        image_url=final_path,
        alt_text=alt_text,
        is_primary=is_primary,
        created_at=datetime.utcnow()
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return db_image

"""

# Insert the new endpoint right before `@router.get("/{product_id}/images/"`
pattern = r'@router\.get\("/\{product_id\}/images/"'
content = re.sub(pattern, new_endpoint + '\n@router.get("/{product_id}/images/"', content)

with open("backend/api/products.py", "w") as f:
    f.write(content)
