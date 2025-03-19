import os
import logging
from . import CommunicationWrapper
import ctypes
import time
import contextlib


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


def _enum_windows_callback(hwnd, windows):
    """Function to get the list of open windows for hacky way to
    save file before passing to SDK to execute the action
    Args:
        hwnd (_type_): _description_
        windows (_type_): _description_

    Returns:
        _type_: _description_
    """
    if user32.IsWindowVisible(hwnd) and user32.IsWindowEnabled(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        windows.append((hwnd, buff.value))
    return True


def get_open_windows():
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    enum_windows_callback_func = WNDENUMPROC(_enum_windows_callback)
    windows = []
    user32.EnumWindows(enum_windows_callback_func, ctypes.byref(ctypes.c_int(len(windows))))
    return windows


def save_file_with_hotkey():
    """Function to save a file using a hotkey (Ctrl+S)

    """
    # Simulate pressing Ctrl+S
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_S, 0, 0, 0)
    time.sleep(0.1)  # Small delay to ensure the key press is registered
    user32.keybd_event(VK_S, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


@contextlib.contextmanager
def set_focus_to_window(window_title):
    """Function to save file before passing it into the headless SDR to publish or
    increment and save file.

    Args:
        window_title (str, optional): Current Ayon tool windows.

    """
    prev_hwnd = user32.FindWindowW(None, window_title)
    hwnd = user32.FindWindowW(None, "SpeedTree  Modeler 10.0.0 ")
    if hwnd:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        save_file_with_hotkey()
    try:
        yield
    finally:
        user32.ShowWindow(prev_hwnd, SW_RESTORE)

