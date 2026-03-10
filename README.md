# PET MNI Overlay Viewer

A lightweight local NIfTI viewer designed for physicians/neuroimaging analysts to perform visual reads locally over web browser without neuroimaging workstation setup. The code-skeleton can be repurposed to view any other .nii or ROI masks. Currently focused on QC of **MNI-normalized PET images** with standard **VOI mask overlays**.

It is intended for quick review of subject PET scans in MNI space, alongside the MNI template and commonly used Centiloid-style VOIs. The viewer runs entirely on your own machine in a web browser, with simple controls for stepping through subjects, adjusting overlay visibility, and recording per-subject notes.

## What it does

This project lets you:

- view a subject PET scan over the MNI template
- overlay standard VOI masks in distinct colors
- control opacity/visibility of PET, MNI template, and each VOI
- move subject-by-subject or jump directly to a specific ID
- enter and save QC notes to `notes.csv`

The viewer is for **inspection and annotation**, not image processing. PET images must already be in **MNI space**.

## What to expect

When launched, the viewer opens a local webpage that shows:

- the **MNI template**
- one **subject PET** volume
- the following **VOI overlays**:
  - Whole Cerebellum
  - Cortex
  - Pons
  - Cerebellar Gray
  - Whole Cerebellum + Brainstem

You can adjust opacity for each layer, hide/show overlays, and attach notes to each subject as you review them.

## Project layout
```
fastreads/
├── viewer.html
├── server.py
├── niivue.umd.js
├── Start_Viewer.bat
├── Start_Viewer_mac.sh
├── Atlases/
│   ├── avg152T1.nii.gz
│   ├── voi_ctx_2mm.nii.gz
│   ├── voi_WhlCbl_2mm.nii.gz
│   ├── voi_Pons_2mm.nii.gz
│   ├── voi_CerebGry_2mm.nii.gz
│   └── voi_WhlCblBrnStm_2mm.nii.gz
└── subPETs/
    ├── w011002_PET_3D.nii
    ├── w011005_PET_3D.nii
    └── ...
```

PET filenames should follow this pattern:

wXXXXXX_PET_3D.nii

where `XXXXXX` is the 6-digit subject ID.

## Run it

### Windows

Double-click: `Start_Viewer.bat`

### macOS

Open Terminal in the project folder and run: `bash Start_Viewer_mac.sh`

The viewer will open in your browser at:

`http://127.0.0.1:8000/viewer.html`

## Notes

- Python 3 is required.
- No extra Python packages are needed.
- Keep the terminal/server window open while using the viewer.
- Notes entered in the viewer can be exported to `notes.csv`.

## In one line

This is a simple, portable QC viewer for browsing **MNI-space PET scans with VOI overlays and notes**, without needing a full neuroimaging workstation setup.


## Third-party libraries

This project includes the following third-party component:

NiiVue (https://github.com/niivue/niivue)

File used:
niivue.umd.js

License:
BSD 2-Clause License

Copyright (c) 2021, Niivue
All rights reserved.