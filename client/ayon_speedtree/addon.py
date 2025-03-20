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
        new_python_paths = [
            os.path.join(
                SPTREE_ADDON_ROOT, "api", "sdk")
        ]
        old_python_path = env.get("PYTHONPATH") or ""
        for path in old_python_path.split(os.pathsep):
            if not path:
                continue
            norm_path = os.path.normpath(path)
            if norm_path not in new_python_paths:
                new_python_paths.append(norm_path)
        env["PYTHONPATH"] = os.pathsep.join(new_python_paths)

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
