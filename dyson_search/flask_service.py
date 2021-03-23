from flask import Flask, jsonify, request

from read_tuples import DysonTuplesAnalysis
from write_excel import write_excel
import json

# 创建服务
app = Flask(__name__)

@app.route("/dyson_sphere_analysis", methods=['post'])
def dyson_sphere_analysis():
    """
    config: "products_info": {product: count}
            "dyson_file_path": str
            "extra_resources": list
            "save_excel_path": str
    """
    config = request.get_data()
    config_json = json.loads(config.decode("utf-8"))
    all_products_plans = {}
    products_info = config_json["products_info"]
    dyson = DysonTuplesAnalysis(config_json["dyson_file_path"], config_json["extra_resources"])
    for key in products_info.keys():
        plans = dyson(key, products_info[key])
        all_products_plans[key] = {"plans": plans, "count": products_info[key]}
    write_excel(config_json["save_excel_path"], all_products_plans)
    return "1"

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8802,debug=True)