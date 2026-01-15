import cv2 as cv

# 손가락 마디 연결 순서
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),    # 엄지
    (0, 5), (5, 6), (6, 7), (7, 8),    # 검지
    (9, 10), (10, 11), (11, 12),       # 중지
    (13, 14), (14, 15), (15, 16),      # 약지
    (17, 18), (18, 19), (19, 20),      # 소지
    (5, 9), (9, 13), (13, 17), (0, 17) # 손바닥
]


def draw_manual(image, detection_result):
    if detection_result is None or not detection_result.multi_hand_landmarks:
        return image

    h, w, _ = image.shape

    for hand_landmarks in detection_result.multi_hand_landmarks:
        points = []

        for lm in hand_landmarks.landmark:
            cx, cy = int(lm.x * w), int(lm.y * h)
            points.append((cx, cy))

        for start_idx, end_idx in HAND_CONNECTIONS:
            cv.line(image, points[start_idx], points[end_idx], (0, 255, 0), 2)

        for pt in points:
            cv.circle(image, pt, 5, (0, 0, 255), cv.FILLED)

    return image



def print_RSP_result(image, rps_result):
    if rps_result is None:
        text = ""
    else:
        text_list = ["Rock", "Paper", "Scissors"]
        text = text_list[rps_result]

    cv.putText(
        image,
        text,
        (50, 100),
        cv.FONT_HERSHEY_SIMPLEX,
        2,
        (255, 255, 255),
        3
    )

    return image


def RockPaperScissors(image, detection_result):
    if detection_result is None or not detection_result.multi_hand_landmarks:
        rps_result = None
        image = print_RSP_result(image, rps_result)
        return image, rps_result

    # 첫 번째 손
    hand = detection_result.multi_hand_landmarks[0]

    fingers = []

    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    for tip, pip in zip(tips, pips):
        if hand.landmark[tip].y < hand.landmark[pip].y or hand.landmark[tip].x < hand.landmark[pip].x:
            fingers.append(1)  # 펴짐
        else:
            fingers.append(0)  # 접힘

    count = sum(fingers)

    if count == 0:
        rps_result = 0  # Rock
    elif count == 4:
        rps_result = 1  # Paper
    elif count == 2:
        rps_result = 2  # Scissors
    else:
        rps_result = None

    image = print_RSP_result(image, rps_result)
    return image, rps_result

