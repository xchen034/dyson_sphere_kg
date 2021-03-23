from read_tuples import DysonTuplesAnalysis
from write_excel import write_excel
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help="path to paramter file")
    args = parser.parse_args()
    _main(args.config_file)

def _main(config_file:str):
    """
    config: "products_info": {product: count}
            "dyson_file_path": str
            "extra_resources": list
            "save_excel_path": str
    """
    with open(config_file) as f:
        config = json.load(f)
    all_products_plans = {}
    products_info = config["products_info"]
    dyson = DysonTuplesAnalysis(config["dyson_file_path"], config["extra_resources"])
    for key in products_info.keys():
        plans = dyson(key, products_info[key])
        all_products_plans[key] = {"plans": plans, "count": products_info[key]}
    write_excel(config["save_excel_path"], all_products_plans)


if __name__ == "__main__":
    main()

