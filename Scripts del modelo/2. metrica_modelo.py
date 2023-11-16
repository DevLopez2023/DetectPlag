
''' SEGUNDO PASO '''

from imageai.Detection.Custom import DetectionModelTrainer 
entrenamiento = DetectionModelTrainer()
entrenamiento.setModelTypeAsYOLOv3()
entrenamiento.setDataDirectory(data_directory="mosca")
metrics = entrenamiento.evaluateModel(model_path="mosca/models", 
json_path="mosca/json/detection_config.json", 
iou_threshold=0.5, object_threshold=0.3, 
nms_threshold=0.5)
print(metrics)

