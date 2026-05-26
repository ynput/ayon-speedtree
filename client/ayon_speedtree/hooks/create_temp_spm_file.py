import os
import shutil

from ayon_core.pipeline import tempdir
from ayon_applications import (
    PreLaunchHook,
    LaunchTypes,
    ApplicationLaunchFailed,
)


class CreateTempSpmFile(PreLaunchHook):
    """Create Temp Spm File to SpeedTree.

    The temp spm file would be created in SpeedTree prior to
    the launch of the software if there is no workfile to launch.

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"speedtree"}
    order = 12
    launch_types = {LaunchTypes.local}

    def execute(self):
        workfile_path = self.get_workfile_path()

        self.launch_context.launch_args.append(workfile_path)

        self.launch_context.env["CURRENT_SPM"] = workfile_path

    def get_workfile_path(self):
        workfile_path = self.data.get("workfile_path")
        if workfile_path:
            if not os.path.exists(workfile_path):
                raise ApplicationLaunchFailed(
                    f"Workfile path '{workfile_path}' does not exist"
                )
            return workfile_path

        if self.data.get("start_last_workfile"):
            self.log.info("It is set to start last workfile on start.")
            workfile_path = self.data.get("last_workfile_path")

        if workfile_path and os.path.exists(workfile_path):
            return workfile_path

        source_template_file = self.get_custom_template_path()
        staging_dir = tempdir.get_temp_dir(
            self.data["project_name"],
            use_local_temp=True
        )
        spm_filename = os.path.basename(source_template_file)
        workfile_path = os.path.join(staging_dir, spm_filename)
        shutil.copyfile(source_template_file, workfile_path)
        return workfile_path

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
