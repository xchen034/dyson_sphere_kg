import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

import numpy as np
from modularity.knowledge_fusion.utils import embed_tuples, get_tuples_dict, get_rel_dict, transpose_dict
# from modularity.knowledge_fusion.utils import *
from modularity.utils.obj_utils import incDicWithAdd
import time
from tqdm import tqdm


class ReadGraphFunc:
    '''
    user defined graph read function
    Input: file_path(must give), user defined parameters
    Output: graph tuples: list
    '''
    @classmethod
    def base_get_graph(cls, graph_txt):
        import re
        graph_tuples = []
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                except:
                    continue
                graph_tuples.append((head, rel, tail))
        graph_tuples = list(set(graph_tuples))
        print(len(graph_tuples))
        return graph_tuples

    @classmethod
    def get_graph_from_dysen(cls, graph_txt):
        import re
        graph_tuples = []
        # head_dict = {}
        # tail_dict = {}
        # rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split("\t|\n", contents[i][:-1])
                    if rel not in ['类型','生产时间(s)','产地'] and '公式' not in head:
                        graph_tuples.append((head, int(rel), tail))
                except:
                    continue
        graph_tuples = list(set(graph_tuples))
        return graph_tuples
    @classmethod
    def get_graph_with_entity(cls, graph_txt):
        import re
        graph_tuples = []
        head_dict = {}
        tail_dict = {}
        rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                except:
                    continue
                incDicWithAdd(head_dict, head, (head, rel, tail))
                incDicWithAdd(tail_dict, tail, (head, rel, tail))
                incDicWithAdd(rel_dict, rel, (head, rel, tail))
                graph_tuples.append((head, rel, tail))
        graph_tuples = list(set(graph_tuples))
        # print(len(graph_tuples))
        return graph_tuples, head_dict, tail_dict, rel_dict

    @classmethod
    def get_graph_with_only_rel_no_property(cls, graph_txt):
        import re
        graph_tuples = []
        head_dict = {}
        tail_dict = {}
        rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                    if head.startswith("\"") or tail.startswith("\""):
                        continue
                except:
                    continue
                incDicWithAdd(head_dict, head, (head, rel, tail))
                incDicWithAdd(tail_dict, tail, (head, rel, tail))
                incDicWithAdd(rel_dict, rel, (head, rel, tail))
                graph_tuples.append((head, rel, tail))
        graph_tuples = list(set(graph_tuples))
        # print(len(graph_tuples))
        return graph_tuples, head_dict, tail_dict, rel_dict

    @classmethod
    def get_graph_with_property_reversed_no_rel(cls, graph_txt, rel_change=True):
        import re
        graph_tuples = []
        head_dict = {}
        tail_dict = {}
        rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                    if not (head.startswith("\"") or tail.startswith("\"")):
                        continue
                except:
                    continue
                if rel_change:
                    rel = "_" + rel
                incDicWithAdd(head_dict, head, (head, tail, rel))
                incDicWithAdd(tail_dict, tail, (head, tail, rel))
                incDicWithAdd(rel_dict, rel, (head, tail, rel))
                graph_tuples.append((head, tail, rel))
        graph_tuples = list(set(graph_tuples))
        # print(len(graph_tuples))
        return graph_tuples, head_dict, tail_dict, rel_dict

    @classmethod
    def get_graph_with_rel_and_property_reverse(cls, graph_txt, change=True):
        import re
        graph_tuples = []
        head_dict = {}
        tail_dict = {}
        rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                    if head.startswith("\"") or tail.startswith("\""):
                        assert not head.startswith("\""), "wrong_file"
                        tmp_rel = rel
                        rel = tail
                        if change:
                            tail = "_"+tmp_rel
                        else:
                            tail = tmp_rel
                        continue
                except:
                    continue
                incDicWithAdd(head_dict, head, (head, rel, tail))
                incDicWithAdd(tail_dict, tail, (head, rel, tail))
                incDicWithAdd(rel_dict, rel, (head, rel, tail))
                graph_tuples.append((head, rel, tail))
        graph_tuples = list(set(graph_tuples))
        # print(len(graph_tuples))
        return graph_tuples, head_dict, tail_dict, rel_dict

    @classmethod
    def get_split_graph_with_rel_and_property_reversed(cls, graph_txt, change=True):
        import re
        rel_graph_tuples = []
        attr_graph_tuples = []
        rel_head_dict = {}
        rel_tail_dict = {}
        rel_rel_dict = {}
        attr_head_dict = {}
        attr_tail_dict = {}
        attr_rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in tqdm(range(len(contents))):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                    if head.startswith("\"") or tail.startswith("\""):
                        assert not head.startswith("\""), "wrong_file"
                        tmp_rel = rel
                        rel = tail
                        if change:
                            tail = "_"+tmp_rel
                        else:
                            tail = tmp_rel
                        incDicWithAdd(attr_head_dict, head, (head, rel, tail))
                        incDicWithAdd(attr_tail_dict, tail, (head, rel, tail))
                        incDicWithAdd(attr_rel_dict, rel, (head, rel, tail))
                        attr_graph_tuples.append((head, rel, tail))
                        continue
                except:
                    continue
                incDicWithAdd(rel_head_dict, head, (head, rel, tail))
                incDicWithAdd(rel_tail_dict, tail, (head, rel, tail))
                incDicWithAdd(rel_rel_dict, rel, (head, rel, tail))
                rel_graph_tuples.append((head, rel, tail))
        graph_tuples = [list(set(rel_graph_tuples))]
        graph_tuples.append(list(set(attr_graph_tuples)))
        # print(len(graph_tuples))
        return graph_tuples, rel_head_dict, rel_tail_dict, rel_rel_dict, attr_head_dict, attr_tail_dict, attr_rel_dict


    @classmethod
    def get_property_reversed(cls, graph_txt, diff_rel=True):
        import re
        graph_tuples = []
        head_dict = {}
        tail_dict = {}
        rel_dict = {}
        with open(graph_txt, encoding='utf-8') as f:
            contents = f.readlines()
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                except:
                    continue
                if diff_rel:
                    rel = "_" + rel
                incDicWithAdd(head_dict, head, (head, tail, rel))
                incDicWithAdd(tail_dict, tail, (head, tail, rel))
                incDicWithAdd(rel_dict, rel, (head, tail, rel))
                graph_tuples.append((head, tail, rel))
        graph_tuples = list(set(graph_tuples))
        # print(len(graph_tuples))
        return graph_tuples, head_dict, tail_dict, rel_dict

    @classmethod
    def get_pku_graph(cls, graph_txt, **kwargs):
        if 'length' in kwargs:
            length = kwargs['length']
        else:
            length = None
        import re
        pku_txt = 'pkubase_complete2.txt'
        pku_tuples = []
        with open(pku_txt, encoding='utf-8') as f:
            if not length:
                contents = f.readlines()
            else:
                contents = []
                for i in range(length):
                    content = f.readline()
                    contents.append(content)
            for i in range(len(contents)):
                try:
                    head, rel, tail = re.split('\t|\n', contents[i])[:-1]
                    head = head.rstrip('.').strip()
                    tail = tail.rstrip('.').strip()
                except:
                    continue
                tail = tail[:-1]
                if rel != '<类型>' and '<' in tail and '>' in tail:
                    pku_tuples.append((head, rel, tail))
                if i%100000 == 0:
                    print(i)
        pku_tuples = list(set(pku_tuples))
        print(len(pku_tuples))
        return pku_tuples

class ReadGraph(ReadGraphFunc):
    '''
    Read tuples from files
    Return data type: tuple list [(head, rel, tail), ...]
    '''
    @classmethod
    def __call__(cls, func_name, **kwargs):
        return getattr(cls,func_name)

    @classmethod
    def data_type_check(cls, graph_tuples, tuple_length=3):
        '''
        Tool to check graph type read from files
        :param graph_tuples: tuple list
        :param tuple_length: str
        '''
        assert isinstance(graph_tuples, list), "Graph must be stored in list"
        print("Graph type checked")
        for i in range(len(graph_tuples)):
            assert isinstance(graph_tuples[i], tuple), "Element in Graph must be tuple"
            assert len(graph_tuples[i]) == tuple_length, "Length of tuple must be {}".format(tuple_length)
        print("Element checked")
        print("check finished")
        return 1

class BaseGetDualGraph:
    def __init__(self, Config, **kwargs):
        read_func_name = Config['read_graph_function']
        file_path = Config['graph_file_path']
        _readfunc = ReadGraph.__call__(read_func_name)
        _graph = _readfunc(file_path, **kwargs)
        if isinstance(_graph, list):
            self.graph = _graph
            self.graph_head_triples, self.graph_tail_triples, self.graph_rel_triples = None, None, None
        elif isinstance(_graph, tuple) and len(_graph) == 4:
            self.graph, self.graph_head_triples, self.graph_tail_triples, self.graph_rel_triples = _graph
        elif isinstance(_graph, tuple) and len(_graph) == 7:
            self.rel_pro_graph, self.graph_head_triples, self.graph_tail_triples, self.graph_rel_triples, \
            self.attr_head_triples, self.attr_tail_triples, self.attr_rel_triples = _graph
            
            self.graph, self.attr_graph = self.rel_pro_graph
        else:
            raise InterruptedError("the graph method we create is only support two type, ret 4 params or just one.")
        print("read graph done")

    def __call__(self, isTrans=False):
        dual_graph, dict2rel = self.get_dual_graph_from_tuples(self.graph, isTrans=isTrans)
        return dual_graph, dict2rel

    def _rfuc(self, triple_list, ent_num, rel_num):
        head = dict()
        tail = dict()
        rel_count = dict()
        for triple in triple_list:
            if triple[1] not in rel_count:
                rel_count[triple[1]] = 1
                head[triple[1]] = set()
                tail[triple[1]] = set()
                head[triple[1]].add(triple[0])
                tail[triple[1]].add(triple[2])
            else:
                rel_count[triple[1]] += 1
                head[triple[1]].add(triple[0])
                tail[triple[1]].add(triple[2])

        return head, tail

    def get_dual_input(self, head, tail):
        count_r = len(head)
        dual_A = np.zeros((count_r, count_r))
        for i in range(count_r):
            for j in range(i+1, count_r):
                a_h = len(head[i] & head[j]) / len(head[i] | head[j])
                a_t = len(tail[i] & tail[j]) / len(tail[i] | tail[j])
                dual_A[i][j] = a_h + a_t
        return dual_A

    def get_dual_graph(self, dual_A, dict2rel:dict=None):
        dual_graph = []
        for i in range(len(dual_A)):
            for j in range(i+1, len(dual_A)):
                if dual_A[i][j] > 1e-5:
                    if isinstance(dict2rel, dict):
                        dual_graph.append((dict2rel[i], dual_A[i][j], dict2rel[j]))
                    else:
                        dual_graph.append((i, dual_A[i][j], j))
        return dual_graph

    def get_dual_graph_from_tuples(self, triple_list, isTrans:bool=False):
        start = time.time()
        ent2dict, rel2dict = get_tuples_dict(triple_list)
        phase1 = time.time()
        print('get tuples dict cost: {}'.format(phase1-start))
        embeded_tuples = embed_tuples(triple_list, ent2dict, rel2dict)
        phase2 = time.time()
        print('embed tuples cost: {}'.format(phase2-phase1))
        dict2rel = transpose_dict(rel2dict)
        phase3 = time.time()
        print('transpose dict cost: {}'.format(phase3-phase2))
        head, tail = self._rfuc(embeded_tuples, len(ent2dict), len(rel2dict))
        phase4 = time.time()
        print('rfunc cost: {}'.format(phase4-phase3))
        dual_A = self.get_dual_input(head, tail)
        phase5 = time.time()
        print('get dual input cost: {}'.format(phase5-phase4))
        if isTrans:
            dual_graph = self.get_dual_graph(dual_A, dict2rel)
        else:
            dual_graph = self.get_dual_graph(dual_A)
        phase6 = time.time()
        print('get dual graph cost: {}'.format(phase6-phase5))
        return dual_graph, dict2rel

if __name__ == "__main__":
    Config = {'read_graph_function':'get_pku_graph',
              'graph_file_path':'pkubase-complete2.txt'}
    GraphCls = BaseGetDualGraph(Config, length=2600000)
    graph = GraphCls.graph
    rel_num_dict = {}
    dual_graph, dict2rel = GraphCls.get_dual_graph_from_tuples(graph, isTrans=False)