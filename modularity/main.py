from DirectedLouvain.run_modularity import RunModularity
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help="path to paramter file")
    args = parser.parse_args()
    RunMo = RunModularity(args.config_file)
    RunMo()

if __name__ == "__main__":
    main()