import cv2
import numpy as np
import pyttsx3
from flask import Flask, render_template, Response, request, session, abort, redirect
import poseModule as pm
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
from datetime import date

uri = "mongodb+srv://darshan_pm:ZjvmVr4GWhoYVP0v@cluster0.4jshfu4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('physio')
col = db.get_collection('col')
app = Flask(__name__)

app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "928790256506-gp8gp73nisrvba16920fjv3j18l7hj29.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

neck_count = knee_count = shoulder_count = back_count = elbow_count = 0
neck_time = knee_time = shoulder_time = back_time = elbow_time = 0


def perform_knee(flag):
    # 1 - hamstring_stretch  2 - isometric_leg_hold  3 - partial_squat  4 - sit_to_stand  5 - isometric_knee_flex
    # 6 - step_up_and_down  7 - heel_step_up
    global knee_count, knee_time
    knee_time = time.process_time()
    engine = pyttsx3.init()
    cap = cv2.VideoCapture(0)
    direction = 0
    leg = True
    start = temp = correct = back_straight = left_foot = leg_straight = False

    def draw_points(x1, y1):
        cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (1280, 620))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        knee_angle_right = knee_angle_left = back_angle_parallel_to_floor = back_angle = foot = 0

        if len(lmList) != 0:
            # Right Leg
            if flag == '1':
                knee_angle_right = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (0, 255, 0))
                knee_angle_left = detector.findAngle(img, lmList[23][1:], lmList[25][1:], lmList[27][1:], (0, 255, 0))
                back_angle_parallel_to_floor = detector.findAngle(img, lmList[8][1:], lmList[24][1:],
                                                                  [lmList[24][1] - 50,
                                                                   lmList[24][2]],
                                                                  (255, 0, 0))
                per = np.interp(knee_angle_right if leg else knee_angle_left, (100, 150), (0, 100))
                bar = np.interp(knee_angle_right if leg else knee_angle_left, (100, 150), (450, 100))

                if 265 < back_angle_parallel_to_floor < 275:
                    back_straight = True
                    if 70 < knee_angle_right < 100 and 70 < knee_angle_left < 100:
                        if not start:
                            start = True
                            engine.say("Alternatively Straighten your right and left leg")
                            engine.runAndWait()
            elif flag == '2':
                right_leg_angle_floor = detector.findAngle(img, [lmList[24][1] - 50, lmList[24][2]], lmList[24][1:],
                                                           lmList[28][1:], (0, 255, 0))
                left_leg_angle_floor = detector.findAngle(img, [lmList[23][1] - 50, lmList[23][2]],
                                                          lmList[23][1:], lmList[27][1:], (0, 255, 0))
                back_angle_parallel_to_floor = detector.findAngle(img, lmList[8][1:], lmList[24][1:],
                                                                  [lmList[24][1] + 50,
                                                                   lmList[24][2]], (255, 0, 0))
                knee_angle_right = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (255, 0, 0))
                knee_angle_left = detector.findAngle(img, lmList[23][1:], lmList[25][1:], lmList[27][1:], (255, 0, 0))
                per = np.interp(min(right_leg_angle_floor, 360 - right_leg_angle_floor)
                                if leg else min(left_leg_angle_floor, 360 - left_leg_angle_floor), (2, 15), (0, 100))
                bar = np.interp(min(right_leg_angle_floor, 360 - right_leg_angle_floor)
                                if leg else min(left_leg_angle_floor, 360 - left_leg_angle_floor), (2, 15), (450, 100))
                if back_angle_parallel_to_floor < 10:
                    back_straight = True
                    if 170 < knee_angle_left < 190 and 170 < knee_angle_right < 190:
                        leg_straight = True
                        if (right_leg_angle_floor > 355 or right_leg_angle_floor < 10) and (
                                left_leg_angle_floor < 10 or left_leg_angle_floor > 355):
                            if not start:
                                start = True
                                engine.say(
                                    "Alternatively lift your left and right leg slightly above floor and hold it for 3  "
                                    "seconds")
                                engine.runAndWait()
            elif flag == '3':
                knee_angle = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (0, 255, 0))
                back_angle = detector.findAngle(img, lmList[8][1:], lmList[24][1:], lmList[12][1:], (255, 0, 0))
                per = np.interp(knee_angle, (183, 240), (0, 100))
                bar = np.interp(knee_angle, (183, 240), (450, 100))

                if back_angle > 350 or back_angle < 5:
                    back_straight = True
                    if 175 < knee_angle < 185:
                        if not start:
                            start = True
                            engine.say("Slowly lower your body into semi squat position keeping your back straight")
                            engine.runAndWait()
            elif flag == '4':
                knee_angle = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (0, 255, 0))
                back_angle = detector.findAngle(img, lmList[8][1:], lmList[24][1:], lmList[12][1:], (255, 0, 0))
                per = np.interp(knee_angle, (185, 290), (100, 0))
                bar = np.interp(knee_angle, (185, 290), (100, 450))

                if back_angle > 350 or back_angle < 5:
                    back_straight = True
                    if 280 < knee_angle < 300:
                        if not start:
                            start = True
                            engine.say("Slowly stand and sit by keeping your back straight")
                            engine.runAndWait()
            elif flag == '5':
                knee_angle = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (0, 255, 0))
                per = np.interp(knee_angle, (190, 220), (0, 100))
                bar = np.interp(knee_angle, (190, 220), (450, 100))

                if knee_angle < 190:
                    if not start:
                        start = True
                        engine.say("Flex your straightened legs inwards alternatively crossing your ankles")
                        engine.runAndWait()
            else:
                draw_points(lmList[29][1], lmList[29][2])
                draw_points(lmList[30][1], lmList[30][2])
                draw_points(lmList[31][1], lmList[31][2])
                draw_points(lmList[32][1], lmList[32][2])
                per = np.interp(abs(lmList[31][2] - lmList[32][2]), (70, 5), (0, 100))
                bar = np.interp(abs(lmList[31][2] - lmList[32][2]), (70, 5), (450, 100))

                if flag == '6':
                    if abs(lmList[31][2] - lmList[32][2]) < 10:
                        if not start:
                            start = True
                            engine.say("Alternatively step up and down on the bench")
                            engine.runAndWait()
                else:
                    if abs(lmList[29][2] - lmList[31][2]) < 20 if leg else abs(lmList[30][2] - lmList[32][2]) < 20:
                        foot = True
                        if abs(lmList[31][2] - lmList[32][2]) > 60 and abs(
                                lmList[30][2] - lmList[32][2]) < 20 if leg else \
                                abs(lmList[29][2] - lmList[31][2]) < 20:
                            if not start:
                                start = True
                                engine.say("Rise and touch only your foot index on the bench")
                                engine.runAndWait()

            # Reps count
            color = (255, 0, 255)
            if start:
                if knee_count <= 10 and not temp and time.process_time() - neck_time > 300:
                    engine.say("You are doing too slow, try to do faster")
                    engine.runAndWait()
                    temp = True
                if flag == '1':
                    if back_straight and not 265 < back_angle_parallel_to_floor < 275:
                        engine.say("Keep your back straight")
                        engine.runAndWait()
                        back_straight = False
                        continue
                elif flag == '2':
                    if back_straight and not back_angle_parallel_to_floor < 10:
                        engine.say("Keep your back straight")
                        engine.runAndWait()
                        back_straight = False
                        continue

                    if leg_straight and not (170 < knee_angle_left < 190 and 170 < knee_angle_right < 190):
                        engine.say("Keep your leg straight")
                        engine.runAndWait()
                        leg_straight = False
                        continue
                elif flag == '3' or flag == '4':
                    if back_straight and not (back_angle > 350 or back_angle < 5):
                        engine.say("Keep your back straight")
                        engine.runAndWait()
                        back_straight = False
                        continue
                elif flag == '7':
                    if foot and not abs(lmList[29][2] - lmList[31][2]) < 20 if leg else abs(
                            lmList[30][2] - lmList[32][2]) < 20:
                        engine.say("Keep your other foot still on the bench")
                        engine.runAndWait()
                        foot = False
                        continue

                    if lmList[30][2] > lmList[32][2] + 10 if leg else lmList[29][2] > lmList[31][2] + 10:
                        engine.say("Your heel should be always be higher than your foot index")
                        engine.runAndWait()

                if per == 100:
                    color = (0, 255, 0)
                    if direction == 0:
                        knee_count += 0.25
                        direction = 1
                        if not correct:
                            correct = True
                            engine.say("Perfect")
                            engine.runAndWait()

                if per == 0:
                    color = (0, 255, 0)
                    if direction == 1:
                        knee_count += 0.25
                        direction = 0
                        leg = not leg

            # Draw Bar
            cv2.rectangle(img, (1100, 100), (1150, 450), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (1150, 450), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color, 4)

            # Draw Count
            cv2.putText(img, str(int(knee_count)), (45, 570), cv2.FONT_HERSHEY_PLAIN, 15,
                        (255, 0, 0), 25)
            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
    cap.release()


def perform_back(flag):
    # 1 - knee_to_chest  2 - heel_slide  3 - extension_lunge  4 - stretching_quadriceps
    engine = pyttsx3.init()
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    direction = 0
    start = correct = leg = temp = False
    back_straight = False
    global back_count, back_time
    back_time = time.process_time()

    def draw_points(x1, y1):
        cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (1280, 620))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        back_angle_parallel_to_floor = 0

        if len(lmList) != 0:
            # Right Leg
            if flag == '1':
                hip_angle_right = detector.findAngle(img, lmList[12][1:], lmList[24][1:], lmList[26][1:], (0, 255, 0))
                hip_angle_left = detector.findAngle(img, lmList[11][1:], lmList[23][1:], lmList[25][1:], (0, 255, 0))
                back_angle_parallel_to_floor = detector.findAngle(img, lmList[8][1:], lmList[24][1:],
                                                                  [lmList[24][1] + 50
                                                                   if lmList[8][1] > lmList[24][1] else lmList[24][
                                                                                                            1] - 50,
                                                                   lmList[24][2]], (255, 0, 0))
                per = np.interp(hip_angle_right if leg else hip_angle_left, (220, 300), (0, 100))
                bar = np.interp(hip_angle_right if leg else hip_angle_left, (220, 300), (450, 100))

                if back_angle_parallel_to_floor < 10:
                    back_straight = True

                    if 210 < hip_angle_left < 230 and 210 < hip_angle_right < 230:
                        if not start:
                            start = True
                            engine.say("Alternatively bring your left and right knees")
                            engine.runAndWait()
            elif flag == '2':
                knee_angle_right = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (0, 255, 0))
                knee_angle_left = detector.findAngle(img, lmList[23][1:], lmList[25][1:], lmList[27][1:], (0, 255, 0))
                back_angle_parallel_to_floor = detector.findAngle(img, lmList[8][1:], lmList[24][1:],
                                                                  [lmList[24][1] + 50
                                                                   if lmList[8][1] > lmList[24][1] else lmList[24][
                                                                                                            1] - 50,
                                                                   lmList[24][2]], (255, 0, 0))
                per = np.interp(knee_angle_right if leg else knee_angle_left, (90, 170), (0, 100))
                bar = np.interp(knee_angle_right if leg else knee_angle_left, (90, 170), (450, 100))
                back_angle_parallel_to_floor = min(back_angle_parallel_to_floor, 360 - back_angle_parallel_to_floor)
                if back_angle_parallel_to_floor < 10:
                    back_straight = True
                    if 90 < knee_angle_right < 110 and 90 < knee_angle_left < 100:
                        if not start:
                            start = True
                            engine.say("Alternatively Straighten your left and right leg")
                            engine.runAndWait()
            elif flag == '3':
                draw_points(lmList[27][1], lmList[27][2])
                draw_points(lmList[28][1], lmList[28][2])
                diff = abs(lmList[27][1] - lmList[28][1])
                per = np.interp(diff, (5, 250), (0, 100))
                bar = np.interp(diff, (5, 250), (450, 100))

                if diff < 5:
                    if not start:
                        start = True
                        engine.say("Step your good leg forward with injured leg planted on ground")
                        engine.runAndWait()
            else:
                if lmList[8][1] > lmList[24][1]:
                    knee_angle = detector.findAngle(img, lmList[24][1:], lmList[26][1:], lmList[28][1:], (0, 255, 0))
                else:
                    knee_angle = detector.findAngle(img, lmList[23][1:], lmList[25][1:], lmList[27][1:], (0, 255, 0))
                knee_angle = max(knee_angle, 360 - knee_angle)
                per = np.interp(knee_angle, (220, 300), (0, 100))
                bar = np.interp(knee_angle, (220, 300), (450, 100))
                back_angle_parallel_to_floor = detector.findAngle(img, lmList[8][1:], lmList[24][1:],
                                                                  [lmList[24][1] + 50
                                                                   if lmList[8][1] > lmList[24][1] else lmList[24][
                                                                                                            1] - 50,
                                                                   lmList[24][2]], (255, 0, 0))
                if min(back_angle_parallel_to_floor,
                       360 - back_angle_parallel_to_floor) < 10 and 215 < knee_angle < 235:
                    if not start:
                        start = True
                        engine.say("Keep your injured leg on top pull it towards your buttock")
                        engine.runAndWait()
            # Reps count
            color = (255, 0, 255)

            if start:
                if back_count <= 10 and not temp and time.process_time() - neck_time > 300:
                    engine.say("You are doing too slow, try to do faster")
                    engine.runAndWait()
                    temp = True
                if flag == '1' or flag == '2':
                    if back_straight and not back_angle_parallel_to_floor < 10:
                        engine.say("Keep your back straight")
                        engine.runAndWait()
                        back_straight = False
                        continue

                if per == 100:
                    color = (0, 255, 0)
                    if direction == 0:
                        back_count += 0.25
                        direction = 1
                        if not correct:
                            correct = True
                            engine.say("Perfect")
                            engine.runAndWait()

                if per == 0:
                    color = (0, 255, 0)
                    if direction == 1:
                        back_count += 0.25
                        direction = 0
                        leg = not leg

            # Draw Bar
            cv2.rectangle(img, (1100, 100), (1150, 450), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (1150, 450), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color, 4)

            # Draw Count
            cv2.putText(img, str(int(back_count)), (45, 570), cv2.FONT_HERSHEY_PLAIN, 15,
                        (255, 0, 0), 25)
            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
    cap.release()


def perform_neck(flag):
    engine = pyttsx3.init()
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    direction = count = 0
    start = correct = temp = False
    global neck_count, neck_time
    neck_time = time.process_time()

    def draw_points(x1, y1):
        cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (1280, 620))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        min_first = max_first = min_sec = max_sec = min_third = max_third = 0

        if len(lmList) != 0:
            x1, y1 = lmList[0][1], lmList[0][2]
            x2, y2 = (lmList[11][1] + lmList[12][1]) // 2, (lmList[11][2] + lmList[12][2]) // 2
            # Right Leg
            if flag == '1':
                draw_points(x1, y1)
                draw_points(x2, y2)
                min_first, max_first, min_sec, max_sec, min_third, max_third = (80, 200, 100, 0, 100, 450)
                measured_value = abs(y1 - y2)
                if measured_value > 200:
                    if not start:
                        start = True
                        engine.say("Nod your chin down as far as you can")
                        engine.runAndWait()
            else:
                measured_value = detector.findAngle(img, [x1, y1], [x2, y2], [x2, y2 - 50], (255, 0, 0))
                measured_value = min(measured_value, 360 - measured_value)
                min_first, max_first, min_sec, max_sec, min_third, max_third = (2, 40, 0, 100, 450, 100)

                if measured_value < 10:
                    if not start:
                        start = True
                        if flag == '2':
                            engine.say("Bend your head to the left as far as possible")
                            engine.runAndWait()
                        else:
                            engine.say("Bend your head to the right as far as possible")
                            engine.runAndWait()

            per = np.interp(measured_value, (min_first, max_first), (min_sec, max_sec))
            bar = np.interp(measured_value, (min_first, max_first), (min_third, max_third))

            # Reps count
            color = (255, 0, 255)
            #
            if start:
                if neck_count <= 10 and not temp and time.process_time() - neck_time > 60:
                    engine.say("You are doing too slow, try to do faster")
                    engine.runAndWait()
                    temp = True
                if per == 100:
                    color = (0, 255, 0)
                    if direction == 0:
                        count += 0.5
                        neck_count += 0.5
                        direction = 1
                        if not correct:
                            correct = True
                            engine.say("Perfect")
                            engine.runAndWait()

                if per == 0:
                    color = (0, 255, 0)
                    if direction == 1:
                        count += 0.5
                        neck_count += 0.5
                        direction = 0

            # Draw Bar
            cv2.rectangle(img, (1100, 100), (1150, 450), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (1150, 450), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color, 4)

            # Draw Count

            cv2.putText(img, str(int(count)), (45, 570), cv2.FONT_HERSHEY_PLAIN, 15,
                        (255, 0, 0), 25)
            # Encode the frame as an MPEG video stream
            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()
        # Yield the frame and data in the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
    cap.release()


def perform_shoulder(flag):
    # 1 - Scaption strengthening  2 - Assisted shoulder flexion  3 - Assisted shoulder  4 - Side lying external rotation
    # 5 - AAROM external rotation
    engine = pyttsx3.init()
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    start = correct = same_pace = arm_straight = temp = False
    direction = 0
    global shoulder_count, shoulder_time
    shoulder_time = time.process_time()

    def draw_points(x1, y1):
        cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (1280, 620))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        right_arm_angle = left_arm_angle = right_shoulder_angle = left_shoulder_angle = arm_correct = point = temp_point = arm_angle = 0

        if len(lmList) != 0:
            # Right Leg
            if flag == '1':
                right_shoulder_angle = detector.findAngle(img, lmList[16][1:], lmList[12][1:], lmList[24][1:],
                                                          (0, 255, 0))
                left_shoulder_angle = detector.findAngle(img, lmList[15][1:], lmList[11][1:], lmList[23][1:],
                                                         (0, 255, 0))
                right_arm_angle = detector.findAngle(img, lmList[12][1:], lmList[14][1:], lmList[16][1:], (255, 0, 0))
                left_arm_angle = detector.findAngle(img, lmList[11][1:], lmList[13][1:], lmList[15][1:], (255, 0, 0))
                #
                right_shoulder_angle = min(right_shoulder_angle, 360 - right_shoulder_angle)
                left_shoulder_angle = min(left_shoulder_angle, 360 - left_shoulder_angle)
                print(right_shoulder_angle, left_shoulder_angle)
                per = np.interp(right_shoulder_angle, (30, 110), (0, 100))
                bar = np.interp(right_shoulder_angle, (30, 110), (450, 100))
                # #
                if 160 < right_arm_angle < 200 and 160 < left_arm_angle < 200:
                    arm_straight = True
                    if abs(right_shoulder_angle - left_shoulder_angle) < 25:
                        same_pace = True
                        if right_shoulder_angle < 30 and left_shoulder_angle < 30:
                            if not start:
                                start = True
                                engine.say("Raise your arms by keeping it straight")
                                engine.runAndWait()
            elif flag == '2':
                arm_angle = detector.findAngle(img, lmList[12][1:], lmList[14][1:], lmList[16][1:], (0, 255, 0))
                arm_angle = max(arm_angle, 360 - arm_angle)
                per = np.interp(arm_angle, (200, 250), (100, 0))
                bar = np.interp(arm_angle, (200, 250), (100, 450))
                #
                if 260 < arm_angle < 280:
                    if not start:
                        start = True
                        engine.say("With your fingers of the affected arm, climb the wall")
                        engine.runAndWait()
            elif flag == '3':
                draw_points(lmList[15][1], lmList[15][2])
                draw_points(lmList[16][1], lmList[16][2])
                right_arm_angle = detector.findAngle(img, lmList[12][1:], lmList[14][1:], lmList[16][1:], (255, 0, 0))
                left_arm_angle = detector.findAngle(img, lmList[11][1:], lmList[13][1:], lmList[15][1:], (255, 0, 0))
                per = np.interp(lmList[15][2], (lmList[0][2] - 100, (lmList[24][2] + lmList[23][2]) // 2), (100, 0))
                bar = np.interp(lmList[15][2], (lmList[0][2] - 100, (lmList[24][2] + lmList[23][2]) // 2), (100, 450))
                right_arm_angle = max(right_arm_angle, 360 - right_arm_angle)
                left_arm_angle = max(left_arm_angle, 360 - left_arm_angle)

                if 200 < right_arm_angle < 230 and 200 < left_arm_angle < 230:
                    arm_straight = True
                    if abs(lmList[15][1] - lmList[16][1]) < 100:
                        same_pace = True
                        if not start:
                            start = True
                            engine.say("Raise your arms by keeping it straight")
                            engine.runAndWait()
            elif flag == '4':
                arm_angle = detector.findAngle(img, lmList[12][1:], lmList[14][1:], lmList[16][1:], (0, 255, 0))
                draw_points(lmList[16][1], lmList[16][2])
                point = lmList[16][2]
                temp_point = lmList[14][2]
                arm_angle = min(arm_angle, 360 - arm_angle)
                per = np.interp(point, (temp_point - 120, temp_point + 120), (100, 0))
                bar = np.interp(point, (temp_point - 120, temp_point + 120), (100, 450))
                # #
                if 80 < arm_angle < 100:
                    arm_correct = True
                    if not start:
                        start = True
                        engine.say("With elbow bent to 90 degree, externally rotate your arm to lift the weight up.")
                        engine.runAndWait()
            else:
                draw_points(lmList[14][1], lmList[14][2])
                draw_points(lmList[16][1], lmList[16][2])
                diff = abs(lmList[14][1] - lmList[16][1])
                diff1 = abs(lmList[14][2] - lmList[16][2])
                per = np.interp(diff, (5, 140), (0, 100))
                bar = np.interp(diff, (5, 140), (450, 100))

                if diff < 10 and diff1 < 10:
                    if not start:
                        start = True
                        engine.say("Push the affected arm to the side by pushing the stick with good hand")
                        engine.runAndWait()
            # Reps count
            color = (255, 0, 255)
            #
            if start:
                if shoulder_count <= 10 and not temp and time.process_time() - shoulder_time > 300:
                    engine.say("You are doing too slow, try to do faster")
                    engine.runAndWait()
                    temp = True
                if flag == '1':
                    if arm_straight and not (160 < right_arm_angle < 200 and 160 < left_arm_angle < 200):
                        engine.say("Keep your arms straight")
                        engine.runAndWait()
                        arm_straight = False
                        continue

                    if same_pace and not abs(right_shoulder_angle - left_shoulder_angle) < 25:
                        engine.say("Move your arms at the same pace")
                        engine.runAndWait()
                        same_pace = False
                        continue
                elif flag == '3':
                    if arm_straight and not (200 < right_arm_angle < 230 and 200 < left_arm_angle < 230):
                        engine.say("Don't bend your arms too much")
                        engine.runAndWait()
                        arm_straight = False
                        continue

                    if same_pace and not abs(lmList[15][1] - lmList[16][1]) < 100:
                        engine.say("Clasp your hands together")
                        engine.runAndWait()
                        same_pace = False
                        continue
                elif flag == '4':
                    if arm_correct and abs(point - temp_point) > 50 and not 70 < arm_angle < 110:
                        engine.say("Keep your elbow bent at 90 degree")
                        engine.runAndWait()
                        arm_correct = False
                        continue

                if per == 100:
                    color = (0, 255, 0)
                    if direction == 0:
                        shoulder_count += 0.5
                        direction = 1
                        if not correct:
                            correct = True
                            engine.say("Perfect")
                            engine.runAndWait()

                if per == 0:
                    color = (0, 255, 0)
                    if direction == 1:
                        shoulder_count += 0.5
                        direction = 0

            # Draw Bar
            cv2.rectangle(img, (1100, 100), (1150, 450), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (1150, 450), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color, 4)

            # Draw Count

            cv2.putText(img, str(int(shoulder_count)), (45, 570), cv2.FONT_HERSHEY_PLAIN, 15,
                        (255, 0, 0), 25)

            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()

        # Yield the frame and data in the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
    cap.release()


def perform_elbow(flag):
    engine = pyttsx3.init()
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    direction = count = 0
    start = correct = arm = hand_straight = temp = False
    global elbow_count, elbow_time
    elbow_time = time.process_time()

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (1280, 620))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)

        if len(lmList) != 0:
            # Right Leg
            upper_hand = detector.findAngle(img, lmList[14][1:], lmList[12][1:], [lmList[12][1], lmList[12][2] - 50],
                                            (0, 255, 0))
            arm_angle = detector.findAngle(img, lmList[12][1:], lmList[14][1:], lmList[16][1:], (0, 255, 0))
            upper_hand = min(upper_hand, 360 - upper_hand)
            arm_angle = min(arm_angle, 360 - arm_angle)
            per = np.interp(arm_angle, (60, 150 if flag == '1' else 170), (100, 0))
            bar = np.interp(arm_angle, (60, 150 if flag == '1' else 170), (100, 450))
            if upper_hand < 30 if flag == '1' else 15:
                hand_straight = True
                if arm_angle > 160 if flag == '1' else 170:
                    if not start:
                        start = True
                        engine.say(
                            "By keeping your upper hand in neutral position, lower your arm towards the head" if flag == '1' else "By keeping your upper hand in neutral position, lower your arm towards the head")
                        engine.runAndWait()
            # Reps count
            color = (255, 0, 255)
            #
            if start:
                if elbow_count <= 10 and not temp and time.process_time() - elbow_time > 250:
                    engine.say("You are doing too slow, try to do faster")
                    engine.runAndWait()
                    temp = False
                if hand_straight and not upper_hand < (30 if flag == '1' else 15):
                    engine.say("Keep your upper hand in neutral position")
                    engine.runAndWait()
                    hand_straight = False
                    continue

                if per == 100:
                    color = (0, 255, 0)
                    if direction == 0:
                        count += 0.5
                        elbow_count += count
                        direction = 1
                        if not correct:
                            correct = True
                            engine.say("Perfect")
                            engine.runAndWait()

                if per == 0:
                    color = (0, 255, 0)
                    if direction == 1:
                        count += 0.5
                        elbow_count += count
                        direction = 0
            #
            # # Draw Bar
            cv2.rectangle(img, (1100, 100), (1150, 450), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (1150, 450), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color, 4)

            # Draw Count
            cv2.putText(img, str(int(count)), (45, 570), cv2.FONT_HERSHEY_PLAIN, 15,
                        (255, 0, 0), 25)

            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()

        # Yield the frame and data in the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
    cap.release()


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/')
def index():
    data = col.aggregate([{"$match": {"id": session['google_id']}}, {"$group": {"_id": "$date", "tot_reps": {"$sum": "$reps"}}}, {"$sort": {"_id": 1}}])
    res1 = []
    for d in data:
        res1.append(list(d.values()))
    data = col.aggregate([{"$match": {"id": session['google_id']}}, {"$group": {"_id": "$date", "tot_reps": {"$sum": "$time"}}}, {"$sort": {"_id": 1}}])
    res2 = []
    for d in data:
        res2.append(list(d.values()))
    return render_template('index.html', session=session, reps_data=res1, time_data=res2)


@app.route('/neck')
def neck():
    return render_template('neck.html')


@app.route('/knee')
def knee():
    return render_template('knee.html')


@app.route('/back')
def back():
    return render_template('back.html')


@app.route('/shoulder')
def shoulder():
    return render_template('shoulder.html')


@app.route('/elbow')
def elbow():
    return render_template('elbow.html')


@app.route('/insert')
def insert():
    data = request.args.get('data')
    if "google_id" in session:
        if data == 'neck':
            col.insert_one({'id': session['google_id'], 'reps': int(neck_count), 'time': (time.process_time() - neck_time) // 60, 'date': str(date.today())})
        elif data == 'back':
            col.insert_one({'id': session['google_id'], 'reps': int(back_count), 'time': (time.process_time() - back_time) // 60, 'date': str(date.today())})
        elif data == 'shoulder':
            col.insert_one({'id': session['google_id'], 'reps': int(shoulder_count), 'time': (time.process_time() - shoulder_time) // 60, 'date': str(date.today())})
        elif data == 'knee':
            col.insert_one({'id': session['google_id'], 'reps': int(knee_count), 'time': (time.process_time() - knee_time) // 60, 'date': str(date.today())})
        else:
            col.insert_one({'id': session['google_id'], 'reps': int(elbow_count), 'time': (time.process_time() - elbow_time) // 60, 'date': str(date.today())})
    return redirect("/")


@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    data = request.args.get('data')
    exercise = data[:-1]
    flag = data[-1]
    if exercise == 'neck':
        return Response(perform_neck(flag), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'back':
        return Response(perform_back(flag), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'shoulder':
        return Response(perform_shoulder(flag), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'knee':
        return Response(perform_knee(flag), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(perform_elbow(flag), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
