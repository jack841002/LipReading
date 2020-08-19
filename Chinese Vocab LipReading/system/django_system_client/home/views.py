from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
import cv2
import sys
import time
import socket
import numpy as np
import dlib
import imutils
from imutils.face_utils import *
import datetime
from glob import glob
import os
from PIL import Image
import paramiko

# 取得預設的臉部偵測器
detector = dlib.get_frontal_face_detector()
# 根據shape_predictor方法載入68個特徵點模型，此方法為人臉表情識別的偵測器
landmark_predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

#伺服器資訊
HOST = '140.116.39.114'
PORT = 8002

def videotolip(file_path, content, theTime):
    capture = cv2.VideoCapture(file_path)
    folder_name = "./AddData/"+str(theTime)
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
        if not os.path.isdir(folder_name+"/lip"):
            os.mkdir(folder_name+"/lip")
    with open(folder_name + "/text.txt" , 'w', encoding='utf-8') as txt_data:
        txt_data.write(content)
#         txt_data.write('\n')
    count = 1
    while(capture.isOpened()):
        ret, frame = capture.read()
#         time.sleep(0.005)
        if ret == True:
            face_rects = detector(frame, 1)

            for i, d in enumerate(face_rects):
                x1 = d.left()
                y1 = d.top()
                x2 = d.right()
                y2 = d.bottom()

                if i == 0:
                    shape = landmark_predictor(frame, d)
                    # 將特徵點轉為numpy (68,2)
                    shape = shape_to_np(shape)

                    # loop over the face parts individually
                    for(name, (i,j)) in FACIAL_LANDMARKS_IDXS.items():
                        if i==48 and j==68:
                            clone = frame.copy()
                            # extract the ROI of the face region as a separate image
                            # x，y是矩阵左上点的坐标，w，h是矩阵的宽和高
                            (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
                            y = y-10
                            x = x-10
                #             print(x, y, w, h)
                            roi = frame[y : y + h + 20, x: x + w + 20]
                            roi = imutils.resize(roi, width = 100, inter = cv2.INTER_CUBIC)
                            cv2.imwrite(folder_name+"/lip/"+str(count)+".jpg", roi)
                            count = count + 1
        else:
            break

def LiptoNumpy(theTime):
    maxlen = 77
    image_list = []
    filesPath = "./AddData/" + str(theTime) + "/lip/*"
    lists1 = glob(filesPath)
    lists1.sort()
    lists1 = lists1[10:-3]         # 去除前10張和後3張
    if len(lists1) <= maxlen:
        for img_path in lists1:
            image = Image.open(img_path)

            image = image.resize((100,50), Image.BILINEAR)
            np_image = np.array(image)
            image_list.append(np_image)

        if len(lists1) != maxlen:
            zeros = np.zeros((maxlen-len(lists1),50,100,3)).astype(int)
            image_list = np.append(image_list, zeros, axis=0)
#             image_list = np.concatenate((image_list, zeros), axis=0)
            image_list = image_list.tolist()
    # save npy file
    np.save('./AddData/' + str(theTime) + "/np", np.array(image_list))

def transferFile(theTime, content):
    scp = paramiko.Transport(("140.116.39.114", 22))
    scp.connect(username="eagleuser", password="nckulina41504eagleepson")
    sftp = paramiko.SFTPClient.from_transport(scp)

    remote_path = "/home/eagleuser/Users/dragon/Chinese_vocab_LipReading/system_data/transfer_data/" + str(theTime)
    try:
        sftp.chdir(remote_path)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_path)  # Create remote_path
        sftp.chdir(remote_path)

    localpath = "D:\\jupyter\\Chinese Vocab LipReading\\system\\django_system_client\\AddData\\" + theTime + "\\np.npy"
    filepath = "/home/eagleuser/Users/dragon/Chinese_vocab_LipReading/system_data/transfer_data/" + theTime + "/np.npy"
    sftp.put(localpath, filepath)  # upload 檔案
    localpath1 = "D:\\jupyter\\Chinese Vocab LipReading\\system\\django_system_client\\AddData\\" + theTime + "\\text.txt"
    filepath1 = "/home/eagleuser/Users/dragon/Chinese_vocab_LipReading/system_data/transfer_data/" + theTime + "/text.txt"
    sftp.put(localpath1, filepath1)  # upload 檔案

    sftp.close()
    scp.close()

def PredictResult(file_path):
    capture = cv2.VideoCapture(file_path)
    theTime = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
    theTime = time.mktime(time.strptime(theTime, "%a %b %d %H:%M:%S %Y"))
    folder_name = "./PredictData/" + str(theTime)
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
        if not os.path.isdir(folder_name + "/lip"):
            os.mkdir(folder_name + "/lip")

    count = 1
    while (capture.isOpened()):
        ret, frame = capture.read()
        #         time.sleep(0.005)
        if ret == True:
            face_rects = detector(frame, 1)

            for i, d in enumerate(face_rects):
                x1 = d.left()
                y1 = d.top()
                x2 = d.right()
                y2 = d.bottom()

                if i == 0:
                    shape = landmark_predictor(frame, d)
                    # 將特徵點轉為numpy (68,2)
                    shape = shape_to_np(shape)

                    # loop over the face parts individually
                    for (name, (i, j)) in FACIAL_LANDMARKS_IDXS.items():
                        if i == 48 and j == 68:
                            clone = frame.copy()
                            # extract the ROI of the face region as a separate image
                            # x，y是矩阵左上点的坐标，w，h是矩阵的宽和高
                            (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
                            y = y - 10
                            x = x - 10
                            #             print(x, y, w, h)
                            roi = frame[y: y + h + 20, x: x + w + 20]
                            roi = imutils.resize(roi, width=100, inter=cv2.INTER_CUBIC)
                            cv2.imwrite(folder_name + "/lip/" + str(count) + ".jpg", roi)
                            count = count + 1
        else:
            break

    maxlen = 77
    # image_list = []
    filesPath = "./PredictData/" + str(theTime) + "/lip/*"
    lists1 = glob(filesPath)
    lists1.sort()
    lists1 = lists1[24:-14]  # 去除前10張和後3張

    num = 0
    split = 80  # 決定多少個frame作切割
    for i in range(0, len(lists1), split):
        lists2 = lists1[i:i + split]
        image_list = []
        num = num + 1
        if len(lists2) <= maxlen:
            for img_path in lists2:
                image = Image.open(img_path)

                image = image.resize((100, 50), Image.BILINEAR)
                np_image = np.array(image)
                image_list.append(np_image)

            if len(lists2) != maxlen:
                zeros = np.zeros((maxlen - len(lists2), 50, 100, 3)).astype(int)
                image_list = np.append(image_list, zeros, axis=0)
                #             image_list = np.concatenate((image_list, zeros), axis=0)
                image_list = image_list.tolist()
        # save npy file
        np.save('./PredictData/' + str(theTime) + "/" + str(num), np.array(image_list))

        scp = paramiko.Transport(("140.116.39.114", 22))
        scp.connect(username="eagleuser", password="nckulina41504eagleepson")
        sftp = paramiko.SFTPClient.from_transport(scp)

        remote_path = "/home/eagleuser/Users/dragon/Chinese_vocab_LipReading/system_data/predict_data/" + str(theTime)
        try:
            sftp.chdir(remote_path)  # Test if remote_path exists
        except IOError:
            sftp.mkdir(remote_path)  # Create remote_path
            sftp.chdir(remote_path)

        localpath = "D:\\jupyter\\Chinese Vocab LipReading\\system\\django_system_client\\PredictData\\" + str(theTime) + "\\" + str(num) + ".npy"
        filepath = "/home/eagleuser/Users/dragon/Chinese_vocab_LipReading/system_data/predict_data/" + str(
            theTime) + "/" + str(num) + ".npy"
        sftp.put(localpath, filepath)  # upload 檔案

        sftp.close()
        scp.close()
    return (str(theTime))

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

# Create your views here.
def home(request):
    return render(request, 'page.html')

def addFunction(request):                                     # add
    addFile = request.FILES.get('file')
    print(addFile)
    addText = request.POST.get('text')
    print(addText)

    file_path = addFile.temporary_file_path()
    print(file_path)

    theTime = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
    theTime = time.mktime(time.strptime(theTime, "%a %b %d %H:%M:%S %Y"))
    videotolip(file_path, addText, str(theTime))
    LiptoNumpy(str(theTime))
    transferFile(str(theTime), str(addText))

    return_object = {
        'result': "新增資料成功"
    }
    return HttpResponse(json.dumps(return_object, cls=MyEncoder), content_type='application/json')

def trainFunction(request):                                   # train
    addTrain = request.POST.get('train')
    print(addTrain)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 創建socket
    s.connect((HOST, PORT))
    mode = "train"
    s.send(mode.encode())

    msg = str(s.recv(1024), encoding='utf-8')
    s.close()

    return_object = {
        'result': msg
    }
    return HttpResponse(json.dumps(return_object, cls=MyEncoder), content_type='application/json')


def predictFunction(request):
    predictFile = request.FILES.get('file')
    print(predictFile)
    file_path = predictFile.temporary_file_path()
    print(file_path)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 創建socket
    s.connect((HOST, PORT))
    mode = "predict"
    s.send(mode.encode())

    theTime = PredictResult(file_path)
    print("theTime: " + theTime)
    s.send(theTime.encode())

    result = str(s.recv(1024), encoding='utf-8')
    s.close()
    return_object = {
        'result': result
    }
    return HttpResponse(json.dumps(return_object, cls=MyEncoder), content_type='application/json')
