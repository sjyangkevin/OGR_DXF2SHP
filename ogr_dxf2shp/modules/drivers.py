import os
from osgeo import ogr, osr 
from qgis.PyQt.QtWidgets import QListWidgetItem

class DXF2SHP_Driver:
    def __init__(self):
        self.input_file = None # implementation done
        self.output_dir = None # implementation done
        self.input_name = None # implementation done
        self.output_name = None # implementation done
        self.DXF_DRIVER = ogr.GetDriverByName("DXF") # implementation done
        self.ESRI_DRIVER = ogr.GetDriverByName("ESRI Shapefile") 
        self.ORIGINAL_PROJECTION = osr.SpatialReference() # implementation done
        self.TARGET_PROJECTION = osr.SpatialReference() # implementation done
        self.DXF_SOURCE = None # implementation done
        self.ESRI_SOURCE = None 
        self.DXF_LAYERS = [] # implementation done 
        self.SELECTED_DXF_LAYERS = [] # implementation done

    def set_input_file(self, input_file):
        self.input_file = input_file
        input_name = os.path.basename(self.input_file).split('.')[0]
        self.input_name = input_name
    
    def set_output_dir(self, output_dir):
        self.output_dir = output_dir
    
    def set_output_name(self, output_name):
        self.output_name = output_name

    def create_dxf_source(self):
        self.DXF_SOURCE = self.DXF_DRIVER.Open(self.input_file, 0)

    def create_esri_source(self):
        self.ESRI_SOURCE = self.ESRI_DRIVER.CreateDataSource(self.output_dir)

    def set_original_projection(self, EPSG_ID):
        self.ORIGINAL_PROJECTION.ImportFromEPSG(EPSG_ID)

    def set_target_projection(self, EPSG_ID):
        self.TARGET_PROJECTION.ImportFromEPSG(EPSG_ID)

    def recreate_projection_file(self):
        proj_wkt = self.TARGET_PROJECTION.MorphToESRI().ExportToWkt()
        with open(os.path.join(self.output_dir, self.output_name + '.prj'), 'w') as f:
            f.write(proj_wkt)

    def set_dxf_layers(self):
        layers = self.DXF_SOURCE.ExecuteSQL("SELECT DISTINCT Layer FROM entities")
        layer = self.DXF_SOURCE.GetLayer()

        loaded_layers = []
        for i in range(0, layers.GetFeatureCount()):
            layer_name = layers.GetFeature(i).GetFieldAsString(0)
            layer.SetAttributeFilter("Layer='%s'" %layer_name)
            loaded_layers.append(layer_name)
        self.DXF_LAYERS = loaded_layers





