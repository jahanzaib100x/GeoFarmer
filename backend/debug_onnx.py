import onnxruntime
import numpy as np

def debug_onnx():
    session = onnxruntime.InferenceSession("backend/yolov8n_geokisan.onnx")
    
    # Run on a mock image of random green pixels
    np.random.seed(42)
    mock_data = np.random.uniform(0, 1, (1, 3, 640, 640)).astype(np.float32)
    
    inputs = {session.get_inputs()[0].name: mock_data}
    outputs = session.run(None, inputs)
    output0 = outputs[0][0]  # shape [10, 8400]
    
    print("Output shape:", output0.shape)
    print("Boxes (first 4 rows) - min:", np.min(output0[:4, :]), "max:", np.max(output0[:4, :]))
    
    class_scores = output0[4:, :]  # rows 4 to 9
    print("Class scores (last 6 rows) - min:", np.min(class_scores), "max:", np.max(class_scores), "mean:", np.mean(class_scores))
    
    # Print the maximum score of each class across all 8400 boxes
    max_per_class = np.max(class_scores, axis=1)
    for idx, score in enumerate(max_per_class):
        print(f"Class {idx} max score: {score:.5f}")

if __name__ == "__main__":
    debug_onnx()
