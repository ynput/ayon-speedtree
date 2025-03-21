import os
import logging
from . import CommunicationWrapper
import ctypes
import time
import contextlib

import speedtree.SpeedTree as SpeedTree


log = logging.getLogger("speedtree.lib")


# Define necessary constants and structures
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_CONTROL = 0x11
VK_S = 0x53
KEYEVENTF_KEYUP = 0x0002
SW_RESTORE = 9


def get_workdir() -> str:
    """Return the currently active work directory"""
    return os.environ["AYON_WORKDIR"]


def execute_sptree_command(zscript, communicator=None):
    """Execute Speedtree command.

    Note that this will *not* wait around for the Speedtree command to run or
    for its completion. Nor will errors in the script be detected or raised.

    """
    if not communicator:
        communicator = CommunicationWrapper.communicator
    print(f"Executing speedtree command: {zscript}")
    return communicator.execute_sptree_command(zscript)


def _save_file_with_hotkey():
    """Function to save a file using a hotkey (Ctrl+S)

    """
    # Simulate pressing Ctrl+S
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_S, 0, 0, 0)
    time.sleep(0.1)  # Small delay to ensure the key press is registered
    user32.keybd_event(VK_S, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


@contextlib.contextmanager
def save_scene(window_title):
    """Hacky function to save file during context before passing
    it into the headless SDR to publish or increment and save file

    Args:
        window_title (str, optional): Current Ayon tool windows.

    """
    prev_hwnd = user32.FindWindowW(None, window_title)
    hwnd = user32.FindWindowW(None, "SpeedTree  Modeler 10.0.0 ")
    if hwnd:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        _save_file_with_hotkey()
    try:
        yield
    finally:
        user32.ShowWindow(prev_hwnd, SW_RESTORE)


def export_model(current_file: str, fbx_filepath: str, xml_filepath: str):
    """Function to export model in fbx format along with the xml file.

    Args:
        current_file (str): current file
        fbx_filepath (str): fbx output filepath
        xml_filepath (str): xml output filepath
    """
    resource_path = os.path.dirname(os.path.dirname(os.environ["SPTREE_EXE"]))
    resource_path = os.path.normpath(resource_path)
    SpeedTree.StpSetExportResourcePath(resource_path)
    context = SpeedTree.StpContext()
    context.new()
    loaded, _ = context.loadSpeedTreeFile(current_file)
    if loaded:
        # Configure FBX export options
        export_options = SpeedTree.StpVfxExportOptions()
        export_options.initVfxExportOptions()

        # Set FBX-specific options
        export_options.fbxCacheCompatible = True
        export_options.fbxCacheFormat = SpeedTree.StpFbxCacheFormat.STP_FBX_CACHE_FORMAT_MCX
        export_options.fbxAxis = SpeedTree.StpFbxAxis.STP_FBX_AXIS_MAYA_Y_UP
        export_options.fbxBonesSmooth = True
        # Set other export options
        export_options.include3dGeometry = True
        export_options.includeBones = True
        export_options.animationWind = True
        export_options.animationFPS = 30
        export_options.textureSkipWriting = True
        fbx_success = context.exportForVfx(fbx_filepath, export_options)
        xml_success = context.exportForVfx(xml_filepath, export_options)
        # Cleanup
        if fbx_success and xml_success:
            log.debug("Successfully export tree model.")

    context.delete()


def load_spm_file(spm_file, communicator=None):
    """Load spm file for either loading existing file or refreshing purpose.
    There is no way in SpeedTree to increment and save for current workfile.
    Ayon needs to always save and re-load the spm file again for getting
    the latest version.
    """
    if not communicator:
        communicator = CommunicationWrapper.communicator
    print(f"Loading Spm file: {spm_file}")
    speedtree_executable = os.environ["SPTREE_EXE"]
    return communicator.replace_process([speedtree_executable, spm_file])
