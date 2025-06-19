# 1. Query and Download JWST NIRCam Data
from astroquery.mast import Observations
from astropy.io import fits
from astropy.visualization import (MinMaxInterval, LogStretch, ImageNormalize, AsinhStretch)
from astropy.wcs import WCS
import matplotlib.pyplot as plt
from photutils.segmentation import detect_sources, SourceCatalog, detect_threshold
import numpy as np
import os
from multiprocessing import Pool
import functools
import gc
import time
from astroquery.exceptions import TimeoutError as AstroQueryTimeout

# Configure matplotlib for better performance
plt.rcParams['figure.dpi'] = 100  # Lower DPI for faster rendering
plt.rcParams['figure.figsize'] = (8, 8)  # Smaller figure size
plt.rcParams['figure.max_open_warning'] = 10  # Reduce memory usage from many plots

# Configuration
PERFORM_SOURCE_DETECTION = True  # Set to False to skip source detection
COLOR_MODE = 'grayscale'  # Options: 'grayscale', 'false_color'

# Available targets (famous JWST observations)
TARGETS = {
    'SMACS': {
        'name': 'SMACS J0723.3-7327',
        'description': 'Galaxy cluster SMACS 0723'
    },
    'CARINA': {
        'name': 'NGC 3372',
        'description': 'Carina Nebula'
    },
    'CARTWHEEL': {
        'name': 'ESO 350-40',
        'description': 'Cartwheel Galaxy'
    },
    'PILLARS': {
        'name': 'M16',
        'description': 'Pillars of Creation in Eagle Nebula'
    },
    'STEPHAN': {
        'name': "Stephan's Quintet",
        'description': 'Compact galaxy group HCG 92'
    },
    'SOUTHERN': {
        'name': 'NGC 7469',
        'description': 'Southern Ring Nebula'
    },
    'ORION': {
        'name': 'NGC 1976',
        'description': 'Orion Nebula'
    
    },
    'PANDORA': {
        'name': 'Pandora Cluster',
        'description': 'Abell 2744 galaxy cluster'
    }
}

# Select target
print("Available targets:")
for key, value in TARGETS.items():
    print(f"{key}: {value['description']}")
    
target_key = input("Select target (SMACS/CARINA/CARTWHEEL/PILLARS/STEPHAN/SOUTHERN/ORION/PANDORA) [default=SMACS]: ").strip().upper() or 'SMACS'
target = TARGETS[target_key]['name']

print(f"\nSelected target: {target}")

# Check for cached data first
cache_dir = "cached_data"
cache_file = os.path.join(cache_dir, f"{target.replace(' ', '_')}.fits")

if os.path.exists(cache_file):
    print("Using cached file...")
    fits_path = cache_file
else:
    print("Starting JWST data query...") 
    # Configure longer timeout
    Observations.TIMEOUT = 1200  # 20 minutes
    max_retries = 3
    retry_delay = 5  # seconds
    attempt = 0

    try:
        while attempt < max_retries:
            try:
                print(f"Attempt {attempt + 1}/{max_retries}...")
                # Search with more specific constraints
                obs_table = Observations.query_object(target, radius='0.1 deg')
                print(f"Found {len(obs_table)} observations")

                # Filter for JWST observations
                jwst_obs = obs_table[obs_table['obs_collection'] == 'JWST']

                # Further filter for images
                if 'dataproduct_type' in jwst_obs.colnames:
                    jwst_obs = jwst_obs[jwst_obs['dataproduct_type'] == 'image']

                # Filter for NIRCam images if possible
                if 'instrument_name' in jwst_obs.colnames:
                    nircam_obs = jwst_obs[jwst_obs['instrument_name'] == 'NIRCAM']
                    if len(nircam_obs) > 0:
                        jwst_obs = nircam_obs

                break  # If successful, exit the retry loop

            except (TimeoutError, AstroQueryTimeout) as e:
                attempt += 1
                if attempt < max_retries:
                    print(f"Timeout occurred. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise TimeoutError("All retry attempts failed")

        print(f"\nFound {len(jwst_obs)} JWST images total")

        if len(jwst_obs) > 0:
            print("Downloading calibrated image...")
            products = Observations.get_product_list(jwst_obs[0])
            print(f"\nAvailable product types:", np.unique(products['productSubGroupDescription']))
            calib_products = Observations.filter_products(products, 
                                                                       productSubGroupDescription=['CAL'],
                extension='fits')
            if len(calib_products) > 0:
                download_manifest = Observations.download_products(calib_products[:1], mrp_only=False)
                fits_path = download_manifest['Local Path'][0]
                # Cache the downloaded file
                os.makedirs(cache_dir, exist_ok=True)
                os.rename(fits_path, cache_file)
                fits_path = cache_file
                print(f"Downloaded and cached file to: {fits_path}")
            else:
                raise ValueError("No calibrated products found for the first JWST observation.")
        else:
            raise ValueError("No matching JWST observations found!")
            
    except Exception as e:
        if os.path.exists(cache_file):
            print(f"Error querying MAST: {str(e)}")
            print("Using cached file instead...")
            fits_path = cache_file
        else:
            raise Exception(f"Error querying MAST and no cached file available: {str(e)}")

# 2. Read and Display the Calibrated Image
print("\nReading FITS file...")
hdu = fits.open(fits_path)
data = hdu[1].data  # JWST NIRCam images are often in extension 1
wcs = WCS(hdu[1].header)

# 3. Apply Contrast Stretching
if COLOR_MODE == 'grayscale':
    norm = ImageNormalize(data, interval=MinMaxInterval(), stretch=LogStretch())
elif COLOR_MODE == 'false_color':
    # For false color, we can use the original data with a different colormap
    norm = ImageNormalize(data, interval=MinMaxInterval(), stretch=LogStretch())
else:
    raise ValueError("Invalid COLOR_MODE. Choose from 'grayscale' or 'false_color'.")

# 4. Display with WCSAxes, overlay celestial coordinates and scale bar
fig = plt.figure(figsize=(20, 8))

# Create two subplots for different visualization modes
visualizations = [
    ('NIRCam', 'gray', LogStretch()),
    ('False Color', 'inferno', LogStretch())
]

for idx, (title, cmap, stretch) in enumerate(visualizations, 1):
    ax = plt.subplot(1, 2, idx, projection=wcs)
    norm = ImageNormalize(data, interval=MinMaxInterval(), stretch=stretch)
    im = ax.imshow(data, norm=norm, origin='lower', cmap=cmap)
ax.set_xlabel('RA')
ax.set_ylabel('Dec')
ax.set_title(f'JWST NIRCam Image: {target}')

# Add scale bar using a simpler method
# Convert arcseconds to degrees for the scale bar
scale_bar_length = 5  # arcseconds
scale_bar_length_deg = scale_bar_length / 3600  # convert to degrees

# Get the pixel scale from the WCS
pix_scale = np.abs(wcs.wcs.cdelt[0])  # degrees per pixel
scale_bar_length_pix = scale_bar_length_deg / pix_scale

# Position the scale bar in the lower right corner
y_pos = int(data.shape[0] * 0.1)  # 10% from bottom
x_start = int(data.shape[1] * 0.7)  # 70% from left
x_end = x_start + int(scale_bar_length_pix)

# Draw the scale bar
ax.plot([x_start, x_end], [y_pos, y_pos], '-w', linewidth=2)
ax.text(x_start + scale_bar_length_pix/2, y_pos + data.shape[0]*0.02,
        f"{scale_bar_length}\"", color='white', ha='center', va='bottom')

plt.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04, label='Counts')
plt.show()

# Helper function for parallel source detection
def detect_sources_parallel(data, threshold, npixels):
    # Split image into chunks
    chunks = np.array_split(data, 4)  # Split into 4 sections
    with Pool(processes=4) as pool:
        detect_func = functools.partial(detect_sources, threshold=threshold, npixels=npixels)
        results = pool.map(detect_func, chunks)
    return results

# 5. Use photutils for Source Detection
if PERFORM_SOURCE_DETECTION:
    print("\nPerforming source detection...")
    threshold = detect_threshold(data, nsigma=3)
    segm = detect_sources(data, threshold, npixels=10)
    cat = SourceCatalog(data, segm, wcs=wcs)
    print(f"Detected {len(cat)} sources.")

    # Overlay segmentation map
    plt.figure(figsize=(10, 10))
    ax2 = plt.subplot(projection=wcs)
    ax2.imshow(segm.data, origin='lower', cmap='nipy_spectral', alpha=0.5)
    ax2.set_title('Source Detection Map')
    plt.show()

    # Clean up memory
    del segm
    del cat
    gc.collect()
else:
    print("Skipping source detection...")

# Clean up memory
del data
hdu.close()
gc.collect()
