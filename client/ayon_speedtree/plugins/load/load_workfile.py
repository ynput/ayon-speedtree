import os
from ayon_core.pipeline import load
from ayon_core.pipeline import (
    registered_host,
    get_current_context,
    Anatomy,
)
from ayon_core.pipeline.workfile import (
    get_workfile_template_key_from_context,
    get_last_workfile_with_version,
)
from ayon_core.pipeline.template_data import get_template_data_with_names
from ayon_speedtree.api.pipeline import get_current_workfile_context

from ayon_core.pipeline.version_start import get_versioning_start


class WorkfileLoader(load.LoaderPlugin):
    """SpeedTree Workfile Loader."""

    product_types = {"workfile"}
    representations = {"spm"}
    order = -9
    icon = "code-fork"
    color = "white"
    label = "Load Workfile"

    def load(self, context, name=None, namespace=None, data=None):
        file_path = os.path.normpath(
            self.filepath_from_context(context)
        )
        if not os.path.exists(file_path):
            raise FileExistsError("The loaded file not found.")


        host = registered_host()
        work_context = get_current_workfile_context()
        project_name = work_context.get("project_name")
        folder_path = work_context.get("folder_path")
        task_name = work_context.get("task_name")

        if not folder_path:
            current_context = get_current_context()
            project_name = current_context.get("project_name")
            folder_path = current_context.get("folder_path")
            task_name = current_context.get("task_name")

        host_name = "speedtree"
        template_key = get_workfile_template_key_from_context(
            project_name,
            folder_path,
            task_name,
            host_name,
        )
        anatomy = Anatomy(project_name)

        data = get_template_data_with_names(
            project_name, folder_path, task_name, host_name
        )

        data["root"] = anatomy.roots

        work_template = anatomy.get_template_item("work", template_key)

        extensions = host.get_workfile_extensions()
        extension = extensions[0]
        data["ext"] = extension.lstrip(".")

        work_root = work_template["directory"].format_strict(data)
        version = get_last_workfile_with_version(
            work_root, work_template["file"].template, data, extensions
        )[1]

        if version is None:
            version = get_versioning_start(
                project_name,
                "tvpaint",
                task_name=task_name,
                task_type=data["task"]["type"],
                product_type="workfile"
            )
        else:
            version += 1

        data["version"] = version

        filename = work_template["file"].format_strict(data)
        path = os.path.join(work_root, filename)
        host.save_workfile(path)
