from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
)


class ProductTypeItemModel(BaseSettingsModel):
    _layout = "compact"
    product_type: str = SettingsField(
        title="Product type",
        description="Product type name",
    )
    label: str = SettingsField(
        "",
        title="Label",
        description="Label to display in UI for the product type",
    )


class CreateModelModel(BaseSettingsModel):
    product_type_items: list[ProductTypeItemModel] = SettingsField(
        default_factory=list,
        title="Product type items",
        description=(
            "Optional list of product types that this plugin can create."
        )
    )


class CreatPluginsModel(BaseSettingsModel):
    CreateModel: CreateModelModel = SettingsField(
        default_factory=CreateModelModel,
        title="Create Model",
        description="Creator for model product"
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
    create: CreatPluginsModel = SettingsField(
        default_factory=CreatPluginsModel,
        title="Create Plugins",
    )


DEFAULT_SPTREE_VALUES = {
    "sdk_directory": "/path/to/bindings/python/python3.9",
    "template_path": ""
}
