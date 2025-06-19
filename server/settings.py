from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,

)


class SpeedtreeSettings(BaseSettingsModel):
    sdk_directory: str = SettingsField(
        "/path/to/bindings/python/python3.9/speedtree",
        title="Pipeline SDK directory",
        description=("The path to get the python binding folder "
                     "to be used in SpeedTree Integration.")
    )
    template_path: str = SettingsField(
        "", title="Custom Template Path",
        description=("The path to get the custom template "
                     "to be used in SpeedTree Integration.")
    )


DEFAULT_SPTREE_VALUES = {
    "sdk_directory": "/path/to/bindings/python/python3.9",
    "template_path": ""
}
