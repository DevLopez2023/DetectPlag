from imageai.Detection import VideoObjectDetection
import os
import cv2 
execution_path = os.getcwd()
camera = cv2.VideoCapture(0)
detector = VideoObjectDetection()
# el modelo a testear tipo YOLOv3
detector.setModelTypeAsYOLOv3()
# ruta donde está el modelo entrenado
detector.setModelPath(os.path.join(execution_path, "pretrained-yolov3.h5"))
# guardar modelo
detector.loadModel()


video_path = detector.detectObjectsFromVideo(camera_input=camera,
output_file_path=os.path.join(execution_path, "camera_detected_video"), 
frames_per_second=30, log_progress=True, minimum_percentage_probability=30, detection_timeout=120)
print(video_path)