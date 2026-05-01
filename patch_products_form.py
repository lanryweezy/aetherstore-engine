with open("backend/api/products.py", "r") as f:
    content = f.read()

content = content.replace("from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File", "from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form")

with open("backend/api/products.py", "w") as f:
    f.write(content)
