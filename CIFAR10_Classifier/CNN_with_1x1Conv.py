import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
from torchvision import datasets, transforms
import time
import os
import torch.backends.cudnn as cudnn

os.environ["CUDA_VISIBLE_DEVICES"] = '0'
start_time = time.time()
batch_size = 256
learning_rate = 0.1

transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    #transforms.RandomAffine(degrees=[-35, 30], shear=[-15, 15], scale=[1, 1.3]),
    #transforms.RandomAffine(degrees=[-35, 30], shear=[-15, 15], scale=[1, 1.3]),
    transforms.RandomHorizontalFlip(),    
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.4914, 0.4824, 0.4467),
                             std=(0.2471, 0.2436, 0.2616))
    #transforms.Normalize(mean=(0.4914, 0.4822, 0.4465),
    #                         std=(0.2023, 0.1994, 0.2010))
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.4914, 0.4824, 0.4467),
                             std=(0.2471, 0.2436, 0.2616))
    #transforms.Normalize(mean=(0.4914, 0.4822, 0.4465),
    #                         std=(0.2023, 0.1994, 0.2010))

])


train_dataset = datasets.CIFAR10(root='/content/pytorch/data/cifar10/',
                                 train=True,
                                 transform=transform_train,
                                 download=True)

test_dataset = datasets.CIFAR10(root='/content/pytorch/data/cifar10/',
                                train=False,
                                transform=transform_test)

train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                           batch_size=batch_size,
                                           shuffle=True,
                                           num_workers=4)

test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
                                          batch_size=batch_size,
                                          shuffle=False,
                                          num_workers=4)
accuracies = []


def train(epoch):
    model.train()
    train_loss = 0
    total = 0
    correct = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        if torch.cuda.is_available():
            data, target = Variable(data.cuda()), Variable(target.cuda())
        else:
            data, target = Variable(data), Variable(target)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        train_loss += loss.data[0]
        _, predicted = torch.max(output.data, 1)
        # torch.max() : (maximum value, index of maximum value) return.
        # 1 :  row마다 max계산 (즉, row는 10개의 class를 의미)
        # 0 : column마다 max 계산
        total += target.size(0)
        correct += predicted.eq(target.data).cpu().sum()
    print('Epoch: {} | Batch_idx: {} |  Loss: ({:.4f}) | Acc: ({:.2f}%) ({}/{})'
            .format(epoch, batch_idx, train_loss/(batch_idx+1), 100.*correct/total, correct, total))


def test(): 
    model.eval()
    test_loss = 0
    correct = 0
    total = 0
    for batch_idx, (data, target) in enumerate(test_loader):
        if torch.cuda.is_available():
            data, target = Variable(data.cuda()), Variable(target.cuda())
        else:
            data, target = Variable(data), Variable(target)

        outputs = model(data)
        loss = criterion(outputs, target)

        test_loss += loss.data[0]
        _, predicted = torch.max(outputs.data, 1)
        total += target.size(0)
        correct += predicted.eq(target.data).cpu().sum()
    print('# TEST : Loss: ({:.4f}) | Acc: ({:.2f}%) ({}/{})'
      .format(test_loss/(batch_idx+1), 100.*correct/total, correct, total))
    test_accuracy = 100.*correct/total

    highest_accuracy = 0
    for index in range(len(accuracies)):
        if highest_accuracy < accuracies[index]['accuracy']:
            highest_accuracy = accuracies[index]['accuracy']

    if highest_accuracy < test_accuracy:
        accuracies.append({'epoch' : epoch, 'accuracy' : test_accuracy})



class only_cnn(nn.Module):
    def __init__(self, num_classes=10):
        super(only_cnn, self).__init__()
        self.features = nn.Sequential(
            # conv layer 1, 2
            nn.Conv2d(3, 64, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(64),
            nn.ReLU(True),

	    # 1x1 conv for dimension reduction
            nn.Conv2d(64, 32, kernel_size=1, padding=1, stride=1),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            
            # conv layer 3, 4
            nn.Conv2d(32, 128, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

	    # 1x1 conv for dimension reduction
            nn.Conv2d(128, 64, kernel_size=1, padding=1, stride=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            
	    # conv layer 5, 6
            nn.Conv2d(64, 256, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(256),
            nn.ReLU(True),

	    # 1x1 conv for dimension reduction
            nn.Conv2d(256, 128, kernel_size=1, padding=1, stride=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            
            # conv layer 7, 8
            nn.Conv2d(128, 512, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(512),
            nn.ReLU(True),

	    # 1x1 conv for dimension reduction
            nn.Conv2d(512, 256, kernel_size=1, padding=1, stride=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            
            nn.AvgPool2d(2),
        )
        # fc 9
        self.classifier = nn.Linear(2304, num_classes)

    ######## Total 9 Layers #########
    def forward(self, x):
        x = self.features(x)
        #print(x.size())
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x



###################################################### Runner
model = only_cnn()
optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=1e-5)
#optimizer = optim.Adadelta(model.parameters(), lr=learning_rate, weight_decay=1e-5)
criterion = nn.CrossEntropyLoss().cuda()

if torch.cuda.device_count() > 0:
    print("USE", torch.cuda.device_count(), "GPUs!")
    model = nn.DataParallel(model)
    cudnn.benchmark = True
else:
    print("USE ONLY CPU!")

if torch.cuda.is_available():
    model.cuda()

for epoch in range(0, 200):
    if epoch < 10:
        learning_rate = learning_rate * 30
    elif epoch < 20:
        learning_rate = learning_rate * 20
    elif epoch < 30:
        learning_rate = learning_rate * 10
    elif epoch < 40:
        learning_rate = learning_rate * 5
    elif epoch < 50:
        learning_rate = learning_rate
    elif epoch < 100:
        learning_rate = learning_rate * 0.1
    elif epoch < 140:
        learning_rate = learning_rate * 0.01
    elif epoch < 180:
        learning_rate = learning_rate * 0.001     
    else:
        learning_rate = learning_rate * 0.0001
    for param_group in optimizer.param_groups:
        param_group['learning_rate'] = learning_rate
 
    train(epoch)
    test()
highest_accuracy = 0
epoch = 0
for index in range(len(accuracies)):
    if highest_accuracy < accuracies[index]['accuracy']:
        highest_accuracy = accuracies[index]['accuracy']
        epoch = accuracies[index]['epoch']
print("###### Best accuracy #####")
print("epoch : ", epoch, "  highest accuracy : ", highest_accuracy)
print("##########################")
now = time.gmtime(time.time() - start_time)
print('{} hours {} mins {} secs for training'.format(now.tm_hour, now.tm_min, now.tm_sec))
