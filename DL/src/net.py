import torch
from torch import nn
from torchvision import transforms, datasets
from torch.utils.data.dataloader import DataLoader
import torch.optim as optim
from torchinfo import summary
import os

from .check_data import is_valid_file


class mixed_net(nn.Module):
    """小型 CNN：3 Conv + 2 FC，权重层共 5 层"""
    def __init__(self, num_classes=3):
        super(mixed_net, self).__init__()

        # 第 1 个卷积块: 3 -> 16
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),   # 16 x 64 x 64
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                            # 16 x 32 x 32
        )

        # 第 2 个卷积块: 16 -> 32
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, padding=1),  # 32 x 32 x 32
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                            # 32 x 16 x 16
        )

        # 第 3 个卷积块: 32 -> 64
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 64 x 16 x 16
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                            # 64 x 8 x 8
        )

        # 全连接层: 64*8*8 = 4096 -> 256 -> 3
        self.fc = nn.Sequential(
            nn.Flatten(),                                  # 4096
            nn.Linear(64 * 8 * 8, 256),                   # 256
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),                   # 3
        )

    def forward(self, x):
        """
        前向传播，每层尺寸注释：
        输入: (B, 3, 64, 64)

        conv1: (B, 16, 32, 32)
        conv2: (B, 32, 16, 16)
        conv3: (B, 64, 8, 8)

        flatten: (B, 4096)
        fc:      (B, 3)
        """
        x = self.conv1(x)   # (B, 16, 32, 32)
        x = self.conv2(x)   # (B, 32, 16, 16)
        x = self.conv3(x)   # (B, 64, 8, 8)
        x = self.fc(x)      # (B, 3)
        return x


def validate(model, loader, criterion, device):
    """在给定 loader 上计算 loss 和 accuracy"""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for datas, labels in loader:
            datas, labels = datas.to(device), labels.to(device)
            outputs = model(datas)
            loss = criterion(outputs, labels)
            total_loss += loss.item()

            _, predicted = torch.max(outputs, dim=1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    avg_loss = total_loss / len(loader)
    accuracy = 100.0 * correct / total
    model.train()
    return avg_loss, accuracy


if __name__ == "__main__":
    # 项目根目录
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 图像处理和简单数据增强
    train_transform = transforms.Compose([
        transforms.Resize([64, 64]),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    test_transform = transforms.Compose([
        transforms.Resize([64, 64]),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    # 超参数
    BATCH_SIZE = 64
    EPOCH = 50

    # 加载数据
    trainset = datasets.ImageFolder(
        root=os.path.join(ROOT, "dataset", "train"),
        transform=train_transform,
        is_valid_file=is_valid_file,
    )
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

    print(f"训练集图片数量: {len(trainset)}")
    print(f"测试集1图片数量: {len(testset1)}")
    print(f"测试集2图片数量: {len(testset2)}")
    print(f"标签映射: {trainset.class_to_idx}")

    train_loader = DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)
    test_loader1 = DataLoader(testset1, batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)
    test_loader2 = DataLoader(testset2, batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)

    # 选择设备
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"设备: {device}")

    # 创建网络
    net = mixed_net(num_classes=3).to(device)
    summary(net, input_size=(1, 3, 64, 64), device=device)

    # 优化器和损失函数
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(net.parameters(), lr=0.001, weight_decay=1e-4)
    # 之前试过的 SGD 写法：
    # optimizer = optim.SGD(net.parameters(), lr=0.01, momentum=0.9)

    # 开始训练
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)
    best_acc = 0.0
    best_path = os.path.join(ROOT, "models", "model_best.pth")

    print("\nStart Training\n")

    for epoch in range(1, EPOCH + 1):
        net.train()
        train_loss = 0.0

        for datas, labels in train_loader:
            datas, labels = datas.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = net(datas)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # 每个 epoch 在 test1 上验证
        avg_train_loss = train_loss / len(train_loader)
        test_loss, test_acc = validate(net, test_loader1, criterion, device)

        print(f"Train Epoch: {epoch:2d}    Loss: {avg_train_loss:.6f}")
        print(f"Test  -- Average Loss: {test_loss:.4f}, Accuracy: {test_acc:.3f}%")

        # 保存最佳模型
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save(net.state_dict(), best_path)
            print(f"save best model, acc={best_acc:.3f}%")

        print()

    print(f"Training done. Best test1 accuracy: {best_acc:.3f}%")
    print(f"Model saved to: {best_path}")

    # 最后在 test1 和 test2 上看一下整体效果
    net.load_state_dict(torch.load(best_path, weights_only=True))
    net.eval()

    for name, loader in [("test1", test_loader1), ("test2", test_loader2)]:
        loss, acc = validate(net, loader, criterion, device)
        print(f"Final {name} -- Loss: {loss:.4f}, Accuracy: {acc:.3f}%")
