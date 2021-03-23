import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from tqdm import tqdm
import multiprocessing

from modularity.utils.io_utils import read_from_file, write_to_file
from modularity.utils.obj_utils import node2idx, incDicWithAdd
from modularity.preprocess.pku_preprocess import parse_line

## for diff rel in same entities, we weight all the edges to 1.

def reverse_out_degree_to_in(node2rel_node_out):
    node2rel_node_in = {}
    for node, out_rel_nodes in tqdm(node2rel_node_out.items()):
        for rel_node in out_rel_nodes:
            rel, in_node = rel_node
            incDicWithAdd(node2rel_node_in, in_node, (rel, node))
    return node2rel_node_in
             
def reverse_node2idx(node2_idxes):
    id2node = {}
    for key, val in tqdm(node2_idxes.items()):
        id2node[val] = key
    return id2node

def get_nodes_weight(rel_nodes, node2idx):
    node_weight = {}
    for rel, node in rel_nodes:
        if node not in node_weight:
            node_weight[node] = 1
        else:
            node_weight[node] += 1
    nodes = []
    weights = []
    for node, weight in node_weight.items():
        nodes.append(node2idx[node])
        weights.append(weight)
    return node_weight, nodes, weights

def get_links_out_and_weights(in_nodes, out_nodes, node2idx):
    node_in_weight, this_links_in, this_weights_in = get_nodes_weight(in_nodes, node2idx)
    node_out_weight, this_links_out, this_weights_out = get_nodes_weight(out_nodes, node2idx)
    return this_links_in, this_weights_in, this_links_out, this_weights_out

def get_all_node_in_out(node_idxes, node2rel_node_in, node2rel_node_out):
    id2node = reverse_node2idx(node_idxes)
    all_node_list, links_out, links_in, degrees_out, degrees_in, weights_in, weights_out, labels = [], [], [], [], [], [], [], []
    for i in tqdm(range(len(node_idxes))):
        all_node_list.append(i)
        node = id2node[i]
        labels.append(node)
        in_nodes = node2rel_node_in.get(node, [])
        out_nodes = node2rel_node_out.get(node, [])
        this_links_in, this_weights_in, this_links_out, this_weights_out = get_links_out_and_weights(in_nodes, out_nodes, node_idxes)
        links_in.extend(this_links_in)
        links_out.extend(this_links_out)
        weights_in.extend(this_weights_in)
        weights_out.extend(this_weights_out)
        degrees_in.append(len(links_in))
        degrees_out.append(len(links_out))
    return all_node_list, links_out, links_in, degrees_out, degrees_in, weights_in, weights_out, labels

def graph_relation_lines(nodes_list, degrees_out, links_out, degrees_in, links_in, labels=None):
    lines = []
    all_list = [nodes_list, degrees_out, links_out, degrees_in, links_in]
    if labels is not None:
        all_list.append(labels)
    for item_list in all_list:
        lines.append("\t".join(map(str, item_list))+'\n')
    return lines

def graph_weight_lines(weights_out, weights_in):
    all_list = [weights_out, weights_in]
    lines = []
    for item_list in all_list:
        lines.append("\t".join(map(str, item_list))+'\n')
    return lines

def get_triplets_to_degrees(file_name, out_graph_file, out_graph_weight_file):
    lines = read_from_file(file_name)
    node2rel_node_out = {}
    node2rel_node_in = {}
    node_idx = {}
    rel_idx = {}
    for line in tqdm(range(len(lines))):
        line = lines[line].strip()
        triple = parse_line(line)
        ent1, rel, ent2 = triple
        ent1_idx = node2idx(node_idx, ent1)
        ent2_idx = node2idx(node_idx, ent2)
        rel_id = node2idx(rel_idx, rel)
        incDicWithAdd(node2rel_node_out, ent1, (rel, ent2))
        incDicWithAdd(node2rel_node_in, ent2, (rel, ent1))
    # node2rel_node_in = reverse_out_degree_to_in(node2rel_node_out)
    all_node_list, links_out, links_in, degrees_out, degrees_in, weights_in, weights_out, labels = get_all_node_in_out(node_idx, node2rel_node_in, node2rel_node_out)
    assert len(degrees_in) == len(degrees_out) == len(all_node_list) == len(labels), "error in degrees"
    assert len(links_out) == degrees_out[-1] == len(weights_out), "error in out links"
    assert len(links_out) == degrees_in[-1] == len(weights_in), "error in in links"
    graph_lines = graph_relation_lines(all_node_list, degrees_out, links_out, degrees_in, links_in, labels)
    graph_weights = graph_weight_lines(weights_out, weights_in)
    write_to_file(out_graph_file, graph_lines)
    write_to_file(out_graph_weight_file, graph_weights)

def multiprocess(func, args):
    # print(multiprocessing.cpu_count())
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.apply(func, args)
    pool.close()
    pool.join()


if __name__ == "__main__":
    file_name = "/media/aiteam/DATA/lini/lini/dataset/PKUBASE/pkubase-complete-2020/all_pkubase_triplets.txt"
    out_graph_file = "/media/aiteam/DATA/lini/lini/dataset/PKUBASE/pkubase-complete-2020/graph_in.txt"
    out_graph_weight_file = "/media/aiteam/DATA/lini/lini/dataset/PKUBASE/pkubase-complete-2020/graph_weight.txt"
    # get_triplets_to_degrees(file_name, out_graph_file, out_graph_weight_file)
    # file_name = "/media/aiteam/DATA/lini/lini/dataset/PKUBASE/pkubase-complete-2020/test_preprocess1.txt"
    # out_graph_file = "/media/aiteam/DATA/lini/lini/dataset/PKUBASE/pkubase-complete-2020/test_graph_in.txt"
    # out_graph_weight_file = "/media/aiteam/DATA/lini/lini/dataset/PKUBASE/pkubase-complete-2020/test_graph_weight.txt"
    multiprocess(get_triplets_to_degrees, (file_name, out_graph_file, out_graph_weight_file))