import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from tqdm import tqdm
from typing import Union

from modularity.utils.io_utils import read_from_file, load_json, dump_json

def get_communs(file_name):
    lines = read_from_file(file_name)
    communs = eval(lines[-1])
    assert type(communs) == list, "the communs should be list"
    assert type(communs[0]) == list, "the element of communs should be list"
    return communs

def comm2node(node2comm, last_partition, **kwargs)->list:
    renumber = [-1] * len(last_partition)
    for node in tqdm(range(len(last_partition))):
        renumber[node2comm[node]] += 1

    final = 0
    for i in tqdm(range(len(last_partition))):
        if renumber[i] != -1:
            renumber[i] = final
            final += 1
    comm_node = [[] for _ in range(final)]
    for i, nodes in tqdm(enumerate(last_partition)):
        comm_node[renumber[node2comm[i]]].extend(nodes)
    return comm_node

class ProcessModularity:
    @classmethod
    def split_graph_tree(cls, lines:list) -> list:
        node2comm_list = []
        node2comm = {}
        for line in tqdm(lines):
            if line.startswith("0 "):
                if node2comm:
                    node2comm_list.append(node2comm)
                    node2comm = {}
            node, comm = list(map(int, line.split(" ")))
            node2comm[node] = comm
        if node2comm:
            node2comm_list.append(node2comm)
        return node2comm_list

    @classmethod
    def reverse_node2label(cls, id2label:list, partition_list:list, sort:bool=True)->list:
        if sort:
            sorted_partition_list = sorted(partition_list, key=lambda x:len(x), reverse=True)
            partition_list = sorted_partition_list
        last_comms = [[] for _ in range(len(partition_list))]
        for idx, comm in tqdm(enumerate(partition_list)):
            for node in comm:
                last_comms[idx].append(id2label[str(node)])
        return last_comms

    @classmethod
    def revert_list_to_dict(cls, last_comms:list)->dict:
        communs = {}
        for idx, comms in tqdm(enumerate(last_comms)):
            communs[idx] = comms
        return communs

    @classmethod
    def cluster_community(cls, node2comm_list:list, **kwargs)->list:
        last_partition = [[i] for i in range(len(node2comm_list[0]))]
        for node2comm in node2comm_list:
            last_partition = comm2node(node2comm, last_partition)
        return last_partition

    @classmethod
    def reverse_graph_tree(cls, filename:str, labelfile:str, outfile:Union[str, None], node2node_renumber:Union[str, None]=None)->dict:
        print("filename: {}".format(filename))
        lines = read_from_file(filename)
        print("lines: {}".format(lines))
        id2label = load_json(labelfile)
        node2comm_list = cls.split_graph_tree(lines)
        last_partition = cls.cluster_community(node2comm_list)
        if node2node_renumber:
            node2node = load_json(node2node_renumber)
            last_partition = cls.reverse_node2label(node2node, last_partition)
        communs = cls.reverse_node2label(id2label, last_partition)
        communs_dict = cls.revert_list_to_dict(communs)
        dump_json(outfile, communs_dict)
        return communs_dict


class FindModularity:
    @classmethod
    def get_community(cls, communs:list, largest:bool):
        if len(communs) == 1:
            return len(communs[0]), communs[0]
        longest_or_shortest = len(communs[0])
        largest_or_minest_comm = communs[0]
        for comm in communs[1:]:
            if (largest and len(comm) > longest_or_shortest) or (not largest and len(comm) < longest_or_shortest):
                longest_or_shortest = len(comm)
                largest_or_minest_comm = comm
        return longest_or_shortest, largest_or_minest_comm