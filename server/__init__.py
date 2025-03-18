from typing import Type

from ayon_server.addons import BaseServerAddon

from .settings import SpeedtreeSettings, DEFAULT_SPTREE_VALUES


class SpeedtreeAddon(BaseServerAddon):
    settings_model: Type[SpeedtreeSettings] = SpeedtreeSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_SPTREE_VALUES)
