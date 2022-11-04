import argparse
import json

parser = argparse.ArgumentParser(description='Identify and smooth cellular neighborhoods.', formatter_class=argparse.RawTextHelpFormatter)

def include_items(items, all_items):
    s = '[ ' + ' | '.join(all_items) + ' ]'
    for item in set(all_items) - set(items):
        s = s.replace(item, ' ' * len(item))
    return s

def include_methods(methods):
    return include_items(methods, ['CC', 'CFIDF', 'CNE', 'LDA'])

def include_techs(techs):
    return include_items(techs, ['Naive', 'HMRF'])

parser.add_argument('ds_path', type=str, help='input dataset path')
parser.add_argument('cn_out_dir', type=str, help='CN output directory')
parser.add_argument('method', type=str, help='identification method')
parser.add_argument('smooth_techs', type=str, help='list of smoothing techniques seperated by space')

parser.add_argument('--m', type=int, help=f'{include_methods(["CC"])} number of neighbors')
parser.add_argument('--eps', type=float, help=f'{include_methods(["CFIDF"])} radius of neighborhoods')
parser.add_argument('--r', type=float, help=f'{include_methods(["CFIDF"])} resolution of Louvain algorithm')
parser.add_argument('--eta', type=float, help=f'{include_methods(["CNE"])} ')
parser.add_argument('--include_all', type=bool, help=f'{include_methods(["CC", "CNE"])} whether to include all cells')
parser.add_argument('--n_included', type=bool, help=f'{include_methods(["CC", "CNE"])} number of cells included')
parser.add_argument('--n_cns', type=int, help=f'{include_methods(["CC", "CFIDF", "CNE", "LDA"])} number of CNs')
parser.add_argument('--seed', type=int, help=f'{include_methods(["CC", "CFIDF", "CNE"])} seed for kmeans clustering')
parser.add_argument('--s', type=str, help=f'{include_techs(["Naive"])} minimum size of a CN instance')
parser.add_argument('--beta', type=str, help=f'{include_techs(["HMRF"])} weight of each neighbor in the same CN')
parser.add_argument('--verbose', type=bool, help='whether to print out metric values')

args = parser.parse_args()
print("Argument values:")
print(json.loads(args.pos_arg))
print(args.opt_pos_arg)
print(args.opt_arg)
print(args.switch)