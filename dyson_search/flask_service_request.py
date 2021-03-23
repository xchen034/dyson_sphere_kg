import requests
import json

def test_request(config, url="http://127.0.0.1:8802//dyson_sphere_analysis"):
    result = requests.post(url=url, json=config)
    res = result.text
    return res

if __name__ == "__main__":
    config = {"products_info": {"电动机":1,"卡西米尔晶体":2,"氘核燃料棒":1,"碳纳米管":10,"小型运载火箭":1,"太阳帆":5},
              "dyson_file_path": "/Users/chenxi/projects/dyson_sphere_kg/dyson_sphere_tuples.txt",
              "extra_resources": ["硫酸","刺笋结晶","可燃冰","光栅石"],
              "save_excel_path": "test_excel_1.xlsx"}
    res = test_request(config)
    print("res: {}".format(res))
