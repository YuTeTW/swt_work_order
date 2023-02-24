import os

from fastapi import HTTPException
from sqlalchemy.orm import Session


async def upload_picture_to_folder(db: Session, order_id: int, client_id: int, picture_file):
    # order = db.query(Order).filter(Order.id == order_id, Order.client_id == client_id).first()
    # if not order:
    #     HTTPException(status_code=401, detail="client only can upload file to his order")

    file_dir = os.path.join(os.getcwd(), f"db_image/order_pic_name_by_id/{order_id}/")
    os.makedirs(file_dir, exist_ok=True)
    try:
        file_path = os.path.join(file_dir, picture_file.filename)
        with open(file_path, "wb") as f:
            f.write(await picture_file.read())
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Failed to upload image")
    return {"message": "Image uploaded successfully"}


def download_picture_from_folder(order_id, file_name):
    print("abc")
    file_path = os.getcwd() + f"/db_image/order_pic_name_by_id/{order_id}/" + file_name
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image doesn't exist.")
    try:
        from starlette.responses import FileResponse

        # 如果檔案是圖片，直接顯示
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            image_path = os.getcwd() + f"/db_image/order_pic_name_by_id/{order_id}/{file_name}"
            return FileResponse(image_path, media_type="image/png")

        # 如果檔案是其他類型，下載
        else:
            file_path = os.getcwd() + f"/db_image/order_pic_name_by_id/{order_id}/{file_name}"
            return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to download image")


def delete_picture_from_folder(db: Session, order_id, file_name):
    dir_path = os.getcwd() + f"/db_image/order_pic_name_by_id/{order_id}/"
    file_path = dir_path + str(file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image doesn't exist.")
    try:
        os.remove(file_path)
        if not os.listdir(dir_path):  # 判斷資料夾是否為空
            os.rmdir(dir_path)  # 刪除空資料夾
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to Delete image")
    return "Image deleted successfully"