# Sat2UAV: Generating UAV-Style Imagery from Satellite Data

Disaster-response pipelines often rely on UAV imagery for close-range detail, texture and viewpoint. Satellite imagery provides rapid regional coverage but lacks UAV-style perspective and fine detail.

This capstone research project on investigates whether generative models can bridge that visual gap and aims to convert **satellite imagery to UAV-like views (sat2UAV)** for *search and rescue (SAR)** workflows, especially when real UAV footage is unavailable or unsafe to collect in certain situations.

This repository contains code, experiments, and utilities developed for the project and focuses two main approaches that were tested:
- **CycleGAN (img2img-turbo)** for unpaired satellite→UAV domain translation
- **Stable Diffusion XL + ControlNet** for geometry-guided synthesis (Canny, Tile, Depth)

### Key Components:

- TE23D earthquake imagery stitching + preprocessing examples
- ESRGAN upsampling utilities
- CycleGAN training pipeline
- SDXL ControlNet inference workflows
- Sample of comparison results and qualitative findings which can be seen in `images/`

## Data Access
This project uses several datasets:    
**Satellite Imagery Dataset:**  
1. [TE23D Türkiye Earthquake 2023](https://ieeexplore.ieee.org/document/10824929/) - 256x256 tiled imagery + damage annotations.  

**UAV Reference Datasets:**  
2. [(ICCV 2025) UAVScenes Drone Dataset](https://github.com/sijieaaa/UAVScenes) - Large scale multi-modal dataset  

3. [ESRI Packing House District & Marshall Fire](https://www.esri.com/en-us/arcgis/products/arcgis-reality/resources/sample-drone-datasets) - orthophotos and other UAV data in smaller datasets

Due to size/licensing, **these datasets cannot be redistributed in this repository.** Please download them/request access directly from their official sources.  
- Include your own copy under `datasets` locally or in cloud storage.
- This repo provides some examples of the dataset images and orthomosaics in `images/` for demonstration only.


