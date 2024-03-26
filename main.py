import cv2
import pickle
import cvzone
import numpy as np
from datetime import datetime

# 60 minutes = 1 hour
ONE_HOUR = 60

# Khởi tạo thời gian check-in là hôm nay, 13:00
check_in_time = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)

# Lấy thời gian hiện tại
current_time = datetime.now()

# Video feed
cap = cv2.VideoCapture('carPark.mp4')
cap.set(3, 640)
cap.set(4, 480)

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48

check_time = {}

for pos in posList:
    item = str((pos[0], pos[1]))
    if ((pos[0] == 406 and pos[1] == 89)
            or (pos[0] == 514 and pos[1] == 187)
            or (pos[0] == 751 and pos[1] == 327)):
        check_time[item] = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        check_time[item] = check_in_time


def checkParkingSpace(imgPro):
    spaceCounter = 0
    text = ""

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)
        item = str((pos[0], pos[1]))

        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            text = "Yes"
        else:
            flag = False
            print(f'Time check in of {item} is {check_time[item]}')

            # Tính khoảng thời gian giữa thời gian hiện tại và thời gian check-in
            time_difference = current_time - check_time[item]

            # Chuyển đổi khoảng thời gian thành phút
            total_minutes = time_difference.total_seconds() // 60

            # CHECK IN TIME 60 minute
            if total_minutes > ONE_HOUR:
                flag = True

            text = "Overtime" if flag else "No"
            color = (0, 0, 255) if flag else (139, 0, 139)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, text, (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))


out = cv2.VideoWriter('test_model.mov', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 20.0, (int(cap.get(3)), int(cap.get(4))))
while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    out.write(img)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
print("DONE")
cv2.destroyAllWindows()
