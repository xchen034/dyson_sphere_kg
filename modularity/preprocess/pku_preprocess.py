import os
import sys

basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from tqdm import tqdm
import math
from collections import OrderedDict
import logging
logging.getLogger()

from modularity.utils.io_utils import read_from_file, write_to_file, write_csv, dump_json, load_json
from modularity.utils.obj_utils import incDic, appendDic

def ent_process(entity):
    '''
    针对当前数据集当中的实体表达方式，拆解出最终的数据
    '''
    entity = entity.strip()
    entity = entity.strip('<|>.。,，":\'：“”‘')
    entity = entity.strip('\"')
    return entity

def parse_line(line):
    ent1, rel, ent2 = line.split('\t')
    ent2 = ent2.rstrip('.').strip()
    rel = ent_process(rel)
    ent1 = ent_process(ent1)
    ent2 = ent_process(ent2)
    return ent1, rel, ent2
            
def get_all_entities(file_name, entity_json, ent_neo_csv, ent_csv_header=("id:ID","name",":LABEL"), parse_line=parse_line):
    lines = read_from_file(file_name)
    entities = {}
    idx = 0
    csv_data = []
    for line in tqdm((range(len(lines)))):
        line = lines[line].strip()
        try:
            ent1, rel, ent2 = parse_line(line)
        except:
            print(line.split('\t'))
            continue
        if ent1 not in entities:
            incDic(entities, ent1, idx)
            idx += 1
            csv_data.append((str(idx), ent1, 'Entity'))
        if ent2 not in entities:
            incDic(entities, ent2, idx)
            idx += 1
            csv_data.append((str(idx), ent2, 'Entity'))
    if ent_neo_csv:
        write_csv(ent_neo_csv, csv_data, ent_csv_header)
    dump_json(entity_json, entities)
    return entities

def get_all_rels(file_name, rel_json, rel_neo_csv, entities=None, rel_csv_header=(":START_ID",":END_ID",":TYPE","name"), parse_line=parse_line):
    lines = read_from_file(file_name)
    relations = {}
    idx = 0
    rel_data = []
    if not entities:
        entities = get_all_entities(file_name, None, None)
    for line in tqdm(range(len(lines))):
        line = lines[line].strip()
        try:
            ent1, rel, ent2 = parse_line(line)
        except:
            print(line)
            continue
        if rel not in relations:
            incDic(relations, rel, idx)
            idx += 1
        rel_data.append((entities[ent1], entities[ent2], 'Relation', rel))
    logger.info("origin relationships: %d"%len(rel_data))
    rel_data = list(set(rel_data))
    logger.info("duplicated data deleted: %d"%len(rel_data))
    write_csv(rel_neo_csv, rel_data, rel_csv_header)
    dump_json(rel_json, relations)
    return relations

def get_type_dic(file_name, json_file, type_key='<类型>', encoding_format='utf-8', parse_line=parse_line):
    lines = read_from_file(file_name)
    ent_types_maps = {}
    for line in tqdm(range(len(lines))):
        line = lines[line].strip()
        try:
            ent1, rel, ent2 = parse_line(line)
        except:
            print(line)
            continue
        if rel == type_key:
            appendDic(ent_types_maps, ent1, ent2)
    dump_json(json_file, ent_types_maps)
    return ent_types_maps

def get_type2ents(file_name, json_file, ent_type_maps=None, type_key='<类型>', encoding_format='utf-8'):
    if ent_type_maps is None:
        ent_type_maps = get_type_dic(file_name, None, type_key, encoding_format)
    type2ents_map = {}
    for ent, types in ent_type_maps.items():
        for typ in types:
            appendDic(type2ents_map, typ, ent)
    logger.info("number of types: %d"%len(type2ent2_map))
    dump_json(json_file, type2ents_map)

def get_duplicated_relations(file_name):
    rels = load_json(file_name)
    new_rels = {}
    idx = 0
    for key, val in rels.items():
        new_rel = ent_process(key)
        if new_rel not in new_rels:
            incDic(new_rels, new_rel, idx)
            idx += 1
        else:
            print(new_rel, key)

def get_triplets_from_file(file_name, save_file, parse_line=parse_line):
    lines = read_from_file(file_name)
    triplets = set()
    count = 0
    for line in tqdm(range(len(lines))):
        line = lines[line].strip()
        triples = parse_line(line)
        ent1, rel, ent2 = triples
        if (not rel) or (not ent1) or (not ent2):
            print(line)
            print(ent1, rel, ent2)
            count +=1 
            continue
        tris = '\t'.join(triples)+'\n'
        tries = tris.strip().split('\t')
        if len(tries) < 3:
            logger.info(line)
            logger.info("%s:%s:%s"%(ent1, rel, ent2))
            continue
        triplets.add('\t'.join(triples)+'\n')
    logger.info("filtered num: %d"%count)
    write_to_file(save_file, list(triplets))

def parse_clean_line(line):
    triples = line.strip().split('\t')
    if len(triples) != 3:
        print(triples)
    return triples

def sorted_dict(nums_dic):
    ret_dic = OrderedDict()
    sorted_dic = sorted(nums_dic.items(), key=lambda x:x[1], reverse=True)
    for key, val in sorted_dic:
        ret_dic[key] = val
    return ret_dic

def get_lines_format(triplets):
    all_lines = []
    for tris in triplets:
        all_lines.append('\t'.join(tris)+'\n')
    # print(len(all_lines))
    return all_lines

def split_train_valid_test_triplets(file_name, rel_tris_num, save_files, train_valid_test=(0.8, 0.1, 0.1), parse_line=parse_clean_line):
    lines = read_from_file(file_name)
    rel_with_tris = {}
    for line in tqdm(range(len(lines))):
        line = lines[line].strip()
        triples = parse_line(line)
        ent1, rel, ent2 = triples
        appendDic(rel_with_tris, rel, triples)
    train_triplets = []
    valid_triplets = []
    test_triplets = []
    rel_tri_nums = {}
    for rel, triplets in rel_with_tris.items():
        num = len(triplets)
        rel_tri_nums[rel] = num
        test_num = math.ceil(train_valid_test[2]*num)
        valid_num = math.ceil(train_valid_test[1]*num)
        # print(test_num)
        tests = triplets[:test_num]
        valids = triplets[test_num:valid_num+test_num]
        trains = triplets[valid_num+test_num:]
        train_triplets.extend(trains)
        valid_triplets.extend(valids)
        test_triplets.extend(tests)
    rel_tri_nums = sorted_dict(rel_tri_nums)
    dump_json(rel_tris_num, rel_tri_nums)
    write_to_file(save_files[0], get_lines_format(train_triplets))
    write_to_file(save_files[1], get_lines_format(valid_triplets))
    write_to_file(save_files[2], get_lines_format(test_triplets))
    
    
if __name__ == "__main__":
    file_name = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/pkubase-complete.txt'
    ent_neo_csv = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/entities_no_dup.csv'
    rel_neo_csv = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/relations_no_dup.csv'
    entity_json = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/entities_no_dup.json'
    rel_json = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/relations_no_dup.json'
    ent_types_map_json = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/ent_types_map_no_dup.json'
    type2ent2_map = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/type2ent2_map_no_dup.json'
    # entities = get_all_entities(file_name, entity_json, ent_neo_csv)
    # relations = get_all_rels(file_name, rel_json, rel_neo_csv, entities)
    # ent_types_maps = get_type_dic(file_name, ent_types_map_json)
    # get_type2ents(file_name, type2ent2_map, ent_types_maps)
    # print("number of entities", len(entities))
    # print("number of relations", len(relations))
    old_rel_json = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/relations.json'
    # get_duplicated_relations(old_rel_json)
    all_pkubase_txt = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/all_pkubase_triplets.txt'
    # get_triplets_from_file(file_name, all_pkubase_txt)
    rel_tris_num = '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/relations_triplets_nums.json'
    save_files = [
        '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/pku_train.txt',
        '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/pku_valid.txt',
        '/home/aiteam/lini/dataset/PKUBASE/pkubase-complete-2020/pku_test.txt'
    ]
    split_train_valid_test_triplets(all_pkubase_txt, rel_tris_num, save_files)
