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
        if self.data.get("start_last_workfile")  \
            and last_workfile  \
                and os.path.exists(last_workfile):
            self.log.info("It is set to start last workfile on start.")
        else:
            source_template_file = self.get_custom_template_path()
            staging_dir = tempdir.get_temp_dir(
                self.data["project_name"],
                use_local_temp=True
            )
            spm_filename = os.path.basename(source_template_file)
            last_workfile = os.path.join(staging_dir, spm_filename)
            shutil.copyfile(source_template_file, last_workfile)

        self.launch_context.launch_args.append(last_workfile)

        self.launch_context.env["CURRENT_SPM"] = last_workfile

    def get_custom_template_path(self):
        speedtree_settings = self.data["project_settings"]["speedtree"]
        template_path = speedtree_settings["template_path"]
        if template_path and os.path.exists(template_path):
            return template_path
        executable_path = self.launch_context.env["SPTREE_EXE"]
        template_directory = os.path.dirname(
            os.path.dirname(executable_path)
        )
        template_path = os.path.join(
            template_directory, "tree_templates/Games/Blank.spm")

        return template_path
