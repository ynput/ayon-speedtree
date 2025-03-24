# -*- coding: utf-8 -*-
"""Pre-launch to copy SpeedTree Python Binding Script."""
import os
import shutil
from ayon_applications import PreLaunchHook, LaunchTypes
from ayon_speedtree import SPTREE_ADDON_ROOT


class SpeedtreeStartupScript(PreLaunchHook):
    """Copy Python Binding Folder from SpeedTree Pipeline SDK to
    the sdk folder, and so that the addon can get the correct
    PYTHONPATH to run the script.
    """
    app_groups = {"speedtree"}
    launch_types = {LaunchTypes.local}

    def execute(self):
        speedtree_settings = self.data["project_settings"]["speedtree"]
        sdk_folder = os.path.normpath(
            speedtree_settings["sdk_directory"]
        )
        if not sdk_folder and not os.path.exists(sdk_folder):
            raise RuntimeError(
                "Directory not found. Fail to copy the "
                "SDK python binding folder.")
        dst_folder = os.path.join(
            SPTREE_ADDON_ROOT, "api", "sdk", "speedtree"
        )
        if os.path.exists(dst_folder):
            self.log.info(
                "SpeedTree Python Binding Folder is already copied."
            )
            return

        shutil.copytree(sdk_folder, dst_folder)
        self.log.info(
            "SpeedTree Python binding folder "
            f"copied from {sdk_folder} to {dst_folder}"
        )
