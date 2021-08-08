import os
from osgeo import ogr, osr 
from .attrparser import parse_attribute_file
from qgis.utils import QgsMessageLog

class DXF2SHP_Driver:
    def __init__(self):
        self.input_file = None
        self.output_dir = None
        self.input_name = None
        self.output_name = None
        self.DXF_DRIVER = ogr.GetDriverByName("DXF")
        self.ESRI_DRIVER = ogr.GetDriverByName("ESRI Shapefile")
        self.ORIGINAL_PROJECTION = osr.SpatialReference()
        self.TARGET_PROJECTION = osr.SpatialReference()
        self.DXF_SOURCE = None
        self.ESRI_SOURCE = None
        self.DXF_LAYERS = [] 
        self.SELECTED_DXF_LAYERS = []
        self.ATTRIBUTE_FILE = None
        self.SELECTED_ATTRIBUTE_COLUMN = None


    def set_input_file(self, input_file):
        self.input_file = input_file
        input_name = os.path.basename(self.input_file).split('.')[0]
        self.input_name = input_name
    

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir
    

    def set_output_name(self, output_name):
        self.output_name = output_name


    def set_attribute_file(self, file_path):
        self.ATTRIBUTE_FILE = file_path

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
        loaded_layers.sort()
        self.DXF_LAYERS = loaded_layers


    def read_attribute_file(self):
        columns, data = parse_attribute_file(self.ATTRIBUTE_FILE)
        return columns, data

    def __call__(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # set output name the same as input name if output name not specified
        if self.output_name == None:
            self.output_name = os.path.basename(self.input_file).split('.')[0]

        layers = self.DXF_SOURCE.ExecuteSQL("SELECT DISTINCT Layer FROM entities")
        layer = self.DXF_SOURCE.GetLayer()

        if self.ATTRIBUTE_FILE is not None:
            
            columns, attr_data = self.read_attribute_file()

            loaded_data = []
            for i in range(0, layers.GetFeatureCount()):
                layer_name = layers.GetFeature(i).GetFieldAsString(0)
                layer.SetAttributeFilter("Layer='%s'" %layer_name)
                if layer_name in self.SELECTED_DXF_LAYERS:
                    load = {}
                    for data in attr_data:
                        if data[self.SELECTED_ATTRIBUTE_COLUMN] == layer_name:
                            for col in columns:
                                load[col] = data[col]
                            for feature in layer:
                                load['geom'] = feature.GetGeometryRef().ExportToWkt()

                    loaded_data.append(load)
            
            # currently use str as type only and work on polygon feature
            shapefile_layer = self.ESRI_SOURCE.CreateLayer(self.output_name, self.ORIGINAL_PROJECTION, ogr.wkbPolygon)

            for col in columns:
                shapefile_layer.CreateField(ogr.FieldDefn(col, ogr.OFTString))
            
            srs_transform = osr.CoordinateTransformation(self.ORIGINAL_PROJECTION, self.TARGET_PROJECTION)

            layer_defn = shapefile_layer.GetLayerDefn()
            for i in range(layer_defn.GetFieldCount()):
                QgsMessageLog.logMessage(layer_defn.GetFieldDefn(i).GetName(), "OGR DXF2SHP")

            for _data in loaded_data:
                
                _feature = ogr.Feature(shapefile_layer.GetLayerDefn())

                for col in columns:
                    _feature.SetField(col, _data[col])
                
                linework = ogr.CreateGeometryFromWkt(_data['geom'])
                linework.Transform(srs_transform)
                pts = linework.GetPoints()
                ring = ogr.Geometry(ogr.wkbLinearRing)
                for pt in pts:
                    ring.AddPoint(pt[0], pt[1])
                polygon = ogr.Geometry(ogr.wkbPolygon)
                polygon.AddGeometry(ring)
                QgsMessageLog.logMessage(polygon.ExportToWkt(), "OGR DXF2SHP")
                _feature.SetGeometry(polygon)
                shapefile_layer.CreateFeature(_feature)

                _feature = None
                del linework, pts, ring
            
            # over-write the projection file
            self.TARGET_PROJECTION.MorphToESRI()
            with open(os.path.join(self.output_dir, self.output_name + '.prj'), 'w') as f:
                f.write(self.TARGET_PROJECTION.ExportToWkt())

            self.ESRI_SOURCE = None

        else:

            # -----
            # TODO
            # -----
            pass
