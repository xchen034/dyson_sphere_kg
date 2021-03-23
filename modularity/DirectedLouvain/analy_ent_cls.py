import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

import math
import copy
from collections import OrderedDict

from modularity.knowledge_fusion.get_dual_graph import ReadGraph
from modularity.knowledge_fusion.get_seed_graph import GetSeedGraph
from modularity.knowledge_fusion.utils import get_tuples_dict, save_tuples_to_txt, get_rel_dict, transpose_dict

from modularity.preprocess.get_community_info import get_post_community_with_attr_and_entity, filter_less_use_community

from modularity.utils.obj_utils import incDicWithWeightAdd, incDicWithAdd
from modularity.utils.io_utils import dump_json


class EntTypeAnaly:
    def __init__(self, read_graph_func, graph_path, community_path, is_attr=True, **kwargs):
        self.community_path = community_path
        self.read_graph_func = read_graph_func
        self.graph_path = graph_path
        self.is_attr = is_attr

    def load_graph(self, graph_triples=None, head_triples=None, tail_triples=None, rel_triples=None, **kwargs):
        _readfunc = ReadGraph.__call__(self.read_graph_func)
        if graph_triples is None:
            _graph = _readfunc(self.graph_path)
            if isinstance(_graph, list):
                self.graph = _graph
                self.graph_head_triples, self.graph_tail_triples, self.graph_rel_triples = None, None, None
            elif isinstance(_graph, tuple) and len(_graph) == 4:
                self.graph, self.graph_head_triples, self.graph_tail_triples, self.graph_rel_triples = _graph
            else:
                raise InterruptedError("the graph method we create is only support two type, ret 4 params or just one.")
            print("read graph done")
        elif head_triples is None or tail_triples is None or rel_triples is None:
            head_triples, tail_triples, rel_triples = {}, {}, {}
            for triple in graph_triples:
                head, rel, tail = triple
                incDicWithAdd(head_triples, head, triple)
                incDicWithAdd(tail_triples, tail, triple)
                incDicWithAdd(rel_triples, rel, triple)
            self.graph = graph_triples
            self.graph_head_triples = head_triples
            self.graph_tail_triples = tail_triples
            self.graph_rel_triples = rel_triples
        else:
            self.graph = graph_triples
            self.attr_head_triples = head_triples
            self.graph_tail_triples = tail_triples
            self.graph_rel_triples = rel_triples
        
    def get_attr_or_rel_graph(self, barrel, **kwargs):
        filtered_graph, barrel_filtered_num =  GetSeedGraph.get_rel_seed_with_barrel_num(self.graph, barrel, rel_triples=self.graph_rel_triples)
        return filtered_graph, barrel_filtered_num

    # def get_attr_barrel_graph(self, graph, barrel, **kwargs):
    #     filtered_entity_graph = GetSeedGraph.get_reversed_attr_seed(graph, barrel, tail_triples=self.graph_tail_triples)
    #     return filtered_entity_graph

    # def get_rel_barrel_graph(self, graph, barrel, **kwargs):
    #     filtered_rel_graph = GetSeedGraph.get_relation_seed(graph, barrel, rel_triples=self.graph_rel_triples)
    #     return filtered_rel_graph

    def get_attr_barrel(self, **kwargs):
        self.communities, self.communities_info = get_post_community_with_attr_and_entity(self.community_path, None)
        self.left_comm, self.filtered_comm, self.no_rel_comm = filter_less_use_community(self.communities_info, None, None, None)
        return self.left_comm

    def get_rel_graph(self, barrel, **kwargs):
        filtered_graph = GetSeedGraph.get_entity_seed(self.graph, barrel, head_triples=self.graph_head_triples, tail_triples=self.graph_tail_triples)
        rel_dict = {}
        for triple in filtered_graph:
            head, rel, tail = triple
            incDicWithWeightAdd(rel_dict, rel)
        return filtered_graph, rel_dict, list(rel_dict.keys())

    def filter_significant_attrs(self, attr_filtered_num, ent_nums, avg_num_per_attr=None, num_per_attr=None, ratio_per_attr=None, **kwargs):
        significant_num_per_attr = None
        if num_per_attr is not None:
            significant_num_per_attr = num_per_attr
        elif ratio_per_attr is not None:
            significant_num_per_attr = math.floor(ent_nums*ratio_per_attr)
        elif avg_num_per_attr is not None:
            significant_num_per_attr = avg_num_per_attr
        if significant_num_per_attr is None:
            return attr_filtered_num
        significant_attrs = OrderedDict()
        for key, num in attr_filtered_num.items():
            if num >= significant_num_per_attr:
                significant_attrs[key] = num
            else:
                break
        return significant_attrs
        
    def get_all_attr_info_with_barrel(self, ent_num_lower_bound=None, num_per_attr=None, ratio_per_attr=None, community_graphs_json=None, left_related_infos_json=None, left_significants_json=None, no_attr_comm_json=None, single_ent_comm_json=None, **kwargs):
        left_comm = self.get_attr_barrel()
        community_graphs = {}
        community_related_infos = {}
        community_significant_infos = {}
        for idx, comm_info in left_comm.items():
            attrs = comm_info["attr"]
            filtered_graph, attr_filtered_num = self.get_attr_or_rel_graph(attrs)
            attr_filtered_num = OrderedDict(sorted(attr_filtered_num.items(), key=lambda x:x[1], reverse=True))
            ent_attr_nums = comm_info["ent_and_attr_number"]
            attr_nums = comm_info["attr_number"]
            ent_nums = ent_attr_nums - attr_nums
            avg_num = ent_nums * 1./attr_nums
            significant_attrs = None
            if avg_num > 0 and (ent_num_lower_bound is None or ent_nums > ent_num_lower_bound):
                significant_attrs = self.filter_significant_attrs(attr_filtered_num, ent_nums, avg_num_per_attr=avg_num, num_per_attr=None, ratio_per_attr=None)
            community_graphs[idx] = filtered_graph
            comm_info["significant_attrs"] = significant_attrs
            community_related_infos[idx] = comm_info
            if significant_attrs is not None:
                community_significant_infos[idx] = significant_attrs
        self.save_related_attr_infos(community_graphs, community_related_infos, community_significant_infos, community_graphs_json=community_graphs_json, left_related_infos_json=left_related_infos_json, left_significants_json=left_significants_json, no_attr_comm_json=no_attr_comm_json, single_ent_comm_json=single_ent_comm_json)
        return community_graphs, community_related_infos, community_significant_infos

    def save_related_attr_infos(self, community_graphs, community_related_infos, community_significant_infos, community_graphs_json=None, left_related_infos_json=None, left_significants_json=None, no_attr_comm_json=None, single_ent_comm_json=None):
        dump_json(community_graphs_json, community_graphs)
        dump_json(left_related_infos_json, community_related_infos)
        dump_json(left_significants_json, community_significant_infos)
        dump_json(no_attr_comm_json, self.no_rel_comm)
        dump_json(single_ent_comm_json, self.filtered_comm)

import copy
from modularity.utils.io_utils import load_config

class AnaConfigParse:
    def __init__(self, config_path, **kwargs):
        self._config = load_config(config_path)

    def attr_info_params_process(self, **kwargs):
        origin_attrs = copy.deepcopy(self._config.get("attr_info_params"))
        all_saved_path = copy.deepcopy(origin_attrs.get("save_path"))
        del origin_attrs["save_path"]
        new_paths = {}
        if origin_attrs.get("save_parent_path", None):
            parent_path = origin_attrs["save_parent_path"]
            for path_name, path in all_saved_path.items():
                if path:
                    new_paths[path_name] = os.path.join(parent_path, path)
                else:
                    new_paths[path_name] = path
            all_saved_path = new_paths
            del origin_attrs["save_parent_path"]
        origin_attrs.update(all_saved_path)
        return origin_attrs

    @property
    def init_params(self, **kwargs):
        return self._config.get("init_params")

    @property
    def attr_params(self, **kwargs):
        return self.attr_info_params_process()

class RunAttrAnaly:
    def __init__(self, config_path, **kwargs):
        conf_parse = AnaConfigParse(config_path)
        self.init_params = conf_parse.init_params
        self.attr_params = conf_parse.attr_params
        self.ent_anly = EntTypeAnaly(**self.init_params)
    
    def __call__(self, **kwargs):
        self.ent_anly.load_graph()
        if self.ent_anly.is_attr:
            return self.ent_anly.get_all_attr_info_with_barrel(**self.attr_params)

if __name__=="__main__":
    config_path = ""