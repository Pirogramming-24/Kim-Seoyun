import cv2 as cv
import mediapipe as mp
from visualization import draw_manual, RockPaperScissors  # 네가 만든 함수

def cv2_stream():
    cap = cv.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv.flip(frame, 1)
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        detection_result = hands.process(rgb)

        frame = draw_manual(frame, detection_result)
        frame, _ = RockPaperScissors(frame, detection_result)

        cv.imshow("Hand RPS", frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    cv2_stream()
