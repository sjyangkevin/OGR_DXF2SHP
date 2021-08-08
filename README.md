## OGR DXF2SHP - A QGIS Plugin to Convert .DXF Files to ESRI Shapefiles

The plugin loads all of the layers in a .DXF file, and it extracts geometries from those layers selected by the users.  
  
User can specify whether to insert attributes to those extracted geometries by providing an .CSV file that stores data.  

The plugin will load all the records from the .CSV file, and insert those data into selected geometries.

## Work Procedures

1. Select an .DXF file as input.
2. Select an output directory to store shapefiles (e.g. .shp, .prj, ...).
3. Enter the name for the output shapefiles (optional), if it is empty, then the shapefiles have the same name as input.
4. Select the projection (original projection) of the current .DXF file.
5. Select the projection (target projection) of the output shapefile should be.
6. Insert an attribute file (the .CSV file that contains that to be inserted into geometries), it is optional.
7. Select the layers to extract geometries from .DXF files, if attribute file is inputed, select the column to map data. The column should contains the layers name exactly **the same as** the selected layers from .DXF file (same number of records as number of selected layers).
8. Click 'validate' button, to validate data mapping.
9. Click 'Ok' to run the conversion.

## Issues

1. Current version only works for **polygon** features in the .DXF file.
2. When the field_name in the attribute file is over 10 characters, the field_name cannot be created correctly.
3. Help button in the tool is not working, since the edit of help document is not completed yet.

## Future Works

1. Enable functionalities for converting other geometries such as point, polyline, etc.
2. Fix the field_name creation bug in attribute file loading.
3. Enable loading attribute data from databases such as Postgres, Oracle, etc., and interaction with databases.

