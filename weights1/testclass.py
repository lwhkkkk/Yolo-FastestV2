import torch

pth_path = "coco.pth"
state_dict = torch.load(pth_path, map_location="cpu")

output_path = "model_info.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(" 模型权重参数名：\n")
    for k in state_dict.keys():
        f.write(k + "\n")
        if 'conf' in k or 'cls' in k:
            shape_str = str(state_dict[k].shape)
            f.write(f"   该层可能与类别数有关，形状为：{shape_str}\n")

print(f" 模型参数信息已保存至 {output_path}")
