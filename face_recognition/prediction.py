"""
# author: shiyipaisizuo
# contact: shiyipaisizuo@gmail.com
# file: prediction.py
# time: 2018/8/13 09:23
# license: MIT
"""

import argparse
import os

import torch
import torchvision
from torch import nn
from torchvision import transforms

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

parser = argparse.ArgumentParser("""Image classifical!""")
parser.add_argument('--path', type=str, default='../data/A/',
                    help="""image dir path default: '../data/A/'.""")
parser.add_argument('--batch_size', type=int, default=1,
                    help="""Batch_size default:16.""")
parser.add_argument('--num_classes', type=int, default=8,
                    help="""num classes""")
parser.add_argument('--model_path', type=str, default='../../model/pytorch/',
                    help="""Save model path""")
parser.add_argument('--model_name', type=str, default='faces.pth',
                    help="""Model name.""")

args = parser.parse_args()

# Create model
if not os.path.exists(args.model_path):
    os.makedirs(args.model_path)

transform = transforms.Compose([
    transforms.Resize(128),  # 将图像转化为32 * 32
    transforms.RandomCrop(114),  # 从图像中裁剪一个24 * 24的
    transforms.Grayscale(),
    transforms.ToTensor(),  # 将numpy数据类型转化为Tensor
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # 归一化
])


class Net(nn.Module):
    def __init__(self, category=args.num_classes):
        super(Net, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, 1, 1),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(16, 32, 3, 1, 1),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(32, 64, 3, 1, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(64, 128, 3, 1, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

            nn.Conv2d(128, 128, 3, 1, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2)
        )

        self.classifier = nn.Sequential(
            nn.Dropout(p=0.75),
            nn.Linear(128 * 7 * 7, 128),
            nn.ReLU(True),
            nn.Dropout(p=0.75),
            nn.Linear(128, 128),
            nn.ReLU(True),
            nn.Linear(128, category)
        )

    def forward(self, x):
        out = self.features(x)

        dense = out.view(out.size(0), -1)

        out = self.classifier(dense)
        return out


def test():
    # Load data
    test_datasets = torchvision.datasets.ImageFolder(root=args.path + 'test/',
                                                     transform=transform)

    test_loader = torch.utils.data.DataLoader(dataset=test_datasets,
                                              batch_size=args.batch_size,
                                              shuffle=True)
    print(f"test numbers: {len(test_datasets)}.")
    # Load model
    if torch.cuda.is_available():
        model = torch.load(args.model_path + args.model_name).to(device)
    else:
        model = torch.load(args.model_path + args.model_name, map_location='cpu')
    model.eval()

    correct_prediction = 0.
    total = 0
    for images, labels in test_loader:
        # to GPU
        images = images.to(device)
        labels = labels.to(device)
        # print prediction
        outputs = model(images)
        # equal prediction and acc
        _, predicted = torch.max(outputs.data, 1)
        # val_loader total
        total += labels.size(0)
        # add correct
        correct_prediction += (predicted == labels).sum().item()

    print(f"Acc: {(correct_prediction / total):4f}")


if __name__ == '__main__':
    test()
