import argparse
import requests
from src.data.constants import RAW_DATA_LOCAL_DIRECTORY, RAW_DATA_LOCAL_FILENAME, RAW_DATA_URL


def import_raw_data(force: bool = False) -> None:
    """Imports the raw data from the bucket"""

    # Create the destination directory if not exists
    RAW_DATA_LOCAL_DIRECTORY.mkdir(parents=False, exist_ok=True)

    # Check whether the local file already exists or not
    if RAW_DATA_LOCAL_FILENAME.exists() and not force:
        print("Raw data has already been downloaded. Skipping")
        return

    # Downloading using requests
    print(f"Downloading {RAW_DATA_URL} into {RAW_DATA_LOCAL_FILENAME}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(RAW_DATA_URL, headers=headers)
    response.raise_for_status()

    # Writing the output file
    with RAW_DATA_LOCAL_FILENAME.open("wb") as f:
        f.write(response.text.encode('utf-8'))

    print(f"Raw data successfull downloaded at {RAW_DATA_LOCAL_FILENAME}.")
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', action='store_true')
    args = parser.parse_args()
    import_raw_data(force=args.force)
