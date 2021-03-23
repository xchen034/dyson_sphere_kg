import json
import re
import os

def read_txt(txt_path:str):
    with open(txt_path, encoding="utf-8") as f:
        contents = f.readlines()
        for i in range(len(contents)):
            contents[i] = re.split('\n|\t', contents[i])[:-1]
    return contents

def get_links_dict(tuples):
    product_list = []
    formula_list = []
    # print(tuples)
    links_list = []
    nodes_list = []
    for i in range(len(tuples)):
        if tuples[i][1] not in ["产地", '类型', '生产时间(s)']:
            for j in [0,2]:
                if '公式' in tuples[i][j]:
                    formula_list.append(tuples[i][j])
                    temp = {"size":12,"group":0,"id":tuples[i][j],"class":"公式"}
                    if temp not in nodes_list:
                        nodes_list.append(temp)
                else:
                    product_list.append(tuples[i][j])
                    temp = {"size":8,"group":1,"id":tuples[i][j],"class":"产物"}
                    if temp not in nodes_list:
                        nodes_list.append(temp)
            temp = {"source": tuples[i][0],"target":tuples[i][2],"value":3}
            if temp not in links_list:
                links_list.append(temp)
    links_dict = {"nodes":nodes_list, "links":links_list}
    return links_dict

def get_tuples_dict(tuples):
    entity_dict = {}
    for i in range(len(tuples)):
        head = tuples[i][0]
        rel = tuples[i][1]
        tail = tuples[i][2]
        if rel in ["产地", '类型', '生产时间(s)']:
            if head not in entity_dict.keys():
                entity_dict[head] = {}
            if rel not in entity_dict[head].keys():
                entity_dict[head][rel] = [tail]
            else:
                entity_dict[head][rel].append(tail)
        else:
            if '公式' in head:
                if head not in entity_dict.keys():
                    entity_dict[head] = {}
                if '产物' not in entity_dict[head].keys():
                    entity_dict[head]['产物']= ["{}*{}".format(tail, rel)]
                else:
                    entity_dict[head]['产物'].append("{}*{}".format(tail, rel))
                if tail not in entity_dict.keys():
                    entity_dict[tail] = {}
                if '产自' not in entity_dict[tail].keys():
                    entity_dict[tail]['产自'] = [head]
                else:
                    entity_dict[tail]['产自'].append(head)
            elif '公式' in tail:
                if tail not in entity_dict.keys():
                    entity_dict[tail] = {}
                if '原料' not in entity_dict[tail].keys():
                    entity_dict[tail]['原料']= ["{}*{}".format(head, rel)]
                else:
                    entity_dict[tail]['原料'].append("{}*{}".format(head, rel))
                if head not in entity_dict.keys():
                    entity_dict[head] = {}
                if '用于' not in entity_dict[head].keys():
                    entity_dict[head]['用于'] = [tail]
                else:
                    entity_dict[head]['用于'].append(tail)
                
            else:
                print("{}-{}-{}".format(head, rel, tail))
    return entity_dict
                
def _modify_entity_dict(entity_dict:dict)->None:
    for key in entity_dict.keys():
        for _key in entity_dict[key].keys():
            if len(entity_dict[key][_key]) == 1:
                entity_dict[key][_key], = entity_dict[key][_key]
            else:
                temp = list(set(entity_dict[key][_key]))
                _str = ''
                for i in range(len(temp)):
                    _str += temp[i]
                    _str += " "
                _str = _str[:-1]
                entity_dict[key][_key] = _str

if __name__ == "__main__":
    cur_path = os.getcwd()
    # print(cur_path)
    txt_path = cur_path+"/dyson_visualization/dyson_sphere_tuples.txt"
    tuples = read_txt(txt_path)
    link_dict = get_links_dict(tuples)
    print(link_dict)
    entity_dict = get_tuples_dict(tuples)
    _modify_entity_dict(entity_dict)
    # for key in entity_dict.keys():
        # print("{}: {}".format(key, entity_dict[key]))
    with open("dyson_visualization/dyson_all.json", "w", encoding="utf-8") as f:
        json.dump(entity_dict, f, ensure_ascii=False, indent=4)
    with open("dyson_visualization/dyson_links.json", "w", encoding="utf-8") as f:
        json.dump(link_dict, f, ensure_ascii=False, indent=4)