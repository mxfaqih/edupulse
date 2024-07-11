import cv2
import mediapipe as mp
import math
import queue
import threading
import requests

def read_student_name():
    try:
        with open('student_id.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def calculate_distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def is_slouching(landmarks):
    try:
        right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        mouth = landmarks[mp_pose.PoseLandmark.MOUTH_LEFT.value]  # Using left side of the mouth

        # Calculate the distances
        right_distance = calculate_distance(right_ear, right_shoulder)
        left_distance = calculate_distance(left_ear, left_shoulder)
        right_mouth_distance = calculate_distance(mouth, right_shoulder)
        left_mouth_distance = calculate_distance(mouth, left_shoulder)
        
        # Define threshold distance for slouching posture
        SLUCHING_THRESHOLD = 0.4  # Adjust according to your needs
        
        return (right_distance < SLUCHING_THRESHOLD and left_distance < SLUCHING_THRESHOLD and
                right_mouth_distance < SLUCHING_THRESHOLD and left_mouth_distance < SLUCHING_THRESHOLD)
    except Exception as e:
        print(f"Error calculating posture: {e}")
    return False

def draw_bounding_box(image, landmarks, name=None, margin=20):
    try:
        h, w, _ = image.shape
        landmark_points = [(int(landmark.x * w), int(landmark.y * h)) for landmark in landmarks]
        x_min = min(point[0] for point in landmark_points)
        y_min = min(point[1] for point in landmark_points) - margin  # Tambahkan margin ke y_min
        x_max = max(point[0] for point in landmark_points)
        y_max = max(point[1] for point in landmark_points) + margin  # Tambahkan margin ke y_max
        
        # Pastikan y_min dan y_max berada dalam batas gambar
        y_min = max(y_min, 0)
        y_max = min(y_max, h)
        
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        if name:
            cv2.putText(image, name, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    except Exception as e:
        print(f"Error drawing bounding box: {e}")


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

print("Number of CUDA-enabled devices:", cv2.cuda.getCudaEnabledDeviceCount())

class VideoCapture:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()

URL = "http://192.168.0.105"
if __name__ == '__main__':
    try:
        response = requests.get(URL + "/control?var=framesize&val={}".format(8))
        response.raise_for_status()  # Raise an error for bad response status
    except requests.exceptions.RequestException as e:
        print(f"Error setting framesize: {e}")
        # Handle the error appropriately, e.g., retry with a different framesize

    cap = VideoCapture(URL + ":81/stream")

    def detect_pose():
        last_student_name = None

        try:
            with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
                while True:
                    image = cap.read()
                    if image is None:
                        continue

                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = pose.process(image)
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    if results.pose_landmarks:
                        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                        student_name = read_student_name()
                        if student_name and student_name != last_student_name:
                            print(f"Student Name read from file: {student_name}")
                            last_student_name = student_name

                        draw_bounding_box(image, results.pose_landmarks.landmark, last_student_name)

                        if is_slouching(results.pose_landmarks.landmark):
                            cv2.putText(image, "Postur terlalu membungkuk", (50, 50), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            print("Postur terlalu membungkuk")
                        else:
                            cv2.putText(image, "Postur baik", (50, 50), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            print("Postur baik")

                    cv2.imshow('MediaPipe Pose', image)
                    if cv2.waitKey(5) & 0xFF == 27:  # Exit if ESC is pressed
                        break
        except Exception as e:
            print(f"Error during pose detection: {e}")
        finally:
            cv2.destroyAllWindows()

    detect_pose()
