import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from modularity.utils.io_utils import load_json, dump_json

def get_post_community_with_attr_and_entity(community_json, info_save_json):
    communities = load_json(community_json)
    info_dic = {}
    for key, comm in communities.items():
        info_dic[key] = {}
        info_dic[key]["ent_and_attr_number"] = len(comm)
        rel_list = []
        for item in comm:
            if item.startswith("_<"):
                rel_list.append(item[1:])
        info_dic[key]["attr_number"] = len(rel_list)
        info_dic[key]["attr"] = rel_list
    dump_json(info_save_json, info_dic)
    return communities, info_dic

def filter_less_use_community(info_dic, left_comm_json, filtered_comm_json, no_rel_comm_json):
    filtered_comm = {}
    no_rel_comm = {}
    left_comm = {}
    for key, info in info_dic.items():
        if info["attr_number"] == 0:
            this_key = len(no_rel_comm)
            no_rel_comm[this_key] = info
        elif info["ent_and_attr_number"] - info["attr_number"] <= 1:
            this_key = len(filtered_comm)
            filtered_comm[this_key] = info
        else:
            this_key = len(left_comm)
            left_comm[this_key] = info
    dump_json(left_comm_json, left_comm)
    dump_json(filtered_comm_json, filtered_comm)
    dump_json(no_rel_comm_json, no_rel_comm)
    return left_comm, filtered_comm, no_rel_comm