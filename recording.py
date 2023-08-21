import cv2
import numpy as np

link = "rtsp://admin:Mavi2022@172.16.16.57:554/cam/realmonitor?channel=1&subtype=1"
camera_urls = [
    link,
    link,
    link,
    link
]

capture_objects = [cv2.VideoCapture(url) for url in camera_urls]

for capture in capture_objects:
    if not capture.isOpened():
        print("Não foi possível abrir uma das câmeras.")
        exit()

fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_width = 2 * int(capture_objects[0].get(cv2.CAP_PROP_FRAME_WIDTH))
output_height = int(capture_objects[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
output_video = cv2.VideoWriter('output_video.avi', fourcc, 30, (output_width, output_height))

while True:
    frames = []
    for capture in capture_objects:
        ret, frame = capture.read()
        if ret:
            frames.append(frame)

    if len(frames) == len(capture_objects):
        concatenated_frame = np.concatenate(frames, axis=1)
        resized_frame = cv2.resize(concatenated_frame, (output_width, output_height))
        output_video.write(resized_frame)
        print('gravando...')
        #cv2.imshow('Concatenated Video', resized_frame)

    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

for capture in capture_objects:
    capture.release()
output_video.release()
#cv2.destroyAllWindows()
