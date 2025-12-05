# -*- coding: utf-8 -*-
"""Creator plugin for model."""
from ayon_speedtree.api import plugin


class CreateModel(plugin.SpeedTreeCreator):
    """Creator plugin for Model."""
    identifier = "io.ayon.creators.speedtree.model"
    label = "Model"
    product_type = "model"
    product_base_type = "model"
    icon = "cube"
