import requests
import json
import os

# Constants for M2M API URL
M2M_URL = 'https://m2m.cr.usgs.gov/api/api/json/stable/'

# User credentials
USERNAME = 'ereinha3'
PASSWORD = 'Allhart0857!'

# Dataset and search parameters
DATASET_NAME = 'SRTM'
BBOX = [44, -124, 45, -123]  # Bounding box for search

def authenticate(username, password):
    print("Authenticating...")
    response = requests.post(M2M_URL + 'login', json={'username': username, 'password': password})
    data = response.json()
    if data['errorCode']:
        print(f"Error during authentication: {data['errorMessage']}")
        return None
    print("Authenticated successfully.")
    return data['data']

def search_srtm_data(api_key, bbox):
    print("Searching for SRTM data...")
    headers = {'X-Auth-Token': api_key}
    payload = {
        'datasetName': DATASET_NAME,
        'spatialFilter': {
            'filterType': 'mbr',
            'lowerLeft': {'latitude': bbox[1], 'longitude': bbox[0]},
            'upperRight': {'latitude': bbox[3], 'longitude': bbox[2]}
        }
    }
    response = requests.post(M2M_URL + 'scene-search', headers=headers, json=payload)
    data = response.json()
    if data['errorCode']:
        print(f"Error during search: {data['errorMessage']}")
        return []
    print("Search completed.")
    return data['data']['results']

def get_available_products(api_key, dataset_name):
    print("Getting available products...")
    headers = {'X-Auth-Token': api_key}
    response = requests.get(M2M_URL + f'datasets/{dataset_name}/products', headers=headers)
    
    print("Response status code:", response.status_code)
    print("Response content:", response.content)  # Print raw response for debugging

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    
    if data['errorCode']:
        print(f"Error getting products: {data['errorMessage']}")
        return []
    
    print("Available products retrieved.")
    return data['data']


def request_download_urls(api_key, granule_ids, product_id):
    print("Requesting download URLs...")
    headers = {'X-Auth-Token': api_key}
    downloads = [{'label': granule_id, 'entityId': granule_id, 'productId': product_id} for granule_id in granule_ids]
    payload = {'downloads': downloads, 'downloadApplication': 'EE'}
    response = requests.post(M2M_URL + 'download-request', headers=headers, json=payload)
    data = response.json()
    if data['errorCode']:
        print(f"Error requesting download URLs: {data['errorMessage']}")
        return []
    print("Download URLs requested.")
    return data['data']['availableDownloads']

def download_files(api_key, download_requests, save_directory):
    print("Downloading files...")
    headers = {'X-Auth-Token': api_key}
    os.makedirs(save_directory, exist_ok=True)  # Create directory if it doesn't exist
    for download_info in download_requests:
        download_url = download_info.get('url')
        if download_url:
            local_filename = os.path.join(save_directory, download_url.split('/')[-1])
            print(f"Downloading {local_filename} ...")
            response = requests.get(download_url, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {local_filename}")
        else:
            print(f"No download URL for granule: {download_info.get('entityId', 'Unknown')}")

def main():
    # Authenticate
    api_key = authenticate(USERNAME, PASSWORD)
    if not api_key:
        return
    
    # Search for SRTM data
    granules = search_srtm_data(api_key, BBOX)
    if granules:
        print(f"Found {len(granules)} granules")
        granule_ids = [granule['entityId'] for granule in granules]

        # Get available products for the dataset
        products = get_available_products(api_key, DATASET_NAME)
        print(f"Available products: {json.dumps(products, indent=2)}")  # Debugging

        if products:
            product_id = products[0]['productId']  # Assuming the first product is suitable

            # Request download URLs
            download_requests = request_download_urls(api_key, granule_ids, product_id)
            if download_requests:
                # Specify save directory
                save_directory = 'downloads'  # Customize this to your desired directory
                # Download the files
                download_files(api_key, download_requests, save_directory)
            else:
                print("No download URLs received.")
        else:
            print("No available products found for the dataset.")
    else:
        print("No granules found")

    # Logout
    requests.post(M2M_URL + 'logout', headers={'X-Auth-Token': api_key})

if __name__ == "__main__":
    main()
