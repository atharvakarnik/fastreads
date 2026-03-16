# PET MNI Overlay Viewer

A lightweight local NIfTI viewer for physician/neuroimaging visual reads in a web browser, without needing a full neuroimaging workstation setup.

It supports two review modes:

- **PET view**: PET-space subject volume only, with a PET-only grayscale inversion toggle.
- **MNI view**: MNI-normalized PET with an MNI template and Centiloid-style VOI overlays.

The viewer runs entirely on your own machine and includes subject navigation, overlay controls, and per-subject notes saved to `notes.csv`.

## What it does

This project lets you:

- switch between **PET** and **MNI** viewing modes
- view PET-space scans with inverted grayscale support
- view MNI-space PET scans over the template
- overlay standard VOI masks in distinct colors
- control opacity and visibility for PET, template, and VOIs
- move subject-by-subject or jump directly to a specific ID
- enter and save QC notes to `notes.csv`

The viewer is for inspection and annotation, not image processing.

## Demo data and your own data

This repository currently ships with demo data inside `Example/`.

At runtime, the app resolves data folders like this:

- prefer root `PET_MNI/`, otherwise use `Example/PET_MNI/`
- prefer root `PET_Space/`, otherwise use `Example/PET_Space/`

This means the repository works out of the box with the demo dataset, but your own data takes precedence as soon as you create the root folders.

To test this on your own data:

- store MNI-space PETs in root `PET_MNI/`
- store PET-space subject scans in root `PET_Space/`

Important: fallback is based on folder existence, not whether files were found. If root `PET_MNI/` exists but is empty or contains invalid filenames, the app will not fall back to `Example/PET_MNI/`.

## What to expect

When launched, the viewer opens a local webpage with:

- **PET mode**
  - one PET-space subject volume
  - PET-only invert toggle
- **MNI mode**
  - the MNI template
  - one subject PET volume from the resolved `PET_MNI/` folder
  - the following VOI overlays:
    - Whole Cerebellum
    - Cortex
    - Pons
    - Cerebellar Gray
    - Whole Cerebellum + Brainstem

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
│   │   ├── w23_PET_3D.nii
│   │   ├── w24_PET_3D.nii
│   │   └── ...
│   └── PET_Space/
│       ├── 23_PET_3D.nii
│       ├── 24_PET_3D.nii
│       └── ...
├── PET_MNI/        # optional private data at root, preferred when present
└── PET_Space/      # optional private data at root, preferred when present
```

## Input filename and ID rules

The viewer works with any numeric ID length, as long as filenames match the expected pattern exactly.

Accepted filename patterns:

- `PET_MNI/`: `w<ID>_PET_3D.nii` or `w<ID>_PET_3D.nii.gz`
- `PET_Space/`: `<ID>_PET_3D.nii` or `<ID>_PET_3D.nii.gz`

Where:

- `<ID>` must be digits only
- the same `<ID>` should be used across both folders for the same subject
- the viewer derives the subject ID from the numeric portion of the filename

Examples:

- `PET_MNI/w23_PET_3D.nii` pairs with `PET_Space/23_PET_3D.nii`
- `PET_MNI/w011002_PET_3D.nii.gz` pairs with `PET_Space/011002_PET_3D.nii.gz`

Important constraints:

- files that do not match these patterns are ignored by `server.py`
- subjects are discovered from the resolved `PET_MNI/` folder
- `PET_Space/` is optional per subject, but PET view cannot load a subject if its matching PET-space file is missing
- the "Go to ID" field in `viewer.html` uses the first discovered subject ID to show the example digit count

## Run it

### Windows

Double-click `Start_Viewer.bat`

### macOS

Open Terminal in the project folder and run `bash Start_Viewer.sh`

The viewer opens at:

`http://127.0.0.1:8000/viewer.html`

## Notes

- Python 3 is required
- no extra Python packages are needed
- keep the terminal/server window open while using the viewer
- notes entered in the viewer can be exported to `notes.csv`

## Third-party libraries

This project includes the following third-party component:

### Software

NiiVue (https://github.com/niivue/niivue)

File used:
`niivue.umd.js`

License:
BSD 2-Clause License

Copyright (c) 2021, Niivue
All rights reserved.

### Data

Example PET images used in this repository come from the OpenNeuro dataset  
**"Cerebral tau deposition in young healthy adults using [18F]MK6240 PET"**  
https://openneuro.org/datasets/ds006756

Used only 5 subjects for demo.
