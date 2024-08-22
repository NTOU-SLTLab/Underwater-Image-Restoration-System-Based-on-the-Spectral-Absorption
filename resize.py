from PIL import Image
import os

def resize_images(input_folder, output_folder, new_width, new_height):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.JPEG')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            img_resized = img.resize((new_width, new_height), Image.ANTIALIAS)
            img_resized.save(os.path.join(output_folder, filename))


input_folder = 'D:/11053022/20231127/Hierarchical/0410/EUVP_dataset/trainA'
output_folder = 'D:/11053022/20231127/Hierarchical/0410/EUVP_dataset/trainA'

# 調整圖片尺寸
resize_images(input_folder, output_folder, 512, 482)
