import cv2
import os

# 路径配置
image_dir = 'images'     # 你的图片目录
label_dir = 'labels'     # 对应的标签目录
class_names = ['tennis']  # 替换成你自己的类别名

# 画框函数
def draw_boxes(image_path, label_path):
    image = cv2.imread(image_path)
    h, w = image.shape[:2]

    # 检查标签是否存在
    if not os.path.exists(label_path):
        print(f'标签不存在: {label_path}')
        return image

    with open(label_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue  # 跳过格式错误的行

        class_id, x_center, y_center, box_w, box_h = map(float, parts)
        class_id = int(class_id)

        # 还原到像素坐标
        x1 = int((x_center - box_w / 2) * w)
        y1 = int((y_center - box_h / 2) * h)
        x2 = int((x_center + box_w / 2) * w)
        y2 = int((y_center + box_h / 2) * h)

        # 绘制矩形和类别
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = class_names[class_id] if class_id < len(class_names) else str(class_id)
        cv2.putText(image, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return image

# 遍历并显示图像
for filename in os.listdir(image_dir):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        img_path = os.path.join(image_dir, filename)
        label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + '.txt')

        image = draw_boxes(img_path, label_path)

        cv2.imshow('Labeled Image', image)
        key = cv2.waitKey(0)
        if key == ord('q'):  # 按q退出
            break

cv2.destroyAllWindows()
