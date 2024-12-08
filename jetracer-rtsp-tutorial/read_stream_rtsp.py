import cv2

rtsp_url = "rtsp://192.168.1.166:8554/test"
cap = cv2.VideoCapture(rtsp_url)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("RTSP Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


