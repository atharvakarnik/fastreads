# PET MNI Overlay Viewer

A lightweight local NIfTI viewer designed for physicians/neuroimaging analysts to perform visual reads in a web browser without a full neuroimaging workstation setup.

It currently supports two review modes:

- **PET view**: PET-space subject volume only, with a PET-only grayscale inversion toggle (default ON for black-on-white display).
- **MNI view**: MNI-normalized PET with MNI template + Centiloid-style VOI overlays.

The viewer runs entirely on your own machine, with controls for stepping through subjects, adjusting display/overlay visibility, and recording per-subject notes.

## What it does

This project lets you:

- switch between **PET** and **MNI** viewing modes
- view PET-space scans with default inverted grayscale for better physician readability
- view MNI-space PET scans over the template
- overlay standard VOI masks in distinct colors (MNI mode)
- control opacity/visibility of PET, MNI template, and each VOI
- move subject-by-subject or jump directly to a specific ID
- enter and save QC notes to `notes.csv`

The viewer is for **inspection and annotation**, not image processing.

## What to expect

When launched, the viewer opens a local webpage with:

- **PET mode**
  - one PET-space subject volume
  - PET-only invert toggle (default: inverted grayscale)
- **MNI mode**
  - the MNI template
  - one subject PET volume from `subPETs/`
  - the following VOI overlays:
    - Whole Cerebellum
    - Cortex
    - Pons
    - Cerebellar Gray
    - Whole Cerebellum + Brainstem

You can adjust opacity, hide/show overlays, and attach notes to each subject as you review them.

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
├── subPETs/
│   ├── w23_PET_3D.nii
│   ├── w24_PET_3D.nii
│   └── ...
└── PET_Space/
    ├── 23_PET_3D.nii
    ├── 24_PET_3D.nii
    └── ...
```

## Input filename and ID rules

The viewer does not require 6-digit IDs anymore. It works with any numeric ID length, as long as the filenames match the expected PET naming pattern exactly.

Accepted filename patterns:

- `subPETs/`: `w<ID>_PET_3D.nii` or `w<ID>_PET_3D.nii.gz`
- `PET_Space/`: `<ID>_PET_3D.nii` or `<ID>_PET_3D.nii.gz`

Where:

- `<ID>` must be digits only
- the same `<ID>` should be used across both folders for the same subject
- the viewer derives the subject ID from the numeric portion of the filename

Examples:

- `subPETs/w23_PET_3D.nii` pairs with `PET_Space/23_PET_3D.nii`
- `subPETs/w011002_PET_3D.nii.gz` pairs with `PET_Space/011002_PET_3D.nii.gz`

Important constraints:

- Files that do not match these patterns are ignored by `server.py`.
- Subjects are discovered from `subPETs/`. If a subject is missing from `subPETs/`, it will not appear in the viewer.
- `PET_Space/` is optional per subject for PET view, but if its matching file is missing then that subject cannot be shown in PET mode.
- The "Go to ID" field in `viewer.html` uses the first discovered subject ID to show the example digit count and example ID.

## Run it

### Windows

Double-click: `Start_Viewer.bat`

### macOS

Open Terminal in the project folder and run: `bash Start_Viewer.sh`

The viewer will open in your browser at:

`http://127.0.0.1:8000/viewer.html`

## Notes

- Python 3 is required.
- No extra Python packages are needed.
- Keep the terminal/server window open while using the viewer.
- Notes entered in the viewer can be exported to `notes.csv`.

## In one line

This is a simple, portable QC viewer for browsing PET-space and MNI-space PET scans, with VOI overlays in MNI mode and per-subject notes.

## Third-party libraries

This project includes the following third-party component:

### Software 

NiiVue (https://github.com/niivue/niivue)

File used:
niivue.umd.js

License:
BSD 2-Clause License

Copyright (c) 2021, Niivue
All rights reserved.

### Data 

Example PET images used in this repository come from the OpenNeuro dataset  
**"Cerebral tau deposition in young healthy adults using [18F]MK6240 PET"**  
https://openneuro.org/datasets/ds006756

Used only **5 subjects** for demo. I would have preferred to use my own data where physicians use it, but workplace data policies (rightfully) have other plans — so public CC0 data to the rescue.