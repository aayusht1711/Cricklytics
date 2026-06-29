import os
import urllib.request
import zipfile
import shutil

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

DATASETS = {
    # Domestic Leagues
    "IPL": "https://cricsheet.org/downloads/ipl_csv2.zip",
    "BBL": "https://cricsheet.org/downloads/bbl_csv2.zip",
    "WBBL": "https://cricsheet.org/downloads/wbbl_csv2.zip",
    "PSL": "https://cricsheet.org/downloads/psl_csv2.zip",
    "CPL": "https://cricsheet.org/downloads/cpl_csv2.zip",
    "Hundred_Mens": "https://cricsheet.org/downloads/hundred_mens_csv2.zip",
    "Hundred_Womens": "https://cricsheet.org/downloads/hundred_womens_csv2.zip",
    
    # International Men
    "Mens_T20I": "https://cricsheet.org/downloads/t20s_male_csv2.zip",
    "Mens_ODI": "https://cricsheet.org/downloads/odis_male_csv2.zip",
    "Mens_Test": "https://cricsheet.org/downloads/tests_male_csv2.zip",
    
    # International Women
    "Womens_T20I": "https://cricsheet.org/downloads/t20s_female_csv2.zip",
    "Womens_ODI": "https://cricsheet.org/downloads/odis_female_csv2.zip",
    "Womens_Test": "https://cricsheet.org/downloads/tests_female_csv2.zip"
}

def download_and_extract(name, url):
    print(f"Downloading {name} from {url}...")
    zip_path = os.path.join(DATA_DIR, f"{name}.zip")
    
    try:
        # Download the zip
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        print(f"Extracting {name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the main CSV file (usually all_matches.csv or similar)
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv') and not f.endswith('_info.csv')]
            if not csv_files:
                print(f"No CSV found in {name}")
                return
                
            # The largest file or 'all_matches.csv'
            main_csv = max(csv_files, key=lambda f: zip_ref.getinfo(f).file_size)
            
            target_csv_name = f"{name}.csv"
            target_csv_path = os.path.join(DATA_DIR, target_csv_name)
            
            with zip_ref.open(main_csv) as source, open(target_csv_path, "wb") as target:
                shutil.copyfileobj(source, target)
                
        # Cleanup zip
        os.remove(zip_path)
        print(f"Saved to {target_csv_path}")
    except Exception as e:
        print(f"Failed to download or extract {name}: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for name, url in DATASETS.items():
        download_and_extract(name, url)
        
if __name__ == "__main__":
    main()
