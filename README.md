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
│   ├── w011002_PET_3D.nii
│   ├── w011005_PET_3D.nii
│   └── ...
└── PET_Space/
    ├── 011002_PET_3D.nii
    ├── 011005_PET_3D.nii
    └── ...
```

Input naming conventions:

- `subPETs/`: filenames should include ID as `wXXXXXX` (for example, `w011002_PET_3D.nii`).
- `PET_Space/`: filenames should follow `XXXXXX_PET_3D.nii` (for example, `011002_PET_3D.nii`).

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

NiiVue (https://github.com/niivue/niivue)

File used:
niivue.umd.js

License:
BSD 2-Clause License

Copyright (c) 2021, Niivue
All rights reserved.
