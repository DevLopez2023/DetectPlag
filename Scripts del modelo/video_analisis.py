from imageai.Detection.Custom import CustomVideoObjectDetection
import os
execution_path = os.getcwd()

# Tratamiento en video
video_detector = CustomVideoObjectDetection()
video_detector.setModelTypeAsYOLOv3()
# ruta donde está el modelo entrenado
video_detector.setModelPath("detection_model-ex-045--loss-0028.859.h5") 
# ruta donde está el archivo de configuración json
video_detector.setJsonPath("detection_config.json")
video_detector.loadModel()
video_detector.detectObjectsFromVideo(input_file_path="mosca.mp4",output_file_path=os.path.join(execution_path, "mosca-detected"),frames_per_second=40,minimum_percentage_probability=40,log_progress=True)