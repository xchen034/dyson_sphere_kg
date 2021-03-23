import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from modularity.utils.obj_utils import incDicWithAdd

import json
from tqdm import tqdm

def get_barrel(barrel_json, key):
    with open(barrel_json, encoding='utf-8') as f:
        barrel_dict = json.load(f)
    return barrel_dict[key]

class GetSeedGraph:
    @classmethod
    def get_entity_seed(cls, graph, barrel, head_triples=None, tail_triples=None):
        seed_graph = []
        if head_triples is None or tail_triples is None:
            for triple in tqdm(graph):
                if triple[0] in barrel or triple[-1] in barrel:
                    seed_graph.append(triple)
        else:
            seed_graph = set()
            for ent in tqdm(barrel):
                heads = set(head_triples.get(ent, set()))
                tails = set(tail_triples.get(ent, set()))
                heads.update(tails)
                seed_graph.update(heads)
            seed_graph = list(seed_graph)
        return seed_graph

    @classmethod
    def get_relation_seed(cls, graph, barrel, rel_triples=None):
        seed_graph = []
        if rel_triples is None:
            for triple in tqdm(graph):
                if triple[1] in barrel:
                    seed_graph.append(triple)
        else:
            seed_graph = set()
            for rel in tqdm(barrel):
                seed_graph.update(set(rel_triples.get(rel, set())))
            seed_graph = list(seed_graph)
        return seed_graph

    @classmethod
    def get_dual_seed(cls, dual_graph, barrel):
        dual_seed_graph = []
        for triple in tqdm(dual_graph):
            if triple[0] in barrel or triple[-1] in barrel:
                dual_seed_graph.append(triple)
        return dual_seed_graph

    @classmethod
    def get_reversed_attr_seed(cls, graph, barrel, tail_triples=None):
        attr_seed_graph = []
        if tail_triples is None:
            for triple in tqdm(graph):
                if triple[-1] in barrel:
                    attr_seed_graph.append(triple)
        else:
            attr_seed_graph = set()
            for attr in tqdm(barrel):
                attr_seed_graph.update(set(tail_triples.get(attr, set())))
            attr_seed_graph = list(attr_seed_graph)
        return attr_seed_graph

    @classmethod
    def get_attr_seed_with_entity_commun(cls, graph, commun, head_triples=None):
        if graph is None:
            return None
        attr_seed_graph = []
        if head_triples is None:
            for triple in tqdm(graph):
                if triple[0] in commun:
                    attr_seed_graph.append(triple)
        else:
            attr_seed_graph = set()
            for ent in tqdm(commun):
                attr_seed_graph.update(set(head_triples.get(ent, set())))
            attr_seed_graph = list(attr_seed_graph)
        return attr_seed_graph

    @classmethod
    def get_rel_seed_with_barrel_num(cls, graph, barrel, rel_triples=None):
        seed_graph = []
        barrel_num = {}
        if rel_triples is None:
            tmp_barrel_dict = {}
            for triple in tqdm(graph):
                if triple[1] in barrel:
                    incDicWithAdd(tmp_barrel_dict, triple[1], triple)
                    seed_graph.append(triple)
            for item in barrel:
                barrel_num[item] = len(tmp_barrel_dict.get(item, set()))
        else:
            seed_graph = set()
            for rel in tqdm(barrel):
                seed_graph.update(set(rel_triples.get(rel, set())))
                barrel_num[rel] = len(rel_triples.get(rel, set()))
            seed_graph = list(seed_graph)
        return seed_graph, barrel_num