### Uasage
执行文件：  
DirectedLouvain: 
```
run_modularity.py: 多次执行社区发现；
modularity_with_property.py: 与属性图相关的社区发现；
analy_ent_cls.py: 对社区发现结果进行统计分析；
```

**注意**  
调用C\++的社区发现的主要代码在DirectedLouvain中的directedLouvain.py中，其中bin_path指定可执行命令，注意bin_path为C\++可执行代码位置，这里无须修改。

设置文件: settings

执行设置说明：
run_modularity.py: 主要对原图或者时对偶图进行社区发现  
执行设置， multi_modularity.yaml
```
graph_setting:
    triple_txt: path to graph triplets file
    read_graph_function: name of graph func
    is_origin_graph: bool, 是否直接将triple_txt作为原图进行社区发现，default true,  
                     如果为false,执行read_graph_func操作之后再进行社区发现
    del_tmp_file: bool，default false，不删除代码执行阶段保留文件
    seed: int, 123456，随机种子
    is_dual_graph: bool, default false, 不为原图对偶图社区发现
    weight_property:  None or float,全图社区发现时，weight property权重，在输入转换时用到
modularity_setting:
    ratio: null or float, 社区数目在当前比例下停止执行
    com_node_num: null or int，社区节点数目在当前节点数下停止执行；
    （以上两个若都为none值，那么如果节点数目在平均社区节点数目以下，则停止执行,  
    ratio的优先级别高于com_mode_num级别)
    iter_num: int，最多可以执行社区发现的轮数
    init_partition_file: str, default none, 存储最开始划分的区域的文件位置
    precision: float,0.0035， 停止社区发现模块度增长的精度，
    display_level: -1, int, 显示社区发现的轮数
    verbose: true, bool, 是否打印社区发现中间信息
    with_weights: true， bool， 是否考虑权重信息
outfile: path to save the outputs
```

modularity_with_property.py: 
主要对属性图，关系图，以及全图进行社区发现  
配置文件: rel_attr_community.yaml  
```
graph_setting:
    triple_txt: 同上
    read_graph_function: 同上
    is_origin_graph: 同上
    del_tmp_file: 同上
    seed: 同上
    is_dual_graph: 同上
modularity_setting:
    ratio: 同上
    com_node_num: 同上
    iter_num: 同上
    init_partition_file: 同上
    precision:同上
    display_level: 同上
    verbose: 同上
    with_weights: 同上
attr_modularity_setting:
    ratio: 同上
    com_node_num: 同上
    iter_num: 同上
    init_partition_file: 同上
    precision: 同上
    display_level: 同上
    verbose: 同上
    with_weights: 同上
attr_config:
    graph_file_path: path to属性图
    read_graph_function: str，属性图读图方程
attr_lower_bounds: null
outfile: 输出存储路径
```

analy_ent_cls.py: 利用统计信息分析社区聚类结果（这里只设计了属性图相关，效果一般）  
设置文件: analy_ent.yaml  
```
init_params:
    read_graph_func: 同上
    graph_path: path to graph
    community_path: path to community results
    is_attr: bool, default true, 是否为属性图
attr_info_params:
    ent_num_lower_bound: null or in t, 当社区节点数目满足当前数目要求才会进行划分
    num_per_attr: null or int: 一个属性的节点数目超过当前数目才会被认为是重要节点
    ratio_per_attr: null or float： 一个属性的节点数目超过当前社区所有节点的这一比例，才会被认为是重要节点
    (num_per_attr和ratio_per_attr都为nouns，重要级别为社区总节点数目关于属性的平均数，两者的num_per_attr的优先级别较高)
    save_parent_path: 存储的父路径
    save_path:
        community_graphs_json: 存储的社区图
        left_related_infos_json: 留下的社区关系图
        left_significants_json: 主要的重要属性图
        no_attr_comm_json: 无属性的社区图 
        single_ent_comm_json: 实体数目少于等于1的社区
```
现有的可供选择的读图的func
```
get_dual_graph.py-ReadGraphFunc:
（这里的针对性处理都与pkubase的特征相关，如果图有变化，需要根据图来修改这一部分代码）
base_get_graph: 直接读取图中的所有的实体 
get_graph_with_entity: 同上，但是会返回头、尾实体以及关系属性的位置字典
get_graph_with_only_rel_no_property: 获取图中的实体关系图，剔除树形图
get_graph_with_property_reversed_no_rel: 获取图中的属性图，并且将属性和尾实体关系对调
get_graph_with_rel_and_property_reverse: 获取图中的树形图和关系图，并且对调属性图当中的尾实体和关系对调
get_split_graph_with_rel_and_property_reversed: 将图中的实体图和属性图分开，并且把属性图当中的尾实体和关系对调
get_property_reversed:将树形图的尾实体和关系对调
get_pku_graph: 获得pkubase的图谱
```