import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from modularity.utils.io_utils import make_parent_path, read_from_file, load_json

def get_embeding_dict(_list):
    _dict ={}
    for i in range(len(_list)):
        _dict[_list[i]] = i
    return _dict

def transpose_dict(_dict):
    dict_T = {}
    for key in _dict.keys():
        dict_T[_dict[key]] = key
    return dict_T

def get_tuples_dict(tuples):
    entity = {}
    relations = {}
    for i in range(len(tuples)):
        head, rel, tail = tuples[i]
        if rel not in relations:
            relations[rel] = len(relations)
        if head not in entity:
            entity[head] = len(entity)
        if tail not in entity:
            entity[tail] = len(entity)
    return entity, relations

def get_rel_dict(tuples):
    rels = {}
    new_tuples = []
    for i in range(len(tuples)):
        rel1, w, rel2 = tuples[i]
        if rel1 not in rels:
            rels[rel1] = len(rels)
        if rel2 not in rels:
            rels[rel2] = len(rels)
        rel1idx = rels.get(rel1)
        rel2idx = rels.get(rel2)
        new_tuples.append((rel1idx, w, rel2idx))
    return rels, new_tuples

def embed_tuples(tuples, ent_dict, rel_dict=None):
    embeded_tuples = []
    for i in range(len(tuples)):
        if rel_dict:
            embeded_tuples.append((ent_dict[tuples[i][0]], rel_dict[tuples[i][1]], ent_dict[tuples[i][2]]))
        else:
            embeded_tuples.append((ent_dict[tuples[i][0]], tuples[i][1], ent_dict[tuples[i][2]]))
    return embeded_tuples

def save_tuples_to_txt(tuples, file):
    make_parent_path(file)
    with open(file, 'w', encoding='utf-8') as f:
        for i in range(len(tuples)):
            head, rel, tail = tuples[i]
            content = '{0}\t{1}\t{2}\n'.format(head, rel, tail)
            f.writelines(content)
    return 1

def save_dict_to_json(_dict, file):
    import json
    make_parent_path(file)
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(_dict, f, indent=4, ensure_ascii=False)

def create_random_graph(ent_num, rel_num, graph_size):
    import random
    entity_list = [_ for _ in range(ent_num)]
    relation_list = [_ for _ in range(rel_num)]
    graph = []
    while len(graph) < graph_size:
        head, tail = random.sample(entity_list, 2)
        relation, = random.sample(relation_list, 1)
        temp_tuple = (head, relation, tail)
        if temp_tuple not in graph:
            graph.append(temp_tuple)
    return graph

def get_rel_nums(graph):
    rel_num_dict = {}
    for _triple in graph:
        if _triple[1] not in rel_num_dict.keys():
            rel_num_dict[_triple[1]] = 1
        else:
            rel_num_dict[_triple[1]] +=1
    return rel_num_dict

def filter_graph_by_rel_num(graph, number):
    rel_num_dict = get_rel_nums(graph)
    rel_list = []
    for key in rel_num_dict.keys():
        if rel_num_dict[key] > number:
            rel_list.append(key)
    graph_filted = []
    for i in range(len(graph)):
        if graph[i][1] in rel_list:
            graph_filted.append(graph[i])
    return graph_filted