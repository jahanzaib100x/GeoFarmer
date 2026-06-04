import os
import io
import numpy as np
from PIL import Image
import onnxruntime

def test_yolo_inference():
    print("\n--- Testing YOLOv8 Custom model inference ---")
    model_path = "backend/yolov8n_geokisan.onnx"
    if not os.path.exists(model_path):
        print(f"Error: YOLOv8 model not found at {model_path}")
        return
        
    session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    
    # Simulate a 640x640 green image
    mock_img_array = np.zeros((640, 640, 3), dtype=np.uint8)
    mock_img_array[:, :] = [45, 120, 70]
    img = Image.fromarray(mock_img_array)
    
    img_data = np.array(img).astype(np.float32) / 255.0
    img_data = np.transpose(img_data, (2, 0, 1))
    img_data = np.expand_dims(img_data, axis=0)
    
    inputs = {session.get_inputs()[0].name: img_data}
    outputs = session.run(None, inputs)
    output0 = outputs[0][0]
    print(f"YOLOv8 Output shape: {output0.shape} (Expected: [10, 8400] or similar)")
    print("YOLOv8 Inference success!")

def test_mobilenet_inference():
    print("\n--- Testing MobileNetV2 Pre-trained model inference ---")
    model_path = "backend/mobilenetv2_plant.onnx"
    if not os.path.exists(model_path):
        print(f"Error: MobileNetV2 model not found at {model_path}")
        return
        
    session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    
    # Simulate a 224x224 green image
    mock_img_array = np.zeros((224, 224, 3), dtype=np.uint8)
    mock_img_array[:, :] = [45, 120, 70]
    img = Image.fromarray(mock_img_array)
    
    # ImageNet preprocessing
    img_data = np.array(img).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_data = (img_data - mean) / std
    img_data = np.transpose(img_data, (2, 0, 1))
    img_data = np.expand_dims(img_data, axis=0)
    
    inputs = {session.get_inputs()[0].name: img_data}
    outputs = session.run(None, inputs)
    logits = outputs[0][0]
    print(f"MobileNetV2 Output shape: {logits.shape} (Expected: [38])")
    
    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / np.sum(exp_logits)
    best_idx = int(np.argmax(probs))
    print(f"Predicted index: {best_idx}, Top prob: {probs[best_idx]:.4f}")
    print("MobileNetV2 Inference success!")

if __name__ == "__main__":
    test_yolo_inference()
    test_mobilenet_inference()
