# -*- coding: utf-8 -*-
"""Pre-launch to copy SpeedTree Python Binding Script."""
import os
import pathlib
import filecmp
import site
import stat
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

    def _get_version(self, sdk_folder: pathlib.Path):
        site.addsitedir(pathlib.Path(sdk_folder).as_posix())
        import speedtree.SpeedTree as SpeedTree

        return SpeedTree.__version__

    def _sync_sdk_folder_by_perforce(self, sdk_folder: str):
        try:
            import ayon_perforce.api as perforce_api
            perforce_api.sync(sdk_folder)
            self.log.debug(
                f"Sync the sdk folder:{sdk_folder} to Perforce."
            )

        except ImportError as err:
            self.log.debug(f"Skip syncing folder to perforce as {err}")

    def _force_copy_files(self, src: pathlib.Path, dst: pathlib.Path):
        if dst.is_dir():
            try:
                shutil.copytree(src, dst)
                return
            except FileExistsError as error:
                if (
                    "Cannot create a file when that file already exists:"
                    in str(error)
                ):
                    for sub_path in src.iterdir():
                        self._force_copy_files(sub_path, dst / sub_path.name)

                    return

                raise

        try:
            shutil.copy(src, dst)
        except PermissionError:
            os.chmod(str(dst), stat.S_IWRITE)
            shutil.copy(src, dst)

    def execute(self):
        speedtree_settings = self.data["project_settings"]["speedtree"]
        sdk_folder = os.path.normpath(
            speedtree_settings["sdk_directory"]
        )
        if not sdk_folder and not os.path.exists(sdk_folder):
            raise RuntimeError(
                "Directory not found. Fail to copy the "
                "SDK python binding folder.")

        version = self._get_version(sdk_folder)
        dst_folder = os.path.join(
            SPTREE_ADDON_ROOT, "api", "sdk", "speedtree", version
        )
        self._sync_sdk_folder_by_perforce(sdk_folder)
        python_env = self.launch_context.env["PYTHONPATH"]
        paths = python_env.split(os.pathsep)
        paths.append(dst_folder.as_posix())
        self.launch_context.env["PYTHONPATH"] = os.pathsep.join(paths)
        if dst_folder.exists():
            filecmp.clear_cache()
            if not filecmp.cmp(sdk_folder, dst_folder, shallow=False):
                self.log.info(
                    (
                        "Local SpeedTree SDK folder already exists:\n"
                        f"- {dst_folder}"
                    )
                )
                return

            self.log.info(
                (
                    "Local SpeedTree SDK folder exists but is out of date:\n"
                    f"- {dst_folder}\n"
                    "Force updating..."
                )
            )
            self._force_copy_files(sdk_folder, dst_folder)
            return

        shutil.copytree(sdk_folder, dst_folder)
        self.log.info(
            "SpeedTree Python binding folder "
            f"copied from {sdk_folder} -> {dst_folder}"
        )
