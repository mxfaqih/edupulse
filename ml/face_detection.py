import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-a740a-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-a740a.appspot.com"
})

bucket = storage.bucket()

def write_student_id(student_name):
    with open('student_id.txt', 'w') as f:
        f.write(f"{student_name}")
    print(f"Name {student_name} written to file.")

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
imgBackground = cv2.imread('Resources/background.png')

# Load mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load encoding file
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

# Initialize variables
modeType = 0
counter = 0
id = -1
imgStudent = []
studentInfo = {}

while True:
    success, img = cap.read()

    # Resize and convert webcam image
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces and encode
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Update background image
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                # Mendapatkan ID siswa yang cocok dengan wajah yang terdeteksi
                id = studentIds[matchIndex]

                if counter == 0:
                    # Mendapatkan informasi siswa dari database Firebase
                    student_ref = db.reference(f'Students/{id}')
                    studentInfo = student_ref.get()

                    # Menampilkan data siswa di terminal
                    print(f"Student ID: {id}")
                    print(f"Name: {studentInfo['name']}")
                    print(f"Class: {studentInfo['class']}")
                    print(f"Email: {studentInfo['email']}")

                    # Tulis ID siswa dan nama ke file
                    write_student_id(studentInfo['name'])

                    # Update counter and modeType for display purposes
                    counter = 1
                    modeType = 1

                    # Indicate login on the image
                    cvzone.putTextRect(imgBackground, "Login Successful", (100, 100), scale=2, thickness=2, colorR=(0, 255, 0))

            if counter != 0:
                if counter == 1:
                    # Get student image from Firebase storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    if blob is not None:
                        array = np.frombuffer(blob.download_as_string(), np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    else:
                        print(f"Error: Image for student ID {id} not found in Firebase Storage.")
                        imgStudent = np.zeros((216, 216, 3), np.uint8)  # Placeholder image if not found

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        cvzone.putTextRect(imgBackground, f'Class: {studentInfo["class"]}', (1006, 550), scale=1, thickness=1, colorR=(255, 255, 255))
                        cvzone.putTextRect(imgBackground, f'ID: {id}', (1006, 493), scale=1, thickness=1, colorR=(255, 255, 255))
                        cvzone.putTextRect(imgBackground, f'Email: {studentInfo["email"]}', (910, 625), scale=1, thickness=1, colorR=(100, 100, 100))

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cvzone.putTextRect(imgBackground, studentInfo['name'], (808 + offset, 445), scale=1, thickness=1, colorR=(50, 50, 50))

                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = {}
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # Draw face landmarks
    for faceLoc in faceCurFrame:
        top, right, bottom, left = [v * 4 for v in faceLoc]  # Scale back up since we resized to 0.25
        cv2.rectangle(imgBackground, (left, top), (right, bottom), (0, 255, 0), 2)

        # Draw landmarks
        landmarks = face_recognition.face_landmarks(imgS)
        for landmark in landmarks:
            for key, points in landmark.items():
                for point in points:
                    point = tuple([v * 4 for v in point])  # Scale back up
                    cv2.circle(imgBackground, point, 2, (0, 0, 255), -1)

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
