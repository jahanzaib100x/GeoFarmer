import urllib.request
import torch
import torch.nn as nn
from torchvision import models
import os

def download_and_export():
    weights_url = "https://huggingface.co/Daksh159/plant-disease-mobilenetv2/resolve/main/mobilenetv2_plant.pth"
    weights_path = "mobilenetv2_plant.pth"
    onnx_path = "mobilenetv2_plant.onnx"
    
    if not os.path.exists(weights_path):
        print(f"Downloading pre-trained weights from {weights_url}...")
        urllib.request.urlretrieve(weights_url, weights_path)
        print("Download complete.")
    else:
        print("Pre-trained weights already present.")
        
    print("Recreating MobileNetV2 architecture with 38 outputs...")
    model = models.mobilenet_v2(pretrained=False)
    # The Daksh159 classifier architecture is:
    # model.classifier[1] = nn.Sequential(
    #     nn.Dropout(0.2),
    #     nn.Linear(model.classifier[1].in_features, 38)
    # )
    model.classifier[1] = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(model.classifier[1].in_features, 38)
    )
    
    print("Loading weights state dict...")
    state_dict = torch.load(weights_path, map_location='cpu')
    model.load_state_dict(state_dict)
    model.eval()
    
    print("Exporting model to ONNX...")
    dummy_input = torch.randn(1, 3, 224, 224) # MobileNetV2 standard input size
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        export_params=True, 
        opset_version=11, 
        input_names=['input'], 
        output_names=['output']
    )
    print(f"Successfully exported pre-trained PlantVillage model to {onnx_path}!")

if __name__ == "__main__":
    download_and_export()
