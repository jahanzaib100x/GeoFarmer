import os
import sys

def run_model_training():
    """
    Orchestrates the machine learning pipeline to download crop leaf disease datasets
    from Roboflow, initialize a pre-trained YOLOv8 nano network, execute training epochs,
    validate accuracy metrics, and serialize the optimized weights for production deployment.
    """
    print("Initializing GeoKisan/GeoFarmer Machine Learning Pipeline...")
    
    # Roboflow API configuration integration
    # Reads environment variables first, defaults to standard credential mapping
    roboflow_key = os.getenv("ROBOFLOW_API_KEY", "YOUR_ROBOFLOW_API_KEY")
    
    if roboflow_key == "YOUR_ROBOFLOW_API_KEY" or not roboflow_key:
        print("[WARNING] Roboflow API key is set to default placeholder 'YOUR_ROBOFLOW_API_KEY'.")
        print("Please configure your environment variables with 'export ROBOFLOW_API_KEY=your_key_here'.")
        print("Model training will attempt to initialize on local data sources or mock mock structure.")
        
    try:
        from roboflow import Roboflow
        print("Connecting to Roboflow developer API platform...")
        
        # Initialize Roboflow client
        rf = Roboflow(api_key=roboflow_key)
        
        # Pull agricultural leaf disease dataset catalog from high-fidelity research repo
        # Example Workspace: precision-ag-pakistan, Project: crop-rust-blast-detection
        # If credentials fail, this throws an API validation error
        project_name = os.getenv("ROBOFLOW_PROJECT_NAME", "crop-leaf-disease-detection")
        workspace_name = os.getenv("ROBOFLOW_WORKSPACE_NAME", "geo-farmer-intelligence")
        dataset_version = int(os.getenv("ROBOFLOW_DATASET_VERSION", "1"))
        
        workspace = rf.workspace(workspace_name)
        project = workspace.project(project_name)
        dataset = project.version(dataset_version).download("yolov8")
        
        dataset_yaml_path = os.path.join(dataset.location, "data.yaml")
        print(f"Dataset downloaded successfully to: {dataset.location}")
        print(f"Location of config data.yaml file: {dataset_yaml_path}")
        
    except Exception as re:
        print(f"[ERROR] Roboflow dataset retrieval failed: {re}")
        print("Generating local dataset configuration directories mock to ensure offline script execution.")
        
        # Get absolute path of train.py directory to prevent path mismatch
        script_dir = os.path.dirname(os.path.abspath(__file__))
        datasets_base_dir = os.path.join(script_dir, "datasets", "crop_leaf")
        
        train_img_dir = os.path.join(datasets_base_dir, "images", "train")
        val_img_dir = os.path.join(datasets_base_dir, "images", "val")
        train_lbl_dir = os.path.join(datasets_base_dir, "labels", "train")
        val_lbl_dir = os.path.join(datasets_base_dir, "labels", "val")
        
        os.makedirs(train_img_dir, exist_ok=True)
        os.makedirs(val_img_dir, exist_ok=True)
        os.makedirs(train_lbl_dir, exist_ok=True)
        os.makedirs(val_lbl_dir, exist_ok=True)
        
        # Generate dummy images and label annotations to prevent YOLOv8 empty dataset crash
        try:
            import numpy as np
            import cv2
            
            # Create a mock green leaf image array (640x640x3)
            mock_leaf = np.zeros((640, 640, 3), dtype=np.uint8)
            mock_leaf[:, :] = [45, 120, 70] # RGB/BGR green tone
            
            cv2.imwrite(os.path.join(train_img_dir, "dummy_leaf_1.jpg"), mock_leaf)
            cv2.imwrite(os.path.join(val_img_dir, "dummy_leaf_1.jpg"), mock_leaf)
            
            # Generate a standard label format file (class 0, center coordinates, bounding boxes)
            with open(os.path.join(train_lbl_dir, "dummy_leaf_1.txt"), "w") as lf:
                lf.write("0 0.5 0.5 0.4 0.4\n")
            with open(os.path.join(val_lbl_dir, "dummy_leaf_1.txt"), "w") as lf:
                lf.write("0 0.5 0.5 0.4 0.4\n")
            print("Generated local offline mock images and labels successfully.")
        except Exception as e_mock:
            print(f"Failed to generate mock images: e={e_mock}")
            
        # Generate dummy data.yaml config with absolute path
        dataset_yaml_path = os.path.join(datasets_base_dir, "data.yaml")
        with open(dataset_yaml_path, "w") as f:
            f.write(f"path: {datasets_base_dir}\n")
            f.write("train: images/train\n")
            f.write("val: images/val\n")
            f.write("names:\n")
            f.write("  0: Wheat Rust\n")
            f.write("  1: Rice Blast\n")
            f.write("  2: Potato Late Blight\n")
            f.write("  3: Cotton Leaf Curl Virus\n")
            f.write("  4: Tomato Early Blight\n")
            f.write("  5: Healthy Crop Leaf\n")
        print(f"Created fallback training configuration at: {dataset_yaml_path}")

    # Load and Train YOLOv8 nano model
    try:
        from ultralytics import YOLO
        
        print("Loading pre-trained YOLOv8 Nano base model (yolov8n.pt)...")
        # Load pre-trained nano weights
        model = YOLO("yolov8n.pt")
        
        epochs_count = int(os.getenv("TRAINING_EPOCHS", "25"))
        batch_size = int(os.getenv("TRAINING_BATCH_SIZE", "16"))
        device_target = os.getenv("TRAINING_DEVICE", "cpu") # Use cpu as standard low-spec fallback, gpu where accessible
        
        print(f"Starting model optimization loops: {epochs_count} epochs, batch size={batch_size}, target device={device_target}")
        
        # Execute model learning loop
        results = model.train(
            data=dataset_yaml_path,
            epochs=epochs_count,
            imgsz=640,
            batch=batch_size,
            device=device_target,
            workers=2,
            project="geokisan_training",
            name="crop_disease_model",
            exist_ok=True
        )
        
        print("Training execution finished successfully.")
        
        # Validate training metrics
        print("Running validation matrices evaluation...")
        metrics = model.val()
        print(f"Validation Mean Average Precision (mAP50): {metrics.results_dict.get('metrics/mAP50(B)', 0.0)}")
        print(f"Validation Precision metric: {metrics.results_dict.get('metrics/precision(B)', 0.0)}")
        print(f"Validation Recall metric: {metrics.results_dict.get('metrics/recall(B)', 0.0)}")
        
        # Export weights to main backend directory
        export_format = "onnx"
        print(f"Exporting model weights to {export_format} production format...")
        model.export(format=export_format)
        
        # Save output weights paths
        best_pt_path = "geokisan_training/crop_disease_model/weights/best.pt"
        if os.path.exists(best_pt_path):
            shutil_copy_path = "yolov8n_geokisan.pt"
            import shutil
            shutil.copy(best_pt_path, shutil_copy_path)
            print(f"Production model weight file serialized to: {shutil_copy_path}")
            
    except ImportError:
        print("[CRITICAL] ultralytics package is not loaded in this environment. Cannot run YOLOv8 optimization.")
        print("Please run: pip install ultralytics")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL ERROR] Model training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_model_training()
