import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from modularity.DirectedLouvain.conf_parse import ModularityParse
from modularity.DirectedLouvain.multi_round import MultiCommunity
from modularity.preprocess.post_process import ProcessModularity
from modularity.utils.io_utils import dump_json

class RunModularity:
    def __init__(self, config_path, **kwargs):
        conf_parse = ModularityParse(config_path, **kwargs)
        conf_parse(**kwargs)
        self.graph_setting = conf_parse.graph_setting
        self.modularity_setting = conf_parse.modularity_setting
        self.outfile = conf_parse.outfile
        self.modularity = MultiCommunity(**self.graph_setting, **kwargs)

    def __call__(self, **kwargs):
        self.modularity.load_graph()
        community = self.modularity.get_last_community(**self.modularity_setting, **kwargs)
        all_out_dict = ProcessModularity.revert_list_to_dict(community)
        dump_json(self.outfile, all_out_dict)

if __name__== "__main__":
    config_path = "/Users/chenxi/projects/knowledge_graph-modularity/modularity/settings/modularity_dysen_sphere.yaml"
    RunMo = RunModularity(config_path)
    RunMo()