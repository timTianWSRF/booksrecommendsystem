import cv2
import pyttsx3
import face_recognition
import numpy as np
from django.shortcuts import render
from .models import Name_Picture
from django.http import HttpResponse, HttpResponseRedirect
import os
import redis
import random

red = redis.Redis(host='localhost', port=6379, db=1)


def camera(request):
    face_cascade = cv2.CascadeClassifier(
        "C:\\Users\\TIM\\cascades\\haarcascade_frontalface_default.xml")
    red = redis.StrictRedis(host='localhost', port=6379, db=1)

    camera = cv2.VideoCapture(0)
    while True:
        # 参数ret 为True 或者False,代表有没有读取到图片
        # 第二个参数frame表示截取到一帧的图片
        ret, frame = camera.read()
        # frame = cv2.imread(r'C:\Users\TIM\c.jpg')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, 1.5, 3)
        for (x, y, w, h) in face:
            # 绘制矩形框，颜色值的顺序为BGR，即矩形的颜色为蓝色
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
            # 在检测到的人脸区域内检测眼睛
            # eyes = eye_cascade.detectMultiScale(roi_gray)
            # for (ex, ey, ew, eh) in eyes:
            # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        cv2.imshow('camera', frame)

        k = cv2.waitKey(1)
        if k == ord('s'):
            rgb_frame = frame[:, :, ::-1]

            # 获取画面中的所有人脸位置及人脸特征码

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # 对获取的每个人脸进行识别比对
            flag = False
            for (top, right, bottom, left), face_encoding in list(zip(face_locations, face_encodings)):
                print(face_encoding)
                print(face_encoding.shape)

                # 对其中一个人脸的比对结果（可能比对中人脸库中多个人脸）
                # keys = red.keys()
                # for key in keys:
                #     image = face_recognition.load_image_file(red.get(key))
                #     face_encoding = face_recognition.face_encodings(image)[0]
                #     namelist = []
                #     namelist.append(key)
                faces = red.keys()
                for face in faces:
                    image = face_recognition.load_image_file(red.get(face))
                    face_encodings = face_recognition.face_encodings(image)[0]
                    print(np.array(face_encodings).shape)
                    print([np.array(face_encodings)])
                    matches = face_recognition.compare_faces([np.array(list(face_encodings))],
                                                             face_encoding, tolerance=0.40)
                    print(matches)
                    if True in matches:
                        engine = pyttsx3.init()
                        engine.say('你好,{}'.format(face.decode('utf-8')))
                        camera.release()
                        return render(request, 'backGround.html')
                    else:
                        engine = pyttsx3.init()
                        engine.say('无法识别')
                        camera.release()
                        return render(request, 'login.html')
        if k == ord('q'):
            break


def index(request):
    return render(request, 'index.html')


def upload_file(request):

    if request.method == "POST":    # 请求方法为POST时，进行处理
        myFile = request.FILES.get("myfile", None)    # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            return HttpResponse("no files for upload!")
        destination = open(os.path.join('facePhoto', myFile.name), 'wb+')    # 打开特定的文件进行二进制的写操作

        for chunk in myFile.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()

        pictureLocation = os.path.join('facePhoto', myFile.name)
        data = Name_Picture()
        data.picture = pictureLocation
        username = request.POST['username']
        data.names = username
        data.save()

        red.set(username, pictureLocation)

        return HttpResponseRedirect('/index/')

    elif request.method == 'GET':
        return render(request, 'index.html')


def func(facesName):
    facesName = list(set(facesName))
    facesResult = random.sample(facesName, 3)
    for x in facesResult:
        facesName.remove(x)
    facesResult2 = []
    for face in facesResult:
        facesResult2.append(str(face, 'utf-8'))
    routes = []
    for face in facesResult:
        routes.append(red.get(face).decode('utf-8'))
    return dict(zip(facesResult2, routes))