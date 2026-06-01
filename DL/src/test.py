import torch
from torchvision import transforms, datasets
from torch.utils.data.dataloader import DataLoader
from .net import mixed_net
import os

from .check_data import is_valid_file


def test_model(model, loader, device, dataset_name, class_names=None):
    """在给定 loader 上打印 Overall Accuracy 和每类 Accuracy"""
    class_correct = [0] * 3
    class_total = [0] * 3

    model.eval()
    with torch.no_grad():
        for datas, labels in loader:
            datas, labels = datas.to(device), labels.to(device)
            outputs = model(datas)
            _, predicted = torch.max(outputs, dim=1)

            matches = (predicted == labels)
            for i in range(len(labels)):
                label = labels[i].item()
                class_correct[label] += matches[i].item()
                class_total[label] += 1

    total_correct = sum(class_correct)
    total = sum(class_total)
    overall = 100.0 * total_correct / total if total > 0 else 0.0
    print(f"{dataset_name} Overall Accuracy:{overall:.2f}%")

    if class_names is None:
        class_names = ["0", "1", "2"]
    for i in range(3):
        acc = 100.0 * class_correct[i] / class_total[i] if class_total[i] > 0 else 0.0
        print(f"Category Accuracy : {class_names[i]:>6s} : {acc:.2f} %")


if __name__ == "__main__":
    # 项目根目录
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 模型路径
    model_path = os.path.join(ROOT, "models", "model_best.pth")

    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Please train the model first (run: python -m src.net).")
        exit(1)

    # 加载测试数据
    BATCH_SIZE = 256

    test_transform = transforms.Compose([
        transforms.Resize([64, 64]),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    testset1 = datasets.ImageFolder(
        root=os.path.join(ROOT, "dataset", "test1"),
        transform=test_transform,
        is_valid_file=is_valid_file,
    )
    testset2 = datasets.ImageFolder(
        root=os.path.join(ROOT, "dataset", "test2"),
        transform=test_transform,
        is_valid_file=is_valid_file,
    )

    print(f"test1 图片数量: {len(testset1)}")
    print(f"test2 图片数量: {len(testset2)}")

    test_loader1 = DataLoader(testset1, batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)
    test_loader2 = DataLoader(testset2, batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)

    # 选择设备
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"设备: {device}\n")

    # 加载模型
    model = mixed_net(num_classes=3).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))

    # 测试
    class_names = testset1.classes  # ImageFolder 字母序: blue, red, yellow

    print("=== test1 ===")
    test_model(model, test_loader1, device, "test1", class_names)

    print("\n=== test2 ===")
    test_model(model, test_loader2, device, "test2", class_names)
