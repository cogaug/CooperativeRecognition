from ultralytics import YOLO

# Load a model
# model = YOLO('yolov8n.pt')  # load an official model
model = YOLO('/home/kkk/ultralytics/runs/detect/train18/weights/best.pt')  # load an official model

# Validate the model
metrics = model.val(data='/home/kkk/ultralytics/dataset/inavi_231110/Datasets/my.yaml')  # no arguments needed, dataset and settings remembered
metrics.box.map    # map50-95
metrics.box.map50  # map50
metrics.box.map75  # map75
metrics.box.maps   # a list contains map50-95 of each category
