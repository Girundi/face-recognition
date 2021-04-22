from __future__ import print_function
from PIL import Image
from torch.autograd import Variable
import transforms as transforms
import time
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
import torch
import face_recognition
from face_finder import FaceFinder


class_labels = ['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL']

cfg = {
    'VGG11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
    'VGG19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
}


class Net(nn.Module):

    def __init__(self, vgg_name):
        super(Net, self).__init__()
        self.features = self._make_layers(cfg[vgg_name])
        self.classifier = nn.Linear(512, 7)

    def forward(self, x):
        out = self.features(x)
        out = out.view(out.size(0), -1)
        out = F.dropout(out, p=0.5, training=self.training)
        out = self.classifier(out)
        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3
        for x in cfg:
            if x == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                layers += [nn.Conv2d(in_channels, x, kernel_size=3, padding=1),
                           nn.BatchNorm2d(x),
                           nn.ReLU(inplace=True)]
                in_channels = x
        layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)


cut_size = 44
transform_test = transforms.Compose([
    transforms.TenCrop(cut_size),
    transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
])


class Emanalisis:
    """ main class for usage in emotion recognition
    input mode - int, determines where class takes its data.
        0 - from default webcam of device
        1 - from ip camera
        2 - from video
    output mode - int, determines how output would look.
        0 - classical opencv display, augments original video
        1 - makes separate graph of emotions count with matplotlib. if record_video is True, will record only graph
        2 - graph on black background with all info. Needed for nvr
    record_video - bool, if True, will record output on mp4.
    email_to_share - list of strings/string, email(s) to share sheet. If there is none, sheets will be barely reachable
    channel - int/string, sourse for input data. If input_mode is 0, it should be 0, if input_mode is 1, it'd be ip
        address of camera, else it is name of mp4 video file
    on_gpu - bool, if true, will use gpu for detection and classification. NEVER USE IF THERE IS NO GPU DEVICE.
    display - bool, if true, will show output on screen.
    only_headcount - bool, if true, will disable classification and graph drawing
    send_to_nvr - bool, if true, will send recorded video into miem nvr"""
    def __init__(self, on_gpu=False, path_to_classifier=None, finder=None):
        self.on_gpu = on_gpu
        # from classifier by Sizykh Ivan

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # PATH = "./check_points_4/net_714.pth"
        if self.on_gpu:
            self.classifier = Net('VGG19').to(self.device)
            self.classifier.load_state_dict(torch.load(path_to_classifier)['net'])
            self.classifier.cuda()
            self.classifier.eval()

        else:
            self.classifier = Net('VGG19')
            self.classifier.load_state_dict(torch.load(path_to_classifier, map_location=torch.device('cpu'))['net'])
            # self.classifier.cuda()
            self.classifier.eval()

        self.finder = finder

    def classify_face(self, crop_img):
        tic = time.time()
        dim = (48, 48)
        resized = cv2.resize(crop_img, dim)
        roi_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        img = roi_gray[:, :, np.newaxis]

        img = np.concatenate((img, img, img), axis=2)
        img = Image.fromarray(img)
        inputs = transform_test(img)

        ncrops, c, h, w = np.shape(inputs)

        inputs = inputs.view(-1, c, h, w)
        if self.on_gpu:
            inputs = inputs.cuda()
        inputs = Variable(inputs, volatile=True)
        outputs = self.classifier(inputs)
        outputs_avg = outputs.view(ncrops, -1).mean(0)
        score = F.softmax(outputs_avg)
        _, predicted = torch.max(outputs_avg.data, 0)
        emcount = np.zeros(7)
        emcount[predicted] += 1
        # print(str(time.time() - tic) + " to classify")
        return emcount

    def classify_emotions(self, img, face_locations=None):

        if face_locations is None:
            if self.finder is None:
                face_locations = face_recognition.face_locations(img)
            elif isinstance(self.finder, FaceFinder):
                face_locations = self.finder.detect_faces(img)

        if len(face_locations) == 0:
            return []

        em_arr = []

        for (top, right, bottom, left) in face_locations:
            # if img[top:bottom, left:right].sum() != 0:
            if img[top:bottom, left:right].size != 0:
                em_arr.append(self.classify_face(img[top:bottom, left:right]))

        return [(em, loc) for em, loc in zip(em_arr, face_locations)]
