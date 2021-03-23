import json

def read_community(result_file):
    with open(result_file, encoding='utf-8') as f:
        results = json.load(f)
    community_list = {}
    for key in results:
        temp_list = []
        for x in results[key]:
            if '公式' in x:
                temp_list.append(x)
        if len(temp_list) > 1:
            community_list[key] = temp_list
    return community_list
        
if __name__ == "__main__":
    result_file = "dysen_sphere_rel_community_with_weight.json"
    community_file = "dysen_sphere_community_result_with_weight.json"
    community_list = read_community(result_file)
    # print(community_list)
    with open(community_file,'w',encoding='utf-8') as f:
        json.dump(community_list, f, ensure_ascii=False, indent=4)
    