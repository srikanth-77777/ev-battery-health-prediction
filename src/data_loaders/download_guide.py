"""
Download and Dataset Acquisition Guide for all 4 Battery Datasets.
Run this script to inspect dataset locations and initiate downloads.
"""

import os
import sys
import urllib.request
import zipfile

DATA_ROOT = os.path.join(os.getcwd(), "data", "raw")

DATASET_INFO = {
    "NASA": {
        "folder": os.path.join(DATA_ROOT, "nasa"),
        "source_url": "https://data.nasa.gov/dataset/li-ion-battery-aging-datasets",
        "direct_archive": "https://phinate.s3.amazonaws.com/nasa-battery/1.+BatteryAgingARC-FY08Q4.zip",
        "description": "NASA PCoE Li-ion Battery Set 1 (B0005, B0006, B0007, B0018). Run-to-failure 2.0 Ah 18650 cells.",
        "chemistry": "LiCoO2 (LCO)",
        "nominal_capacity_ah": 2.0,
        "eol_capacity_ah": 1.4  # 70% retention
    },
    "CALCE": {
        "folder": os.path.join(DATA_ROOT, "calce"),
        "source_url": "https://calce.umd.edu/battery-data",
        "description": "CALCE UMD CS2 & CX2 prismatic / cylindrical cells (e.g. CS2_35, CS2_36, CS2_37, CS2_38).",
        "chemistry": "LiCoO2",
        "nominal_capacity_ah": 1.1,
        "eol_capacity_ah": 0.88  # 80% retention
    },
    "OXFORD": {
        "folder": os.path.join(DATA_ROOT, "oxford"),
        "source_url": "https://ora.ox.ac.uk/objects/uuid:03ba4b01-cfed-46d3-9b1a-7d4a7bdf6fac",
        "direct_zip": "https://ora.ox.ac.uk/objects/uuid:03ba4b01-cfed-46d3-9b1a-7d4a7bdf6fac/files/m4766e408bf60677a28e3b5e40e2dcae5",
        "description": "Oxford Battery Degradation Dataset 1 (8 Kokam 740 mAh pouch cells cycled at 40°C).",
        "chemistry": "LiCoO2/graphite pouch",
        "nominal_capacity_ah": 0.74,
        "eol_capacity_ah": 0.592  # 80% retention
    },
    "MIT_STANFORD": {
        "folder": os.path.join(DATA_ROOT, "mit_stanford"),
        "source_url": "https://data.matr.io/1/projects/5c48dd4b122308779c532b22",
        "description": "Severson et al. Nature Energy (2019) 124 Commercial A123 LFP cells fast charged at different C-rates.",
        "chemistry": "LiFePO4 (LFP)",
        "nominal_capacity_ah": 1.1,
        "eol_capacity_ah": 0.88  # 80% retention
    }
}

def print_dataset_guide():
    print("=" * 80)
    print("MULTI-DATASET ACQUISITION DIRECTORY GUIDE")
    print("=" * 80)
    for name, info in DATASET_INFO.items():
        print(f"\n[{name}]")
        print(f"  Target Folder : {info['folder']}")
        print(f"  Description   : {info['description']}")
        print(f"  Chemistry     : {info['chemistry']}")
        print(f"  Nominal Q     : {info['nominal_capacity_ah']} Ah")
        print(f"  Source URL    : {info['source_url']}")
        if "direct_archive" in info:
            print(f"  Direct Link   : {info['direct_archive']}")
    print("=" * 80)

def download_nasa():
    target_dir = DATASET_INFO["NASA"]["folder"]
    os.makedirs(target_dir, exist_ok=True)
    existing_mats = [f for f in os.listdir(target_dir) if f.endswith(".mat")]
    if existing_mats:
        print(f"[NASA] Existing .mat files found: {existing_mats}")
        return

    url = DATASET_INFO["NASA"]["direct_archive"]
    zip_dest = os.path.join(target_dir, "nasa_battery_set1.zip")
    print(f"[NASA] Downloading Set 1 archive from {url}...")
    try:
        urllib.request.urlretrieve(url, zip_dest)
        print("[NASA] Extracting archive...")
        with zipfile.ZipFile(zip_dest, "r") as zf:
            zf.extractall(target_dir)
        print("[NASA] Successfully downloaded and extracted.")
    except Exception as e:
        print(f"[NASA] Automated download failed or network blocked: {e}")
        print(f"       Please place B0005.mat, B0006.mat, B0007.mat, B0018.mat in {target_dir}")

if __name__ == "__main__":
    print_dataset_guide()
    if len(sys.argv) > 1 and sys.argv[1] == "--download-nasa":
        download_nasa()
