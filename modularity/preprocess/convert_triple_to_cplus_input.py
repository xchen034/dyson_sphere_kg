import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

import pdb
from tqdm import tqdm
import multiprocessing

from modularity.utils.io_utils import read_from_file, write_to_file, dump_json
from modularity.utils.obj_utils import node2idx, incDicWithAdd, incDicWithWeightAdd

def parse_line(line):
    triples = line.split("\t")
    try:
        assert len(triples) == 3, "we don't get the triple which we want to."
        return triples
    except:
        return None

def convert_triple_to_needs(filename, outfile, direct=True, save_node2idx=None, weight_property=None):
    lines = read_from_file(filename)
    node_idx = {}
    node_weights = {}
    for line in tqdm(range(len(lines))):
        line = lines[line].strip()
        triple = parse_line(line)
        if triple is None:
            continue
        ent1, rel, ent2 = triple
        if save_node2idx is not None:
            ent1idx = node2idx(node_idx, ent1)
            ent2idx = node2idx(node_idx, ent2)
        else:
            ent1idx = int(ent1)
            ent2idx = int(ent2)
        val = None
        try:
            val= float(rel)
        except:
            if weight_property is not None and rel.startswith("\""):
                val = weight_property
        key = " ".join([str(ent1idx), str(ent2idx)])
        incDicWithWeightAdd(node_weights, key, val)
        if not direct:
            key = " ".join([str(ent2idx), str(ent1idx)])
            incDicWithWeightAdd(node_weights, key, val)
    all_out_lines = []
    for key, val in tqdm(node_weights.items()):
        line = key + " " + str(val) + '\n'
        all_out_lines.append(line)
    idx_node = {}
    for node, idx in tqdm(node_idx.items()):
        idx_node[idx] = node
    dump_json(save_node2idx, idx_node)
    write_to_file(outfile, all_out_lines)
