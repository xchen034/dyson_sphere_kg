import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

import shutil
from tqdm import tqdm
import math

from modularity.DirectedLouvain.multi_round import MultiCommunity
from modularity.knowledge_fusion.get_seed_graph import GetSeedGraph

class ModuWithRelAndAttr:
    def __init__(self, graph_setting, modularity_setting, attr_modularity_setting, attr_lower_bounds=None, attr_config=None, **kwargs):
        self.graph_setting = graph_setting
        self.modularity_setting = modularity_setting
        self.attr_modularity_setting = attr_modularity_setting
        self.attr_lower_bounds = attr_lower_bounds
        self.attr_config = attr_config
        self.modularity = MultiCommunity(**self.graph_setting, **kwargs)
        self.is_dual_graph = self.modularity.is_dual_graph

    def load_graph(self, graph_triples=None, head_triples=None, tail_triples=None, rel_triples=None, **kwargs):
        self.modularity.load_graph(graph_triples=graph_triples, head_triples=head_triples, tail_triples=tail_triples, rel_triples=rel_triples, **kwargs)
        
    def get_attr_graph(self, **kwargs):
        try:
            self.attr_graph = self.modularity.attr_graph
            self.attr_head_triples, self.attr_tail_triples, self.attr_rel_triples \
                    = self.modularity.attr_head_triples, self.modularity.attr_tail_triples, self.modularity.attr_rel_triples
        except:
            print("there will be an error or you change the config to reload the attr graph.")
            self.attr_graph = None
            self.attr_head_triples, self.attr_tail_triples, self.attr_rel_triples \
                    = None, None, None
            if self.attr_config is not None:
                self.modularity.set_config(self.attr_config)
                self.modularity.load_graph()
            else:
                raise ValueError("you should set the attr to community.")

    def get_rel_graph_community(self, modularity_setting, **kwargs):
        return self.modularity.get_last_community(**modularity_setting)

    def set_attr_graph_with_community(self, attr_modularity_setting, attr_graph=None, head_triples=None, tail_triples=None, rel_triples=None, **kwargs):
        self.modularity.load_graph(graph_triples=attr_graph, head_triples=head_triples, tail_triples=tail_triples, rel_triples=rel_triples, **kwargs)
        if self.is_dual_graph:
            self.modularity.set_is_dual_graph(False)
        return self.modularity.get_last_community(**attr_modularity_setting, **kwargs)

    def get_attr_graph_from_rel_community(self, attr_graph, all_out_community, attr_modularity_setting, attr_lower_bounds=None, attr_head_triples=None, **kwargs):
        comm_attr_graph_pair = []
        for comm in tqdm(all_out_community):
            comm_attr_graph = GetSeedGraph.get_attr_seed_with_entity_commun(attr_graph, commun=comm, head_triples=attr_head_triples, **kwargs)
            if comm_attr_graph is not None and len(comm_attr_graph) > 0:
                if attr_lower_bounds is None or (attr_lower_bounds is not None and len(comm_attr_graph)>=attr_lower_bounds):
                    attr_comm = self.set_attr_graph_with_community(attr_modularity_setting, attr_graph=comm_attr_graph, **kwargs)
            elif comm_attr_graph is None:
                raise ValueError("you should give the comm attr value")
            else:
                attr_comm = []
            comm_attr_graph_pair.append((comm, attr_comm))
        return comm_attr_graph_pair

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)
from modularity.utils.io_utils import load_config
from modularity.DirectedLouvain.conf_parse import ModularityParse

class RelAndAttrParse(ModularityParse):
    # def __init__(self, config_path, **kwargs):
    #     super(RelAndAttrParse, self).__init__(config_path, **kwargs)

    def _get_attr_modularity_setting(self, attr_setting_key=None, **kwargs):
        if attr_setting_key is None:
            attr_setting_key = "attr_modularity_setting"
        self._attr_setting = self._config.get(attr_setting_key, {})

    def _get_attr_lower_bounds(self, **kwargs):
        self._attr_lower_bounds = self._config.get("attr_lower_bounds", None)

    def _get_attr_config(self, **kwargs):
        self._attr_config = self._config.get("attr_config", None)

    @property
    def attr_config(self, **kwargs):
        return self._attr_config
    
    @property
    def attr_lower_bounds(self, **kwargs):
        return self._attr_lower_bounds

    @property
    def attr_modularity_setting(self, **kwargs):
        return self._attr_setting

    def __call__(self, graph_setting_key=None, modularity_setting_key=None, attr_setting_key=None, **kwargs):
        super(RelAndAttrParse, self).__call__(graph_setting_key=graph_setting_key, modularity_setting_key=modularity_setting_key, **kwargs)
        self._get_attr_modularity_setting(attr_setting_key)
        self._get_attr_lower_bounds()
        self._get_attr_config()


from modularity.utils.io_utils import dump_json


class RunRelAndAttrCommunity:
    def __init__(self, config_path, **kwargs):
        conf_parse = RelAndAttrParse(config_path, **kwargs)
        conf_parse(**kwargs)
        self.graph_setting = conf_parse.graph_setting
        self.modularity_setting = conf_parse.attr_modularity_setting
        self.outfile = conf_parse.outfile
        self.attr_modularity_setting = conf_parse.attr_modularity_setting
        self.attr_lower_bounds = conf_parse.attr_lower_bounds
        self.attr_config = conf_parse.attr_config
        rel_attr_modu_init = {}
        rel_attr_modu_init["graph_setting"] = self.graph_setting
        rel_attr_modu_init["modularity_setting"] = self.modularity_setting
        rel_attr_modu_init["attr_modularity_setting"] = self.attr_modularity_setting
        rel_attr_modu_init["attr_lower_bounds"] = self.attr_lower_bounds
        rel_attr_modu_init["attr_config"] = self.attr_config
        self.rel_attr_modu = ModuWithRelAndAttr(**rel_attr_modu_init, **kwargs)

    def attr_graph(self, **kwargs):
        if self.rel_attr_modu.attr_graph is not None:
            attr_graph = self.rel_attr_modu.attr_graph
            head_triples = self.rel_attr_modu.attr_head_triples
            tail_triples = self.rel_attr_modu.attr_tail_triples
            rel_triples = self.rel_attr_modu.attr_rel_triples
        elif self.attr_config is not None:
            attr_graph = self.rel_attr_modu.modularity.graph
            head_triples = self.rel_attr_modu.modularity.graph_head_triples
            tail_triples = self.rel_attr_modu.modularity.graph_tail_triples
            rel_triples = self.rel_attr_modu.modularity.graph_rel_triples
        else:
            raise ValueError("we don't get the right attr graph with this setting.")
        return attr_graph, head_triples, tail_triples, rel_triples
            
    def __call__(self, **kwargs):
        self.rel_attr_modu.load_graph()
        all_rel_community = self.rel_attr_modu.get_rel_graph_community(self.modularity_setting, **kwargs)
        self.rel_attr_modu.get_attr_graph()
        attr_graph, head_triples, tail_triples, rel_triples = self.attr_graph()
        rel_entity_comm_and_property = self.rel_attr_modu.get_attr_graph_from_rel_community(attr_graph, all_rel_community, self.attr_modularity_setting, attr_lower_bounds=self.attr_lower_bounds, \
            attr_head_triples=head_triples, **kwargs)
        dump_json(self.outfile, rel_entity_comm_and_property)

if __name__ == "__main__":
    config_path = "/home/aiteam/lini/KG/modularity/DirectedLouvain/settings/rel_attr_community.yaml"
    run_rel_and_attr = RunRelAndAttrCommunity(config_path)
    run_rel_and_attr()