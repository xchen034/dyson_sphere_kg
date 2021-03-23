import pandas as pd

def write_excel(excel_path:str, plans_dict):
    with pd.ExcelWriter(excel_path) as writer:
        target_name_list = list(plans_dict.keys())
        for target_name in target_name_list:
            target_plans = plans_dict[target_name]["plans"]
            target_count = plans_dict[target_name]["count"]
            head_df = pd.DataFrame({"目标产物": [target_name], "产量/s": [target_count]})
            start_row = 3
            head_df.to_excel(writer, sheet_name=target_name, index=False)
            for i in range(len(target_plans)):
                plan_index_df = pd.DataFrame({"方案{}".format(i+1):[]})
                plan_index_df.to_excel(writer, sheet_name=target_name, startrow=start_row, index=False)
                start_row += 1
                temp_plan = target_plans[i][0]
                temp_extra = target_plans[i][1]
                temp_plan.to_excel(writer, sheet_name=target_name, startrow=start_row)
                start_row += len(temp_plan)+2
                if len(temp_extra):
                    temp_extra.to_excel(writer, sheet_name=target_name, startrow=start_row)
                    start_row += len(temp_extra)+2
    print("save to {} finished".format(excel_path))