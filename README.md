# Satellite → UAV-Simulated Rubble Detection (Capstone)

This project generates **UAV-simulated imagery from satellite data** using an integrated **style-transfer + upsampling** pipeline, then trains a **transformer-based model** for rubble/damage detection. The goal is to apply this pipeline and integrate detections into a simple **UAV path-planning** demo.

## Repo Structure
data/ # (gitignored) datasets and annotations
raw/ # sample orthomosaics (small examples only)
processed/ # tiles, UAV-sim outputs
annotations/ # COCO/YOLO JSONs

models/ # (gitignored) trained weights/checkpoints
notebooks/ # EDA and experiment notebooks
src/ # reusable source code (training/inference/planner)
reports/ # drafts, figures, results tables
figures/
configs/ # YAML/JSON configs for reproducible runs
submission/ # final report and artefact bundle

README.md
environment.yml
.gitignore
LICENSE


## Data Access
This project uses the **[TE23D Turkey Earthquake dataset]** (tiles + segmentation labels) that was introduced [here.](https://ieeexplore.ieee.org/document/10824929/)  
Due to size/licensing, **raw data is not included**.  
- Include your own copy under `data/` locally or in cloud storage.
- This repo provides **sample orthomosaics** in `data/raw/` for demonstration only.

##License

Code is released under the MIT License. Datasets are subject to their own licenses and are not redistributed in this repository.

##Citation

If you build on this work, please cite the TE23D dataset and this repo.

