import os
from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__

SPTREE_ADDON_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_launch_script_path():
    return os.path.join(
        SPTREE_ADDON_ROOT,
        "api",
        "launch_script.py"
    )


class SpeedtreeAddon(AYONAddon, IHostAddon):
    name = "speedtree"
    version = __version__
    host_name = "speedtree"

    def add_implementation_envs(self, env, app):
        # Set default environments if are not set via settings
        defaults = {
            "AYON_LOG_NO_COLORS": "1",
            "WEBSOCKET_URL": "ws://localhost:6010"
        }
        for key, value in defaults.items():
            if not env.get(key):
                env[key] = value

        # Remove auto screen scale factor for Qt
        env.pop("QT_AUTO_SCREEN_SCALE_FACTOR", None)

    def get_launch_hook_paths(self, app):
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(SPTREE_ADDON_ROOT, "hooks")
        ]

    def get_workfile_extensions(self):
        return [".spm"]
