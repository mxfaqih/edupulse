import cv2
import mediapipe as mp
import math

def calculate_angle(a, b, c):
    angle = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return angle + 360 if angle < 0 else angle

def is_slouching(landmarks):
    ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
    shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    angle = calculate_angle(ear, shoulder, hip)
    
    GOOD_POSTURE_THRESHOLD = 170
    
    return angle < GOOD_POSTURE_THRESHOLD

def is_hand_raised(landmarks, side='left'):
    if side == 'left':
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    else:
        shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    return wrist.y < shoulder.y and wrist.y < hip.y

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Uncomment the next line if you want to check CUDA support
# print(cv2.cuda.getCudaEnabledDeviceCount())

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def detect_pose():
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        hand_raise_count = 0
        previous_hand_state = False

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                current_hand_state = is_hand_raised(results.pose_landmarks.landmark, 'right')
                
                if current_hand_state and not previous_hand_state:
                    hand_raise_count += 1
                
                previous_hand_state = current_hand_state

                cv2.putText(image, f"Hand raises: {hand_raise_count}", (50, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                if is_slouching(results.pose_landmarks.landmark):
                    cv2.putText(image, "Postur terlalu membungkuk", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    print("Postur terlalu membungkuk")
                else:
                    cv2.putText(image, "Postur baik", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('MediaPipe Pose', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_pose()
