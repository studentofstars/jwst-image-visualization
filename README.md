````````.# James Webb Space Telescope Image Visualization

This Python script provides tools for downloading, processing, and visualizing James Webb Space Telescope (JWST) images, along with performing source detection on the astronomical data.

## Features

- Download JWST calibrated images from MAST (Mikulski Archive for Space Telescopes)
- Support for multiple target objects:
  - SMACS J0723.3-7327 (Galaxy cluster SMACS 0723)
  - NGC 3324 (Carina Nebula)
  - ESO 350-40 (Cartwheel Galaxy)
  - M16 (Pillars of Creation in Eagle Nebula)
  - Stephan's Quintet (Compact galaxy group HCG 92)
  - NGC 7469 (Southern Ring Nebula)
  - NGC 1976 (Orion Nebula)
  - Abell 2744 (Pandora Cluster)
- Image visualization with two modes:
  - NIRCam view with grayscale and logarithmic stretch
  - False color view using 'inferno' colormap
- Astronomical features:
  - WCS (World Coordinate System) coordinate overlay
  - Scale bar in arcseconds
  - Source detection with photutils
  - Automatic handling of NaN and infinite values
- Performance optimizations:
  - Local caching of downloaded files
  - Memory management with garbage collection
  - Parallel processing for source detection

## Requirements

- Python 3.x
- Required packages:
  - astroquery
  - astropy
  - matplotlib
  - photutils
  - numpy

## Data Files

Due to their large size (>100MB each), FITS files are not included in this repository. The script will automatically download these files when needed and store them in the `cached_data` directory. The files include:

- ESO_350-40.fits (Cartwheel Galaxy)
- M16.fits (Pillars of Creation)
- NGC_3324.fits (Carina Nebula)
- SMACS_J0723.3-7327.fits (Galaxy cluster SMACS 0723)
- Stephan's_Quintet.fits (HCG 92)
- NGC_7469.fits (Southern Ring Nebula)
- NGC_1976.fits (Orion Nebula)
- Abell_2744.fits (Pandora Cluster)

First-time users should simply run the script and select a target - the required files will be downloaded automatically.

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install astroquery astropy matplotlib photutils numpy
```

## Usage

1. Run the script:
```bash
python WEBB.py
```

2. Select a target when prompted:
   - SMACS (Galaxy cluster SMACS 0723)
   - CARINA (Carina Nebula)
   - CARTWHEEL (Cartwheel Galaxy)
   - PILLARS (Pillars of Creation in Eagle Nebula)
   - STEPHAN (Stephan's Quintet)
   - SOUTHERN (Southern Ring Nebula)
   - ORION (Orion Nebula)
   - JUPITER (Jupiter and its moons)
   - PANDORA (Pandora Cluster)

3. The script will:
   - Download the image if not cached
   - Display the image in both grayscale and false color
   - Perform source detection (if PERFORM_SOURCE_DETECTION = True)
   - Show a source detection map

## Configuration

You can modify these parameters in the script:

- `PERFORM_SOURCE_DETECTION`: Enable/disable source detection (default: True)
- `COLOR_MODE`: Choose visualization mode ('grayscale' or 'false_color')
- `plt.rcParams`: Adjust matplotlib rendering parameters

## Output

The script generates:
1. Two visualization panels:
   - Grayscale view with logarithmic stretch
   - False color view with 'inferno' colormap
2. Source detection visualization (if enabled)
3. Cached FITS files in the `cached_data` directory

## Data Structure

```
project/
├── WEBB.py              # Main script
├── README.md            # This file
├── cached_data/         # Downloaded FITS files
└── mastDownload/        # Temporary download directory
    └── JWST/           # JWST specific data
```

## Technical Details

- Uses WCS for accurate astronomical coordinate mapping
- Implements logarithmic stretch for better dynamic range visualization
- Includes scale bar calibrated to image plate scale
- Performs source detection using sigma-clipping and segmentation
- Handles FITS files with proper error management

## Notes

- The script automatically clips NaN and infinite values in the data
- Downloaded files are cached for faster subsequent access
- Memory management is implemented for handling large FITS files
`````````
