import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from typing import Union
import shutil
from tqdm import tqdm
import math
import pdb

from modularity.DirectedLouvain.directedLouvain import Py2CPlusDL
from modularity.knowledge_fusion.get_dual_graph import ReadGraphFunc, ReadGraph, BaseGetDualGraph
from modularity.knowledge_fusion.get_seed_graph import GetSeedGraph
from modularity.knowledge_fusion.utils import save_tuples_to_txt, get_tuples_dict, get_rel_dict, transpose_dict
from modularity.utils.io_utils import dump_json
from modularity.utils.obj_utils import incDicWithAdd

class MultiCommunity:
    all_out_path = os.path.join(basepath, "modularity", "community")
    rel2dic_path = os.path.join(basepath, "modularity", "community", "dict2rels")
    origin_dual_rel2dict = os.path.join(rel2dic_path, "rel2dict.json")
    entity_dual_rel2dict = os.path.join(rel2dic_path, "rel2dict_entity.json")
    rel_dual_rel2dict = os.path.join(rel2dic_path, "rel2dict_rel.json")
    graph_path = os.path.join(basepath, "modularity", "community", "graphs")
    dual_graph_txt = os.path.join(graph_path, "dual_graph.txt")
    entity_dual_graph = os.path.join(graph_path, "dual_graph_entity.txt")
    rel_dual_graph = os.path.join(graph_path, "dual_graph_rel.txt")
    graph_txt = os.path.join(graph_path, "graph.txt")
    entity_graph = os.path.join(graph_path, "graph_entity.txt")
    rel_graph = os.path.join(graph_path, "graph_rel.txt")
    tmp_community_graph = os.path.join(basepath, "modularity", "community", "communities")
    tmp_count = 0
    tmp_gen_community_path = os.path.join(basepath, "modularity", "community", "gap_gen_community")

    def __init__(self, triple_txt, read_graph_function, is_origin_graph=True, del_tmp_file=False, seed=None, is_dual_graph=False, weight_property=None, **kwargs):
        self.triple_txt = triple_txt
        self.del_tmp_file = del_tmp_file
        self.seed = seed
        self.weight_property = weight_property
        self.is_dual_graph = is_dual_graph
        self.is_origin_graph = is_origin_graph
        self.config = {}
        self.config["read_graph_function"] = read_graph_function
        self.config["graph_file_path"] = triple_txt

    def set_config(self, value, **kwargs):
        self.config = value
    
    def set_is_dual_graph(self, value, **kwargs):
        self.is_dual_graph = value

    def load_graph(self, graph_triples=None, head_triples=None, tail_triples=None, rel_triples=None, **kwargs):
        if graph_triples is None:
            self.graphcls = BaseGetDualGraph(Config=self.config, **kwargs)
            self.graph = self.graphcls.graph
            self.graph_head_triples = self.graphcls.graph_head_triples
            self.graph_tail_triples = self.graphcls.graph_tail_triples
            self.graph_rel_triples = self.graphcls.graph_rel_triples
            is_origin_graph = self.is_origin_graph
            try:
                self.attr_graph = self.graphcls.attr_graph
                self.attr_head_triples, self.attr_tail_triples, self.attr_rel_triples \
                    = self.graphcls.attr_head_triples, self.graphcls.attr_tail_triples, self.graphcls.attr_rel_triples
            except:
                pass
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
            is_origin_graph = False
        else:
            self.graph = graph_triples
            self.attr_head_triples = head_triples
            self.graph_tail_triples = tail_triples
            self.graph_rel_triples = rel_triples
            is_origin_graph = False

        if self.is_dual_graph:
            self.dual_graphs, self.dict2rel = self.graphcls.get_dual_graph_from_tuples(self.graph, isTrans=None)
            self.dual_graph_origin, self.dual_graph = self.dual_graphs
            save_tuples_to_txt(self.dual_graph, self.dual_graph_txt)
            dump_json(self.origin_dual_rel2dict, self.dict2rel)
        entity, relations = get_tuples_dict(self.graph)
        self.total_ent_num = len(entity)
        self.total_rel_num = len(relations)
        if is_origin_graph:
            self.graph_txt = self.triple_txt
        else:
            save_tuples_to_txt(self.graph, self.graph_txt)

    def get_entity_barrel_graph(self, graph, barrel, **kwargs):
        self.filtered_entity_graph = GetSeedGraph.get_entity_seed(graph, barrel)
        # self.filtered_entity_dual_graph, self.filtered_entity_dict2rel = self.graphcls.get_dual_graph_from_tuples(graph, isTrans=False)
        entity, relations = get_tuples_dict(self.filtered_entity_graph)
        save_tuples_to_txt(self.filtered_entity_graph, self.entity_graph)
        # dump_json(self.entity_dual_rel2dict, self.filtered_entity_dict2rel)
        return set(entity.keys())

    def get_rel_barrel_graph(self, graph, barrel, **kwargs):
        # self.filtered_rel_graph = GetSeedGraph.get_relation_seed(graph, barrel)
        # self.filtered_rel_dual_graph, self.filtered_rel_dict2rel = self.graphcls.get_dual_graph_from_tuples(graph, isTrans=False)
        self.filtered_rel_dual_graph_origin = GetSeedGraph.get_dual_seed(graph, barrel)
        self.filtered_rel2id, self.filtered_rel_dual_graph = get_rel_dict(self.filtered_rel_dual_graph_origin)
        self.filtered_rel_dict2rel = transpose_dict(self.filtered_rel2id)
        save_tuples_to_txt(self.filtered_rel_dual_graph, self.rel_graph)
        dump_json(self.rel_dual_rel2dict, self.filtered_rel_dict2rel)
        return set(self.filtered_rel2id.keys())

    def get_configuration_to_community(self, origin_triple_txt:str, labelfile:Union[str,None], outfile:Union[str, None]=None, init_partition_file:Union[str, None]=None,  \
        precision:Union[float, None]=None, display_level:Union[int, None]=None, verbose:Union[bool, None]=None, with_weights:bool=True, **kwargs):
        save_node2dix = None # according to the logic, the dual graph is regenerated from graph
        if self.is_dual_graph:
            direct = False
            tmp_community = "tmp_dual_graph_%d"%(self.tmp_count)
            self.tmp_count += 1
        else:
            direct = True
            tmp_community = "tmp_graph_%d"%(self.tmp_count)
            self.tmp_count += 1
            save_node2dix = os.path.join(self.tmp_gen_community_path, tmp_community+"_ent_map.json")
        if outfile is None:
            outfile = os.path.join(self.tmp_community_graph, tmp_community+"_community.json")
        out_weight_file = None
        if with_weights:
            out_weight_file = os.path.join(self.tmp_gen_community_path, tmp_community+".weights")
        out_graph_tree = os.path.join(self.tmp_gen_community_path, tmp_community+".tree")
        out_bin_file = os.path.join(self.tmp_gen_community_path, tmp_community+".bin")
        community_args = {
            "origin_triple_txt": origin_triple_txt,
            "outfile": outfile,
            "direct": direct,
            "out_bin_file": out_bin_file,
            "out_weights_file": out_weight_file,
            "output_graph_tree": out_graph_tree,
            "labelfile": labelfile,
            "save_node2idx": save_node2dix,
            "init_partition_file": init_partition_file,
            "precision": precision,
            "display_level": display_level,
            "verbose": verbose,
            "seed": self.seed
        }
        try:
            community_args.update({"weight_property":self.weight_property})
        except:
            pass
        return community_args

    def get_community(self, origin_triple_txt:str, labelfile:Union[str, None], init_partition_file:Union[str, None]=None, \
            precision:Union[float, None]=None, display_level:Union[int, None]=None, verbose:Union[bool, None]=None, with_weights:bool=True, **kwargs):
        community_args = self.get_configuration_to_community(origin_triple_txt=origin_triple_txt, labelfile=labelfile, init_partition_file=init_partition_file, precision=precision, \
            display_level=display_level, verbose=verbose, with_weights=with_weights)
        community = Py2CPlusDL.convert_and_community(**community_args)
        return community

    def split_rerun_and_no_process(self, community:dict, rerun_node_num:Union[int, None]=None, aside_comm_entities:Union[set, None]=None, origin_comm:Union[list, None]=None, **kwargs):
        no_process_commun, rerun_commun = [], []
        for idx, commun in tqdm(community.items()):
            if aside_comm_entities is not None and len(aside_comm_entities) > 0:
                commun = list(set(commun).difference(aside_comm_entities))
            elif aside_comm_entities is None and origin_comm is not None:
                commun = list(set(commun).intersection(set(origin_comm)))
            if len(commun) == 0:
                continue
            if rerun_node_num is not None and len(commun) > rerun_node_num:
                rerun_commun.append(commun)
            else:
                no_process_commun.append(commun)
        return no_process_commun, rerun_commun

    def get_last_community(self, ratio:Union[float, None], com_node_num:Union[int, None]=None, iter_num:int=5, init_partition_file:Union[str, None]=None, \
        precision:Union[float, None]=None, display_level:Union[int, None]=None, verbose:Union[bool, None]=None, with_weights:bool=True, **kwargs):
        round_cnt = 0
        all_out_community = []
        if self.is_dual_graph:
            origin_triple_txt = self.dual_graph_txt
            labelfile = self.origin_dual_rel2dict
            start_num = self.total_rel_num
            get_barrel_graph = self.get_rel_barrel_graph
            input_txt = self.rel_graph
            input_labelfile = self.rel_dual_rel2dict
            this_graph = self.dual_graph_origin
        else:
            origin_triple_txt = self.graph_txt
            labelfile = None
            start_num = self.total_ent_num
            get_barrel_graph = self.get_entity_barrel_graph
            input_txt = self.entity_graph
            input_labelfile = None
            this_graph = self.graph
        community = self.get_community(origin_triple_txt=origin_triple_txt, labelfile=labelfile, init_partition_file=init_partition_file, precision=precision,\
            display_level=display_level, verbose=verbose, with_weights=with_weights)
        rerun_node_num = None
        if com_node_num is not None:
            rerun_node_num = com_node_num
        if ratio is not None:
            rerun_node_num = math.ceil(start_num*ratio)
        if rerun_node_num is None:
            rerun_node_num = math.ceil(start_num*1./len(community))
        
        rerun_community = []
        no_process_commun, rerun_commun = self.split_rerun_and_no_process(community, rerun_node_num=rerun_node_num)
        all_out_community.extend(no_process_commun)
        rerun_community = rerun_commun
        round_cnt += 1
        while round_cnt < iter_num and len(rerun_community) > 0:
            new_rerun_community = []
            for r_comm in tqdm(rerun_community):
                rets = get_barrel_graph(graph=this_graph, barrel=r_comm)
                aside_comm_entities = None
                if rets is not None:
                    assert isinstance(rets, set), "you should return the entity or relations"
                    aside_comm_entities = rets.difference(set(r_comm))
                origin_triple_txt = input_txt
                labelfile = input_labelfile
                community = self.get_community(origin_triple_txt=origin_triple_txt, labelfile=labelfile, init_partition_file=init_partition_file, precision=precision,\
                    display_level=display_level, verbose=verbose, with_weights=with_weights)
                no_process_commun, rerun_commun = self.split_rerun_and_no_process(community, rerun_node_num=rerun_node_num, aside_comm_entities=aside_comm_entities, origin_comm=r_comm)
                new_rerun_community.extend(rerun_commun)
                all_out_community.extend(no_process_commun)
            rerun_community = new_rerun_community
            round_cnt += 1
        if rerun_community:
            all_out_community.extend(rerun_community)

        if self.del_tmp_file:
            shutil.rmtree(self.all_out_path, ignore_errors=True)
        return all_out_community


