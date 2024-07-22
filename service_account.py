import ee
import os
import time

def initialize_earth_engine():
    # Authenticate using the service account credentials
    # Replace 'service-account-key.json' with your actual service account key file path
    service_account = '.private-key.json'
    credentials = ee.ServiceAccountCredentials('service-account@dufek-lab.iam.gserviceaccount.com', service_account)
    ee.Initialize(credentials)

def export_image_to_geotiff(image, file_path):
    # Define the export parameters
    export_params = {
        'image': image,
        'description': 'exported_image',  # Description for the export task
        'folder': file_path,  # GDrive folder to save the exported file in
        'scale': 30,  # Spatial resolution in meters
        'fileFormat': 'GeoTIFF',  # Export format
        'region': image.geometry().bounds(),  # Region to export
        'maxPixels': 1e9  # Maximum number of pixels to export (adjust as needed)
    }

    # Start the export task
    task = ee.batch.Export.image.toDrive(**export_params)
    task.start()

    # Wait for the export to complete
    while task.active():
        print('Exporting...')
        time.sleep(10)  # Adjust sleep interval as needed

    print('Export completed!')

    # Check task status
    if task.status()['state'] == 'COMPLETED':
        print('Downloading file...')
        # Download the file from Google Drive if needed
        # Alternatively, you can copy the file from the Google Drive folder where it's saved

def main():
    try:
        initialize_earth_engine()

        # Example: Query and export imagery
        point = ee.Geometry.Point([-122.08, 37.38])
        image_collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
            .filterBounds(point) \
            .filterDate('2020-01-01', '2020-12-31') \
            .sort('CLOUD_COVER') \
            .first()

        # Export the selected image to GeoTIFF
        output_file_path = 'DufekLab'  # Replace with your desired file path
        export_image_to_geotiff(image_collection, output_file_path)

    except ee.EEException as e:
        print('Earth Engine error:', e)

if __name__ == '__main__':
    main()
