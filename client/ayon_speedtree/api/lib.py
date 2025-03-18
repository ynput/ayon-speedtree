import os
import logging
from . import CommunicationWrapper


log = logging.getLogger("speedtree.lib")


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
