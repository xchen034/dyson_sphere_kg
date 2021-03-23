import numpy as np
import pandas as pd
import re
import math
from typing import Union

def get_all_entity(tuples: list) -> list:
    entities = []
    for _tuple in tuples:
        if _tuple[1] in ["类型", "产地", "生产时间(s)"]:
            if not "公式" in _tuple[0]:
                entities.append(_tuple[0])
        else:
            entities.append(_tuple[0])
            entities.append(_tuple[-1])
    return list(set(entities))

def get_category_list(tuples:list) -> list:
    category_list = []
    entity_list = []
    for _tuple in tuples:
        if _tuple[1] == "类型":
            category_list.append(_tuple)
            entity_list.append(_tuple[0])
    return category_list, entity_list

class DysonTuples:
    def __init__(self, txt_path:str, extra_resources:list) -> None:
        self.txt_path = txt_path
        self.extra_resources = extra_resources
        self.dyson_tuples = self.read_tuples_txt(txt_path)
        self._all_formulas = self.get_all_formulas()
        self._all_formulas_dict = {}
        self._all_raw_products = self.get_all_raw_products(self.dyson_tuples)
        for formula in self._all_formulas:
            if formula in ["X射线裂解公式",'重氢公式（2）']:
                continue
            self._all_formulas_dict[formula] = self.get_formula_dict(formula)
        self.remove_special_formula()
        self._all_products_formulas_dict = self.get_all_products_formulas_dict(self._all_formulas_dict)
        self._all_products_formulas_dict["氢"].remove("反物质公式")
        self._all_products_formulas_dict["氢"].remove("等离子精炼公式")


    def check_extra_resources(self):
        for resource in self.extra_resources:
            extra_resources = ["硫酸","光栅石","分型硅石","单级磁石","刺笋结晶","金伯利矿石","可燃冰"]
            if resource not in extra_resources:
                raise ValueError("extra_resource must in {}, but {} received".format(extra_resources, resource))

    def read_tuples_txt(self, txt_path: str) -> list:
        with open(txt_path, encoding="utf-8") as f:
            contents = f.readlines()
            tuples = []
            for content in contents:
                head, rel, tail = re.split("\t|\n", content)[:-1]
                tuples.append((head, rel, tail))
        return tuples

    def get_all_products_formulas_dict(self, formulas_dict:dict) -> dict:
        product_formula_dict = {}
        for formula in formulas_dict.keys():
            products = list(formulas_dict[formula]['产物'].keys())
            for _product in products:
                if _product not in product_formula_dict.keys():
                    product_formula_dict[_product] = [formula]
                else:
                    product_formula_dict[_product].append(formula)
        return product_formula_dict

    def get_all_raw_products(self, tuples:list) -> list:
        raw_products = []
        for _tuple in tuples:
            if _tuple[2] == "原料":
                raw_products.append(_tuple[0])
        return raw_products

    def get_all_formulas(self) -> list:
        formulas = []
        for _tuple in self.dyson_tuples:
            if _tuple[-1] == "生产公式":
                formulas.append(_tuple[0])
        return list(set(formulas))
    
    def get_formula_dict(self, formula:str) -> dict:
        temp_list = []
        for _tuple in self.dyson_tuples:
            if formula in _tuple:
                temp_list.append(_tuple)
        formula_dict = self._get_formula_dict_from_list(formula, temp_list)
        return formula_dict

    def _get_formula_dict_from_list(self, formula:str, formula_list:list) -> dict:
        temp_dict = {'名称': formula,'原料':{},'产物':{}}
        for _tuple in formula_list:
            try:
                count = int(_tuple[1])
                if _tuple[0] == formula:
                    temp_dict['产物'][_tuple[-1]] = count
                else:
                    temp_dict['原料'][_tuple[0]] = count 
            except:
                try:
                    temp_dict[_tuple[1]] = int(_tuple[-1])
                except:
                    temp_dict[_tuple[1]] = _tuple[-1]
        return temp_dict

    def find_method(self, target_product:str) -> list:
        '''
        count: nums/s
        '''
        methods = []
        for _tuple in self.dyson_tuples:
            if _tuple[-1] == target_product:
                methods.append(_tuple[0])
        return methods

    def remove_special_formula(self):
        self.all_raw_products.append("硅石")
        self.all_formulas_dict.pop("石材公式")
        if "硫酸" in self.extra_resources:
            self.all_formulas_dict.pop("硫酸公式")
            self.all_raw_products.append("硫酸")
        if "光栅石" in self.extra_resources:
            self.all_formulas_dict.pop("光子合并器公式")
            self.all_formulas_dict.pop("卡西米尔晶体公式")
        else:
            self.all_formulas_dict.pop("光子合并器公式（高效）")
            self.all_formulas_dict.pop("卡西米尔晶体公式（高效）")

        if "分型硅石" in self.extra_resources:
            self.all_formulas_dict.pop("晶格硅公式")
        else:
            self.all_formulas_dict.pop("晶格硅公式（高效）")

        if "单级磁石" in self.extra_resources:
            self.all_formulas_dict.pop("粒子容器公式")
        else:
            self.all_formulas_dict.pop("粒子容器公式（高效）")
        if "刺笋结晶" in self.extra_resources:
            self.all_formulas_dict.pop("碳纳米管公式")
        else:
            self.all_formulas_dict.pop("碳纳米管公式（高效）")
        if "金伯利矿石" in self.extra_resources:
            self.all_formulas_dict.pop("金刚石公式")
        else:
            self.all_formulas_dict.pop("金刚石公式（高效）")
        if "可燃冰" in self.extra_resources:
            self.all_formulas_dict.pop("石墨烯公式")
        else:
            self.all_formulas_dict.pop("石墨烯公式（高效）")

    @property
    def all_formulas(self):
        return self._all_formulas

    @property
    def all_formulas_dict(self):
        return self._all_formulas_dict

    @property
    def all_raw_products(self):
        return self._all_raw_products

    @property
    def all_products_formulas_dict(self):
        return self._all_products_formulas_dict


class DysonTuplesAnalysis(DysonTuples):
    def __init__(self, txt_path, extra_resources:list) -> None:
        super(DysonTuplesAnalysis, self).__init__(txt_path, extra_resources)
    
    def __call__(self, target_product:str, count:float, filter_station_num:int=np.inf):
        plan_list = []
        all_list = self._analysis_method(target_product, count, plan_list)
        for i in range(len(all_list)):
            # all_list[i] = self.analysis_result(all_list[i], filter_station_num)
            all_list[i] = self.analysis_result_pivot_table(all_list[i])
        return all_list

    def analysis_result_pivot_table(self, plan_list:list):
        plan_dict = {"公式":[],"产地":[],"数量":[]}
        extra_dict = {"额外产物":[],"数量/s":[]}
        for _plan in plan_list:
            plan_dict["公式"].append(_plan["公式"])
            plan_dict["产地"].append(_plan["产地"])
            plan_dict["数量"].append(_plan["数量"])
            if "额外产物" in _plan.keys():
                for _extra_product in _plan["额外产物"]:
                    product_name = list(_extra_product.keys())[0]
                    extra_dict["额外产物"].append(product_name)
                    extra_dict["数量/s"].append(_extra_product[product_name])
        plan_df = pd.DataFrame(plan_dict)
        plan_pt = pd.pivot_table(plan_df,index=["公式","产地"],values=["数量"],aggfunc=np.sum)
        extra_df = pd.DataFrame(extra_dict)
        # extra_df["数量/min"] = extra_df["数量/min"].apply(lambda x: x*60)
        extra_pt = pd.pivot_table(extra_df,index=["额外产物"],values=["数量/s"],aggfunc=np.sum)
        return (plan_pt, extra_pt)

    def analysis_result(self, plan_list:list, station_num_filter:int=np.inf) -> dict:
        plan_dict = {"额外产物": {}}
        max_station_num = 0
        for _plan in plan_list:
            if _plan['公式'] not in plan_dict:
                plan_dict[_plan['公式']] = {'产地':_plan['产地'], '数量':_plan['数量']}
            else:
                plan_dict[_plan['公式']]['数量'] += _plan['数量']
                max_station_num = max(max_station_num, plan_dict[_plan['公式']]['数量'])
            if "额外产物" in _plan.keys():
                for _extra_product in _plan["额外产物"]:
                    product_name = list(_extra_product.keys())[0]
                    if product_name not in plan_dict["额外产物"]:
                        plan_dict["额外产物"][product_name] = _extra_product[product_name]
                    else:
                        plan_dict["额外产物"][product_name] += _extra_product[product_name]
        if max_station_num > station_num_filter:
            plan_dict = {}
        return plan_dict

    def update_dict(self, _dict, dict_list):
        for _d in dict_list:
            key = list(_d.keys())[0]
            if key not in _dict:
                _dict[key] = _d[key]
            else:
                _dict[key] += _d[key]
        return _dict

    def _analysis_product_extra(self, product:str, product_count:Union[int, float], extra_products:dict):
        cost_extra_product = {}
        if product in extra_products:
            if product_count < extra_products[product]:
                extra_products[product] = extra_products[product] - product_count
                product_count = 0
                cost_extra_product = {product: -1*product_count}
            else:
                product_count = product_count - extra_products[product_count]
                cost_extra_product = {product: -1*extra_products[product_count]}
                extra_products.pop(product)
        return product_count, extra_products, cost_extra_product

    def _analysis_method(self, target_product:str, count:float, plan_list:list) -> list:
        target_plan_list = self.all_products_formulas_dict[target_product]
        all_plan_list = []
        for _plan in target_plan_list:
            if _plan in plan_list:
                continue
            raw_products = self.all_formulas_dict[_plan]['原料']
            raw_dict = {}
            products = self.all_formulas_dict[_plan]['产物']
            _plan_extra_products = []
            station = self.all_formulas_dict[_plan]['产地']
            product_time = self.all_formulas_dict[_plan]['生产时间(s)']
            station_nums = math.ceil(count*product_time/products[target_product])
            extra_nums = station_nums*products[target_product]/product_time - count
            for _product in products.keys():
                if _product == target_product and extra_nums:
                    _plan_extra_products.append({_product:extra_nums})
                elif _product != target_product:
                    _plan_extra_products.append({_product:station_nums*products[_product]/product_time})
            temp_plan_list = plan_list + [_plan]
            for _product in raw_products:
                if _product not in self.all_raw_products:
                    raw_count = station_nums*raw_products[_product]/product_time
                    raw_plan = self._analysis_method(_product, raw_count, temp_plan_list)
                    raw_dict[_product] = raw_plan
            raw_methods = self.find_all_raw_mehods(raw_dict)
            if _plan_extra_products:
                _plan_dict = {"公式": _plan, "产地": station, "数量": station_nums, "额外产物":_plan_extra_products}
            else:
                _plan_dict = {"公式": _plan, "产地": station, "数量": station_nums}
            if len(raw_methods):
                for i in range(len(raw_methods)):
                    raw_methods[i] += [_plan_dict]
            else:
                raw_methods = [[_plan_dict]]
            all_plan_list+=raw_methods
        return all_plan_list

    def find_all_raw_mehods(self, raw_dict) -> list:
        def find_all_probs(x:list,y:list)->list:
            all_list = []
            for i in range(len(x)):
                if isinstance(x[i], list):
                    temp = x[i]
                else:
                    temp = [x[i]]
                for j in range(len(y)):
                    if isinstance(y[j], list):
                        all_list.append(temp+y[j])
                    else:
                        all_list.append(temp+[y[i]])
            return all_list
        temp_list = []
        if len(raw_dict) == 1:
            return raw_dict[list(raw_dict.keys())[0]]
        for key in raw_dict.keys():
            if not temp_list:
                temp_list = raw_dict[key]
            else:
                temp_list = find_all_probs(temp_list, raw_dict[key])
        return temp_list

if __name__ == "__main__":
    dyson_file_path = "/Users/chenxi/projects/dyson_sphere_kg/dyson_sphere_tuples.txt"
    dyson = DysonTuplesAnalysis(dyson_file_path, ["硫酸","刺笋结晶","可燃冰","光栅石"])
    # print(dyson.all_formulas_dict)
    # for key in dyson.all_products_formulas_dict.keys():
    #     print("{}: {}".format(key, dyson.all_products_formulas_dict[key]))
    # print(dyson.all_raw_products)

    for plan in ["氘核燃料棒"]:#["电动机","卡西米尔晶体","氘核燃料棒","碳纳米管","小型运载火箭","太阳帆"]:
        plans = dyson(plan, 1)
        # print(len(plans))
        for _plan in plans:
            temp_plan = _plan[0]
            temp_extra = _plan[1]
            print(temp_plan)
            print(temp_extra)
            # for key in _plan.keys():
            #     print("{}: {}".format(key, _plan[key]))
            # print("\n\n")