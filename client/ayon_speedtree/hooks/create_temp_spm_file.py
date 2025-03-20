import os
from ayon_applications import PreLaunchHook, LaunchTypes


class CreateTempSpmFile(PreLaunchHook):
    """Create Temp Spm File to SpeedTree.

    The temp spm file would be created in SpeedTree prior to 
    the launch of the software if there is no last workfile

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"speedtree"}
    order = 10
    launch_types = {LaunchTypes.local}

    def execute(self):
        last_workfile = self.data.get("last_workfile_path")
        if not self.data.get("start_last_workfile") or \
            not last_workfile or \
                not os.path.exists(last_workfile):
            self.log.info("It is set to not start last workfile on start.")
            return
