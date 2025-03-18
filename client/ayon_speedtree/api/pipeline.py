"""Pipeline tools for AYON Speedtree integration."""
import os
import ast
import json
import shutil
import logging
import tempfile
import pyblish.api
from ayon_core.host import HostBase, IWorkfileHost, ILoadHost, IPublishHost
from ayon_core.pipeline import (
    register_creator_plugin_path,
    register_loader_plugin_path,
    AYON_CONTAINER_ID,
    registered_host
)
from ayon_core.pipeline.context_tools import get_global_context

from ayon_core.settings import get_current_project_settings
from ayon_core.lib import register_event_callback
from ayon_core.tools.utils import host_tools
from ayon_speedtree import SPTREE_ADDON_ROOT
from .lib import get_workdir, execute_sptree_command

import speedtree.SpeedTree as SpeedTree


METADATA_SECTION = "avalon"
SPTREE_SECTION_NAME_CONTEXT = "context"
SPTREE_METADATA_CREATE_CONTEXT = "create_context"
SPTREE_SECTION_NAME_INSTANCES = "instances"
SPTREE_SECTION_NAME_CONTAINERS = "containers"


log = logging.getLogger("ayon.hosts.speedtree")


class SpeedtreeHost(HostBase, IWorkfileHost, ILoadHost, IPublishHost):
    name = "speedtree"

    @staticmethod
    def show_tools_dialog():
        """Show tools dialog with actions leading to show other tools."""
        show_tools_dialog()

    def install(self):
        # Create workdir folder if does not exist yet
        workdir = os.getenv("AYON_WORKDIR")
        if not os.path.exists(workdir):
            os.makedirs(workdir)

        plugins_dir = os.path.join(SPTREE_ADDON_ROOT, "plugins")
        publish_dir = os.path.join(plugins_dir, "publish")
        load_dir = os.path.join(plugins_dir, "load")
        create_dir = os.path.join(plugins_dir, "create")

        pyblish.api.register_host("speedtree")
        pyblish.api.register_plugin_path(publish_dir)
        register_loader_plugin_path(load_dir)
        register_creator_plugin_path(create_dir)

        register_event_callback("application.launched", self.initial_app_launch)

    def get_current_project_name(self):
        """
        Returns:
            Union[str, None]: Current project name.
        """

        return self.get_current_context().get("project_name")

    def get_current_folder_path(self):
        """
        Returns:
            Union[str, None]: Current folder path.
        """

        return self.get_current_context().get("folder_path")

    def get_current_task_name(self):
        """
        Returns:
            Union[str, None]: Current task name.
        """

        return self.get_current_context().get("task_name")

    def get_current_context(self):
        context = get_current_workfile_context()
        if not context:
            return get_global_context()
        if "project_name" in context:
            return context
        # This is legacy way how context was stored
        return {
            "project_name": context.get("project_name"),
            "folder_path": context.get("folder_path"),
            "task_name": context.get("task_name")
        }

    def get_current_workfile(self):
        work_dir = get_workdir()
        txt_dir = os.path.join(
            work_dir, ".sptree_metadata").replace(
                "\\", "/"
        )
        with open (f"{txt_dir}/current_file.txt", "r") as current_file:
            content = str(current_file.read())
            filepath = content.rstrip('\x00')
            current_file.close()
            return filepath

    def workfile_has_unsaved_changes(self):
        # Pop-up dialog would be located to ask if users
        # save scene if it has unsaved changes
        return True

    def get_workfile_extensions(self):
        return [".spm"]

    def open_workfile(self, filepath):
        filepath, _ = open_workfile(filepath)
        set_current_file(filepath=filepath)
        return filepath

    def save_workfile(self, filepath=None):
        if not filepath:
            filepath = self.get_current_workfile()
        filepath, context = open_workfile(filepath)
        options = SpeedTree.StpSaveSpmOptions()
        saved = context.saveSpeedTreeFile(filepath, options)
        if saved:
            return filepath
        return None

    def initial_app_launch(self):
        """Triggers on launch of the communication server for Speedtree.

        Usually this aligns roughly with the start of Speedtree.
        """
        #TODO: figure out how to deal with the last workfile issue
        set_current_file()
        context = get_global_context()
        save_current_workfile_context(context)


def save_current_workfile_context(context):
    """Save current workfile context data to `.sptree_metadata/{workfile}/key`

    This persists the current in-memory context to be set for a specific
    workfile on disk. Usually used on save to persist the local sessions'
    workfile context on save.

    The context data includes things like the project name, folder path,
    etc.

    Args:
        context (dict): context data

    """
    return write_context_metadata(SPTREE_SECTION_NAME_CONTEXT, context)


def write_context_metadata(metadata_key, context):
    """Write context data into the related json
    which stores in .sptree_metadata/key folder
    in the project work directory.

    The context data includes the project name, folder path
    and task name.

    Args:
        metadata_key (str): metadata key
        context (dict): context data
    """
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".sptree_metadata", metadata_key).replace(
            "\\", "/"
        )
    os.makedirs(json_dir, exist_ok=True)
    json_file = f"{json_dir}/{metadata_key}.json"
    if os.path.exists(json_file):
        with open (json_file, "r") as file:
            value = json.load(file)
            if value == context:
                return
    with open (json_file, "w") as file:
        value = json.dumps(context)
        file.write(value)
        file.close()


def get_current_workfile_context():
    """Function to get the current context data from the related
    json file in .sptree_metadata/context folder

    The current context data includes thing like project name,
    folder path and task name.

    Returns:
        list: list of context data
    """
    return get_load_context_metadata()


def get_load_context_metadata():
    """Get the context data from the related json file
    ("context.json") which stores in .sptree_metadata/context
    folder in the project work directory.

    The context data includes the project name, folder path and
    task name.

    Returns:
        list: context data
    """
    file_content = {}
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".sptree_metadata", SPTREE_SECTION_NAME_CONTEXT).replace(
            "\\", "/"
        )
    if not os.path.exists(json_dir):
        return file_content
    file_list = os.listdir(json_dir)
    if not file_list:
        return file_content
    for file in file_list:
        with open (f"{json_dir}/{file}", "r") as data:
            content = ast.literal_eval(str(data.read().strip()))
            file_content.update(content)
            data.close()
    return file_content



def set_current_file(filepath=None):
    """Function to store current workfile path

    Args:
        filepath (str, optional): current workfile path. Defaults to None.
    """
    work_dir = get_workdir()
    txt_dir = os.path.join(
        work_dir, ".sptree_metadata").replace(
            "\\", "/"
    )
    os.makedirs(txt_dir, exist_ok=True)
    txt_file = f"{txt_dir}/current_file.txt"
    if filepath is None:
        with open(txt_file, "w"):
            pass
        return filepath
    filepath_check = tmp_current_file_check()
    if filepath_check.endswith("spm"):
        filepath = os.path.join(
            os.path.dirname(filepath), filepath_check).replace("\\", "/")
    with open (txt_file, "w") as current_file:
        current_file.write(filepath)
        current_file.close()


def tmp_current_file_check():
    """Function to find the latest .spm file used
    by the user in Speedtree.

    Returns:
        file_content (str): the filepath in .spm format.
            If the filepath does not end with '.spm' format,
            it returns None.
    """
    output_file = tempfile.NamedTemporaryFile(
        mode="w", prefix="a_sptree_cfc", suffix=".txt", delete=False
    )
    output_filepath = output_file.name.replace("\\", "/")
    output_file.write(output_filepath)
    output_file.close()
    with open(output_filepath) as data:
        file_content = str(data.read().strip()).rstrip('\x00')
    os.remove(output_filepath)
    return file_content


def show_tools_dialog():
    """Show dialog with tools.

    Dialog will stay visible.
    """
    from ayon_speedtree.api import tools_ui

    tools_ui.show_tools_dialog()


def show_creator():
    host_tools.show_creator()


def show_loader():
    host_tools.show_loader(use_context=True)


def show_publisher():
    host_tools.show_publish()


def show_manager():
    host_tools.show_scene_inventory()


def show_workfiles():
    host_tools.show_workfiles(use_context=True)


def open_workfile(filepath):
    context = SpeedTree.StpContext()
    context.new()

    # Set maximum CPU threads
    context.setMaxCpuThreads(4)

    # Load a SpeedTree file
    loaded, _ = context.loadSpeedTreeFile(filepath)
    if loaded:
        return filepath, context

    return None, context
