import os
import shutil
from ayon_applications import PreLaunchHook, LaunchTypes
from ayon_core.pipeline import tempdir


class CreateTempSpmFile(PreLaunchHook):
    """Create Temp Spm File to SpeedTree.

    The temp spm file would be created in SpeedTree prior to 
    the launch of the software if there is no last workfile

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"speedtree"}
    order = 12
    launch_types = {LaunchTypes.local}

    def execute(self):
        last_workfile = self.data.get("last_workfile_path")
        if self.data.get("start_last_workfile") and last_workfile:
            self.log.info("It is set to not start last workfile on start.")
        else:
            executable_path = self.launch_context.env["SPTREE_EXE"]
            template_directory = os.path.dirname(os.path.dirname(executable_path))
            staging_dir = tempdir.get_temp_dir(
                self.data["project_name"],
                use_local_temp=True
            )
            source_template_file = os.path.join(
                template_directory, "tree_templates/Games/Blank.spm")
            last_workfile = os.path.join(staging_dir, "Blank.spm")
            shutil.copyfile(source_template_file, last_workfile)
            self.launch_context.launch_args.append(last_workfile)

        self.launch_context.env["CURRENT_SPM"] = last_workfile

