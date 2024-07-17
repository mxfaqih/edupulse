import cv2
import mediapipe as mp
import math
import json
import time
import os

def read_student_name():
    try:
        with open('student_id.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def calculate_angle(a, b, c):
    angle = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return angle + 360 if angle < 0 else angle

def is_slouching(landmarks):
    try:
        ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
        shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        angle = calculate_angle(ear, shoulder, hip)
        GOOD_POSTURE_THRESHOLD = 160
        return angle < GOOD_POSTURE_THRESHOLD
    except Exception as e:
        print(f"Error calculating posture: {e}")
    return False

def draw_bounding_box(image, landmarks, name=None):
    try:
        h, w, _ = image.shape
        landmark_points = [(int(landmark.x * w), int(landmark.y * h)) for landmark in landmarks]
        x_min = min(point[0] for point in landmark_points)
        y_min = min(point[1] for point in landmark_points)
        x_max = max(point[0] for point in landmark_points)
        y_max = max(point[1] for point in landmark_points)
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        if name:
            cv2.putText(image, name, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    except Exception as e:
        print(f"Error drawing bounding box: {e}")

def is_hand_raised(landmarks):
    try:
        right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

        # Check if either hand is raised above the shoulder
        if right_hand.y < right_shoulder.y or left_hand.y < left_shoulder.y:
            return True
    except Exception as e:
        print(f"Error checking hand raised: {e}")
    return False

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

print("Number of CUDA-enabled devices:", cv2.cuda.getCudaEnabledDeviceCount())

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def detect_pose():
    last_student_name = None
    points = 0  # Initialize points
    hand_raised = False  # Flag to track if hand is raised
    show_points_message = False  # Flag to control message display

    try:
        with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    student_name = read_student_name()
                    if student_name and student_name != last_student_name:
                        print(f"Student Name read from file: {student_name}")
                        with open('student_id.txt', 'w') as f:
                            f.write('')
                        last_student_name = student_name
                        print(f"Student Name: {student_name} read and file cleared.")

                    draw_bounding_box(image, results.pose_landmarks.landmark, last_student_name)

                    if is_slouching(results.pose_landmarks.landmark):
                        cv2.putText(image, "Postur terlalu membungkuk", (50, 100), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        print("Postur terlalu membungkuk")
                        
                        # Simpan status bungkuk dan waktu
                        posture_status = {
                            "status": "slouching",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        with open('posture_status.json', 'w') as json_file:
                            json.dump(posture_status, json_file)
                    else:
                        cv2.putText(image, "Postur baik", (50, 100), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        print("Postur baik")
                    # Hapus file JSON jika postur baik
                        if os.path.exists('posture_status.json'):
                            os.remove('posture_status.json')
                            print("Data postur dihapus karena siswa tegak.")
                    if is_hand_raised(results.pose_landmarks.landmark):
                        if not hand_raised:
                            points += 100
                            hand_raised = True
                            show_points_message = True
                            print(f"Tangan diangkat! Poin: {points}")
                    else:
                        hand_raised = False
                        show_points_message = False

                    if show_points_message:
                        cv2.putText(image, "Tangan diangkat! Poin: " + str(points), (50, 150), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                cv2.imshow('MediaPipe Pose', image)
                if cv2.waitKey(5) & 0xFF == 27:  # Exit if ESC is pressed
                    break
    except Exception as e:
        print(f"Error during pose detection: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

detect_pose()
