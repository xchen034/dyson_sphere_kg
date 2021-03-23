import os
import sys
import yaml
from pathlib import Path
import logging
import pdb
import json


def make_parent_path(file_path):
    parent = Path(file_path).parent
    if not parent.exists():
        os.makedirs(parent)

def read_from_file(file_name, mode='r', encoding_format='utf-8'):
    if not os.path.exists(file_name):
        raise ValueError("The {} is not exists".format(file_name))
    with open(file_name, mode, encoding=encoding_format) as f:
        lines = f.readlines()
    return lines

def write_to_file(file_name, data, mode='w', encoding_format='utf-8'):
    if not file_name:
        return
    make_parent_path(file_name) 
    with open(file_name, mode, encoding=encoding_format) as f:
        f.writelines(data)

def load_json(json_file, mode='r', encoding_format='utf-8'):
    if not os.path.exists(json_file):
        raise ValueError("The {} is not exists".format(json_file))
    try:
        with open(json_file, mode, encoding=encoding_format) as f:
            data = json.load(f)
        return data
    except:
        raise ValueError("The {} cannot open, please check!".format(json_file))

def dump_json(json_file, json_data, mode='w', encoding_format='utf-8'):
    if not json_file:
        return 
    try:
        make_parent_path(json_file)
        with open(json_file, mode, encoding=encoding_format) as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    except:
        raise ValueError("save failed")

def write_csv(csv_file, csv_data, csv_header=None, mode='w', newline='', encoding_format='utf-8'):
    if not csv_file:
        return None
    try:
        make_parent_path(json_file)
        #with open(csv_file, mode, newline, encoding=encoding_format) as csvf:
        with open(csv_file, 'w', newline='', encoding=encoding_format) as csvf:
            f = csv.writer(csvf)
            if csv_header:
                f.writerow(csv_header)
            for csv_row in csv_data:
                f.writerow(csv_row)
    except:
        raise ValueError("The {} is not right".format(csv_file))

def load_yaml(yaml_file, mode='r', **kwargs):
    if yaml_file is None:
        return {}
    if not os.path.exists(yaml_file):
        raise FileNotFoundError("{} does not exists".format(yaml_file))
    f = open(yaml_file, mode, encoding='utf-8')
    config = yaml.load(f)
    return config

def dump_yaml(out_file, params, mode='w', **kwargs):
    if os.path.exists(out_file):
        logging.info("we will overwrite th %s"%out_file)
    make_parent_path(out_file)
    with open(out_file, mode, encoding='utf-8') as f:
        yaml.dump(params, f, ident=4, allow_unicode=True)

def load_config(config_path, **kwargs):
    if not config_path:
        return {}
    elif isinstance(config_path, dict):
        return config_path
    elif isinstance(config_path, str):
        con_p = Path(config_path)
        suffix = con_p.suffix
        if suffix[1:] == "json":
            config = load_json(config_path)
        elif suffix[1:] == "yaml" or suffix[1:]=="yml":
            config = load_yaml(config_path)
        else:
            raise NotImplementedError("the file you set in config is '%s'"%suffix[1:])
    return config
