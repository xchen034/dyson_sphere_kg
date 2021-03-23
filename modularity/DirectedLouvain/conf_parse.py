import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from modularity.utils.io_utils import load_config

class ModularityParse:
    def __init__(self, config_path, **kwargs):
        self._config = load_config(config_path)

    def _get_graph_setting(self, graph_setting_key=None, **kwargs):
        if graph_setting_key is None:
            graph_setting_key = "graph_setting"
        self._graph_setting = self._config.get(graph_setting_key, {})

    def _get_modularity_setting(self, modularity_setting_key=None, **kwargs):
        if modularity_setting_key is None:
            modularity_setting_key = "modularity_setting"
        self._modularity_setting = self._config.get(modularity_setting_key, {})

    def _get_outfile(self, **kwargs):
        self._outfile = self._config.get("outfile")

    @property
    def graph_setting(self, **kwargs):
        return self._graph_setting

    @property
    def modularity_setting(self, **kwargs):
        return self._modularity_setting

    @property
    def outfile(self, **kwargs):
        return self._outfile

    def __call__(self, graph_setting_key=None, modularity_setting_key=None, **kwargs):
        self._get_graph_setting(graph_setting_key=graph_setting_key)
        self._get_modularity_setting(modularity_setting_key=modularity_setting_key)
        self._get_outfile(**kwargs)