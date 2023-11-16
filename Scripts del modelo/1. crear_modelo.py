
''' PRIMER PASO '''

from imageai.Detection.Custom import DetectionModelTrainer 
entrenamiento = DetectionModelTrainer()
entrenamiento.setModelTypeAsYOLOv3()
entrenamiento.setDataDirectory(data_directory="mosca")
entrenamiento.setTrainConfig(object_names_array=["mosca_blanca"], 
batch_size=4, 
num_experiments=25, 
train_from_pretrained_model="pretrained-yolov3.h5") 
entrenamiento.trainModel()

