import os

# 修改路径
train_img_dir = 'D:/lwh/Yolo-FastestV2/train/images'
val_img_dir   = 'D:/lwh/Yolo-FastestV2/valid/images'

train_txt_path = 'D:/lwh/Yolo-FastestV2/train/train.txt'
val_txt_path   = 'D:/lwh/Yolo-FastestV2/valid/val.txt'

def generate_txt(img_dir, output_txt):
    with open(output_txt, 'w') as f:
        for file in os.listdir(img_dir):
            if file.endswith('.jpg'):
                full_path = os.path.join(img_dir, file).replace('\\', '/')
                f.write(full_path + '\n')

generate_txt(train_img_dir, train_txt_path)
generate_txt(val_img_dir, val_txt_path)

print(" 已成功生成 train.txt 和 val.txt！")