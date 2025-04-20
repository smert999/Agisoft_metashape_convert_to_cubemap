# Spherical to Cubemap Converter for Agisoft Metashape

This script `convert_to_cubemap_v007.py` is designed for converting spherical (360°) images into cubemap projection (six-faced cube map) in Agisoft Metashape. The script automatically creates six perspective images for each spherical panorama and corresponding cameras in the project.

## Features

- Conversion of spherical images into six faces of a cubemap projection
- Automatic detection of the project's coordinate system (Y-UP, Z-UP, X-UP)
- Multi-threaded processing for faster conversion
- Adjustable overlap between cube faces for better stitching
- Verification of cube face edge quality
- Preservation of internal and external camera orientation

## System Requirements

- Agisoft Metashape Professional (version 1.8 or higher recommended)
- Python 3.x (included with Metashape)
- OpenCV (automatically installed by the script if needed)

## Installation

1. Download the `convert_to_cubemap_v007.py` file
2. Put the file in a convenient location (e.g., in the Metashape scripts folder)

## Usage

### Project Preparation

1. Before running the script, you need to add spherical images to your Metashape project and correctly determine their position in space (align them).
2. Spherical images must be in equirectangular projection.

### Running the Script

1. In Metashape, select the menu **Tools > Run Script...**
2. In the dialog box that appears, find and select the `convert_to_cubemap_v007.py` file
3. Click the "Open" button to run the script
4. In the dialog box that appears, select a folder to save the created cube face images
5. Enter the overlap value between faces (10° is recommended for reliable stitching)

Alternatively, you can run the script through the Python console in Metashape:
1. Open **Tools > Console**  
2. Enter the command:
   ```python
   exec(open("/path/to/file/convert_to_cubemap_v007.py").read())
   ```

### Operation Parameters

- **Output Folder**: Directory where the cube face images will be saved.
- **Overlap**: Value of overlap between faces in degrees (from 0 to 20). Recommended value: 10°.

## How It Works

1. The script analyzes the project's coordinate system for proper cube face orientation.
2. Six perspective images are created for each spherical camera (front, right, left, top, down, back).
3. New cameras are created in the project with correct position and orientation.
4. Face images are saved in the specified folder with names: `[original_camera_name]_[face].jpg`.

## Results

After running the script, new cameras for each cube face will be added to the project. They can be used for:

- Creating a dense point cloud
- Building a textured model
- Improving alignment quality when working with spherical panoramas

## Usage Tips

- Make sure that spherical images have sufficient resolution to obtain high-quality cube faces.
- If your project uses different types of cameras, it is recommended to disable all non-spherical cameras before running the script.
- Check the conversion results, especially when using non-standard coordinate systems.
- For large projects, the conversion process may take significant time.

## Troubleshooting

- If the script cannot determine the coordinate system, try selecting it manually by changing the value of the `coord_system` variable in the code.
- If you have problems installing OpenCV, perform the installation manually:
  ```
  /path/to/python_metashape/python.exe -m pip install opencv-python
  ```
- If there are issues with cube face stitching, try increasing the overlap value.
