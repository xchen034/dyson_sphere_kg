import os
import sys
basepath = os.path.dirname(os.path.abspath(__file__))
basepath = os.path.dirname(os.path.dirname(basepath))
sys.path.append(basepath)

from pathlib import Path
from typing import Union
import shutil

from modularity.preprocess.convert_triple_to_cplus_input import convert_triple_to_needs
from modularity.preprocess.post_process import ProcessModularity

bin_path = os.path.join(basepath, "modularity", "DirectedLouvain-CPlusMain", "bin")
tmp_idx = -1

def create_tmp_file():
    tmp_basepath = os.path.join(basepath, 'tmp')
    global tmp_idx
    if not os.path.exists(tmp_basepath):
        os.makedirs(tmp_basepath)
    else:
        tmp_idx += 1
        tmp_basepath = os.path.join(basepath, "tmp_%d"%tmp_idx)
    return tmp_basepath

class Py2CPlusDL:
    @classmethod
    def convert_triple_to_bin(cls, origin_triple_txt:str, out_bin_file:str, out_weights_file:Union[str, None]=None, direct:bool=True, save_node2idx:Union[str, None]=None, **kwargs):
        assert origin_triple_txt is not None, "you should given the input file."
        assert out_bin_file is not None, "you should define the output file path."
        tmp_basepath = create_tmp_file()
        tmp_filename = os.path.join(tmp_basepath, 'tmp_convert_bin.txt')
        convert_triple_to_needs(filename=origin_triple_txt, outfile=tmp_filename, direct=direct, save_node2idx=save_node2idx, **kwargs)
        command_args = "-i %s -o  %s"%(tmp_filename, out_bin_file)
        parent_path = Path(out_bin_file).parent
        if not parent_path.exists():
            os.makedirs(parent_path)
        if out_weights_file is not None:
            parent_path = Path(out_weights_file).parent
            if not parent_path.exists():
                os.makedirs(parent_path)
            command_args += " -w %s"%out_weights_file
        command_name = os.path.join(bin_path, "convert")
        command = "%s %s"%(command_name, command_args)
        os.system(command)
        # os.removedirs(tmp_basepath)

        shutil.rmtree(tmp_basepath, ignore_errors=True)

    @classmethod
    def cluster_modularity(cls, output_graph_tree:str, input_bin_file:str, init_partition_file:Union[str, None]=None, weight_bin_file:Union[str, None]=None, precision:Union[float, None]=None, display_level:Union[int, None]=None, verbose:Union[bool, None]=None,\
            seed:Union[int, None]=None, **kwargs):
        assert output_graph_tree is not None, "you should pass the save graph path"
        assert input_bin_file is not None, "you should pass the bin file path"
        out_parent = Path(output_graph_tree).parent
        if not out_parent.exists():
            os.makedirs(out_parent)
        command_args = ""
        out_parent = Path(output_graph_tree).parent
        if not out_parent.exists():
            os.makedirs(out_parent)
        if precision is not None:
            command_args += " -q %f"%(precision)
        if init_partition_file is not None:
            command_args += " -p %s"%(init_partition_file)
        if display_level is not None:
            command_args += " -l %d"%(display_level)
        if verbose is not None and verbose:
            command_args += " -v"
        if weight_bin_file is not None:
            command_args += " -w %s"%weight_bin_file
        if seed is not None:
            command_args += " -s %d"%seed
        command_name  = os.path.join(bin_path, "community")
        command = "%s %s"%(command_name, input_bin_file)+command_args+' > %s'%(output_graph_tree)
        os.system(command)

    @classmethod
    def post_process(cls, filename: str, labelfile:str, outfile:Union[str, None], node2node_renumber:Union[str, None]=None, **kwargs)->dict:
        return ProcessModularity.reverse_graph_tree(filename=filename, labelfile=labelfile, outfile=outfile, node2node_renumber=node2node_renumber)


    @classmethod
    def cluster2community(cls, input_bin_file:str, labelfile:str, outfile:Union[str, None], output_graph_tree:Union[str, None]=None, node2node_renumber:Union[str, None]=None, init_partition_file:Union[str, None]=None, weight_bin_file:Union[str, None]=None, precision:Union[float, None]=None, display_level:Union[int, None]=None, verbose:Union[bool, None]=None,\
            seed:Union[int, None]=None, **kwargs)->dict:
        tmp_basepath = create_tmp_file()
        if output_graph_tree is None:
            output_graph_tree = os.path.join(tmp_basepath, "tmp_graph.tree")
        if outfile is None:
            outfile = os.path.join(tmp_basepath, "last_community.json")
        cls.cluster_modularity(output_graph_tree=output_graph_tree, input_bin_file=input_bin_file, init_partition_file=init_partition_file, weight_bin_file=weight_bin_file, precision=precision, display_level=display_level, verbose=verbose, seed=seed, **kwargs)
        community = cls.post_process(filename=output_graph_tree, labelfile=labelfile, outfile=outfile, node2node_renumber=node2node_renumber, **kwargs)
        # os.removedirs(tmp_basepath)
        shutil.rmtree(tmp_basepath, ignore_errors=True)
        return community

    @classmethod
    def convert_and_community(cls, origin_triple_txt:str, labelfile:Union[str,None], outfile:Union[str, None], out_bin_file:Union[str, None]=None, out_weights_file:Union[str, None]=None, direct:bool=True, save_node2idx:Union[str, None]=None, \
        output_graph_tree:Union[str, None]=None, init_partition_file:Union[str, None]=None, precision:Union[float, None]=None, display_level:Union[int, None]=None, verbose:Union[bool, None]=None, seed:Union[int, None]=None, **kwargs):
        tmp_basepath = create_tmp_file()
        if out_bin_file is None:
            out_bin_file = os.path.join(tmp_basepath, "tmp_graph.bin")
        cls.convert_triple_to_bin(origin_triple_txt=origin_triple_txt, out_bin_file=out_bin_file, out_weights_file=out_weights_file, direct=direct, save_node2idx=save_node2idx, **kwargs)
        node2node_renumber = None
        if labelfile is None:
            labelfile = save_node2idx
        else:
            node2node_renumber = save_node2idx
        community = cls.cluster2community(input_bin_file=out_bin_file, labelfile=labelfile, outfile=outfile, output_graph_tree=output_graph_tree, node2node_renumber=node2node_renumber, init_partition_file=init_partition_file, \
            weight_bin_file=out_weights_file, precision=precision, display_level=display_level, verbose=verbose, seed=seed, **kwargs)
        # os.removedirs(tmp_basepath)
        shutil.rmtree(tmp_basepath, ignore_errors=True)
        return community
