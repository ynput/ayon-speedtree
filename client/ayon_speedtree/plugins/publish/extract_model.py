import os
import pyblish.api
from ayon_core.pipeline import publish
from ayon_core.pipeline.publish import (
    AYONPyblishPluginMixin
)
from ayon_speedtree.api.lib import save_scene, export_model



class ExtractModel(publish.Extractor,
                   AYONPyblishPluginMixin):
    """
    Extract PolyMesh(.fbx, .xml) in SpeedTree
    """

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Model"
    hosts = ["speedtree"]
    families = ["model"]

    def process(self, instance):

        stagingdir = self.staging_dir(instance)
        fbx_filename = f"{instance.name}.fbx"
        fbx_filepath = os.path.join(stagingdir, fbx_filename)
        fbx_filepath = os.path.normpath(fbx_filepath)

        xml_filename = f"{instance.name}.xml"
        xml_filepath = os.path.join(stagingdir, xml_filename)
        xml_filepath = os.path.normpath(xml_filepath)

        with save_scene("Ayon Publisher"):
            current_file = instance.context.data["current_file"]
            export_model(current_file, fbx_filepath, xml_filepath)

        if "representations" not in instance.data:
            instance.data["representations"] = []
        fbx_representation = {
        "name": "fbx",
        "ext": "fbx",
        "files": fbx_filename,
        "stagingDir": stagingdir,
        }
        xml_representation = {
        "name": "xml",
        "ext": "xml",
        "files": xml_filename,
        "stagingDir": stagingdir,
        }
        instance.data["representations"].extend(
            [fbx_representation, xml_representation]
        )
        self.log.info(
            "Extracted instance '%s' to: %s" % (instance.name, fbx_filepath)
        )
        self.log.info(
            "Extracted instance '%s' to: %s" % (instance.name, xml_filepath)
        )
