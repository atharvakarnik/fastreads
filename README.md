# PET MNI Overlay Viewer

A lightweight local NIfTI viewer for physician/neuroimaging visual reads in a web browser, without needing a full neuroimaging workstation setup.

Supports two review modes:

-  **PET view**: PET-space subject volume only, with grayscale inversion and PET intensity min/max controls.
- **MNI view**: MNI-normalized PET with an MNI template, Centiloid-style VOI overlays, and the same PET intensity min/max controls.

Everything runs locally. You can move through subjects, adjust PET display range and overlays, and save notes to `notes.csv`.

## What it does

- switch between **PET** and **MNI**
- review PET-space scans with invert-on/off control
- adjust PET intensity min/max in either view
- review MNI-space PET over the template
- show standard VOI masks in MNI view
- adjust opacity and visibility for PET, template, and VOIs
- jump to a subject ID or step through the list
- save per-subject notes

This viewer is for review and annotation, not processing.

## Demo data vs your own data

The repo includes a small demo dataset in `Example/`.

The app looks for data in this order:

- root `PET_MNI/`, otherwise `Example/PET_MNI/`
- root `PET_Space/`, otherwise `Example/PET_Space/`

So the demo works out of the box, but your own root folders take priority if they exist.

To try your own data:

- put MNI-space PETs in root `PET_MNI/`
- put PET-space scans in root `PET_Space/`

Fallback is based on folder existence, not file validity. If root `PET_MNI/` exists but is empty or misnamed, the app will not fall back to the demo folder.

## What you will see

- **PET mode**
  - one PET-space scan
  - invert toggle for grayscale display
  - PET intensity min/max controls
- **MNI mode**
  - MNI template
  - one scan from the resolved `PET_MNI/` folder
  - PET intensity min/max controls shared with PET mode for the current subject
  - VOIs for Whole Cerebellum, Cortex, Pons, Cerebellar Gray, and Whole Cerebellum + Brainstem

## Project layout

```text
fastreads/
├── viewer.html
├── server.py
├── niivue.umd.js
├── Start_Viewer.bat
├── Start_Viewer.sh
├── Atlases/
│   ├── avg152T1.nii.gz
│   ├── voi_ctx_2mm.nii.gz
│   ├── voi_WhlCbl_2mm.nii.gz
│   ├── voi_Pons_2mm.nii.gz
│   ├── voi_CerebGry_2mm.nii.gz
│   └── voi_WhlCblBrnStm_2mm.nii.gz
├── Example/
│   ├── PET_MNI/
│   │   ├── w23_PET_3D.nii.gz
│   │   ├── w24_PET_3D.nii.gz
│   │   └── ...
│   └── PET_Space/
│       ├── 23_PET_3D.nii.gz
│       ├── 24_PET_3D.nii.gz
│       └── ...
├── PET_MNI/        # To store your cohort 3D PET-MNI normalized
└── PET_Space/      # To store your cohort 3D PET
```

## Filename rules

The viewer accepts any numeric ID length as long as the filenames match exactly:

- `PET_MNI/`: `w<ID>_PET_3D.nii` or `w<ID>_PET_3D.nii.gz`
- `PET_Space/`: `<ID>_PET_3D.nii` or `<ID>_PET_3D.nii.gz`

Rules:

- `<ID>` must be digits only
- use the same `<ID>` in both folders for the same subject
- the app extracts the subject ID from the filename

Examples:

- `PET_MNI/w23_PET_3D.nii.gz` pairs with `PET_Space/23_PET_3D.nii.gz`
- `PET_MNI/w011002_PET_3D.nii` pairs with `PET_Space/011002_PET_3D.nii`

Notes:

- files that do not match the pattern are ignored
- subjects are discovered from the resolved `PET_MNI/` folder
- `PET_Space/` can be missing for a subject, but PET view will not load for that subject
- the "Go to ID" box uses the first discovered ID as its example

## Run it

### Windows

Double-click `Start_Viewer.bat`

### macOS

Run:

```bash
bash Start_Viewer.sh
```

Then open:

`http://127.0.0.1:8000/viewer.html`

## Notes

- Python 3 required
- no extra Python packages
- keep the server window open while using the viewer
- notes can be written to `notes.csv`

 License : MIT (applies to source code in this repo. 3rd party resources retain their original license)

## Third-party resources

### Software

NiiVue  
https://github.com/niivue/niivue

File used: `niivue.umd.js`  
License: BSD 2-Clause License

Copyright (c) 2021, Niivue
All rights reserved.

### Data

Example PET images come from the OpenNeuro dataset:  
**"Cerebral tau deposition in young healthy adults using [18F]MK6240 PET"**  
https://openneuro.org/datasets/ds006756

This repo includes 5 subjects for demo use.
