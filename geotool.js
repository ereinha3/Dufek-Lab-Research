// Import the Earth Engine API library
const { EarthEngine } = require('@google/earthengine');

// Initialize Earth Engine API
const earthEngine = new EarthEngine({
  keyFilename: 'dufek-lab-31d54483b85b.json',  // Path to your service account key file
});

// Define your point of interest (latitude, longitude)
const latitude = 44.6082;  // Example latitude (replace with your desired latitude)
const longitude = -122.9180;  // Example longitude (replace with your desired longitude)

// Authenticate with Earth Engine
earthEngine.initialize()
  .then(() => {
    // Define a point as a GEE geometry object
    const point = ee.Geometry.Point([longitude, latitude]);

    // Load a Landsat image collection for the specified location and time range
    const collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
      .filterBounds(point)
      .filterDate('2024-01-01', '2024-12-31')  // Adjust date range as per your requirement
      .sort('CLOUD_COVER')
      .first();  // Get the least cloudy image

    // Print the metadata of the image
    console.log('Selected image metadata:', collection);

    // Select the bands you want to download (e.g., RGB bands)
    const bands = ['B4', 'B3', 'B2'];

    // Clip the image to your point of interest
    const clippedImage = collection.clip(point);

    // Define the export parameters
    const exportParams = {
      image: clippedImage.select(bands),  // Select bands to export
      description: 'landsat_image',  // Description for the exported file
      scale: 30,  // Spatial resolution in meters (e.g., 30 meters for Landsat)
      region: point.buffer(5000).bounds(),  // Add buffer around the point and export the bounds
      fileFormat: 'GeoTIFF',  // Export format
    };

    // Export the image to Google Drive
    earthEngine.exportImageToDrive(exportParams)
      .then(() => {
        console.log('Exporting image. Check your Google Drive for the file.');
      })
      .catch(err => {
        console.error('Error exporting image:', err);
      });
  })
  .catch(err => {
    console.error('Error initializing Earth Engine:', err);
  });
