import numpy as np
import pickle
import networkx as nx
import os
from id_methods.CC import CC
from id_methods.CFIDF import CFIDF
from id_methods.CNE import CNE
from id_methods.Spatial_LDA import Spatial_LDA
from sm_techs.Naive import Naive
from sm_techs.HMRF import HMRF
import argparse
from itertools import chain
import logging
import sys
import inspect
import time


def cns_info(ds, n_cns, cns, logger):
    data = ds.data
    info_ent, info_pat, info_size = {i: [] for i in range(n_cns)}, np.zeros(n_cns), np.zeros(n_cns)
    for sample in data:
        for image in data[sample]:
            graph = nx.Graph(data[sample][image].edge_indices)
            for edge in graph.edges:
                if cns[sample][image][edge[0]] != cns[sample][image][edge[1]]:
                    graph.remove_edge(edge[0], edge[1])
            for i in nx.connected_components(graph):
                info_ent[cns[sample][image][list(i)[0]]] += data[sample][image].cts_oh[list(i)].tolist()
                info_pat[cns[sample][image][list(i)[0]]] += 1
                info_size[cns[sample][image][list(i)[0]]] += len(i)
    for i in info_ent:
        if not info_ent[i]:
            info_ent[i] = 0
        else:
            p = np.array(info_ent[i]).mean(axis=0)
            p = p[p.nonzero()]
            info_ent[i] = -(p * np.log2(p)).sum()
    info_ent = np.array(list(info_ent.values()))
    logger.info(f'Entropy: {(info_ent * info_size / info_size.sum()).sum():.3f}')
    logger.info(f'Size: {sum(info_size) / sum(info_pat):.2f}')


def make_logger(filename):
    print(f'=> {filename}.log')
    file_handler = logging.FileHandler(filename=f'{filename}.log', mode='w')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stdout_handler], format='%(message)s', force=True)
    logger = logging.getLogger()
    return logger


def identify(ds_path, out_dir, cns_path, method, verbose, **params):
    ds = pickle.load(open(ds_path, 'rb'))
    ds.cts_sg_to_oh()
    if not cns_path:
        params_list = inspect.getfullargspec(eval(method)).args[1:]
        params_values = [params[param] for param in params_list]
        id_start = time.time()
        cns, feats = eval(method)(ds, *params_values)
        id_end = time.time()
        filename = os.path.join(out_dir, ('cns' + '_{}={}' * len(params_list)).format(*chain(*zip(params_list, params_values))))
        pickle.dump(cns, open(f'{filename}.pkl', 'wb'))
    else:
        cns, feats = pickle.load(open(cns_path, 'rb')), None
        filename = os.path.join(out_dir, os.path.split(cns_path)[1].split('.')[0])
    if verbose:
        logger = make_logger(filename)
        if not cns_path:
            logger.info(f'Identification time: {id_end - id_start:.2f} s')
        cns_info(ds, params['n_cns'], cns, logger)
    for tech in ['Naive', 'HMRF']:
        if params[tech]:
            sm_start = time.time()
            if tech == 'Naive':
                cns_smoothed = eval(tech)(ds, cns, feats, *params[tech])
            elif tech == 'HMRF':
                cns_smoothed = eval(tech)(ds, cns, params['n_cns'], *params[tech])
            sm_end = time.time()
            pickle.dump(cns_smoothed, open(f'{filename}_{tech}.pkl', 'wb'))
            if verbose:
                logger = make_logger(f'{filename}_{tech}')
                logger.info(f'Smoothing time: {sm_end - sm_start:.2f} s')
                cns_info(ds, params['n_cns'], cns_smoothed, logger)


def required_length(nmin, nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                msg='argument "{f}" requires {nmin}~{nmax} arguments'.format(f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Identify and smooth CNs.', formatter_class=argparse.RawTextHelpFormatter)
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('--ds_path', type=str, help='input dataset (.pkl) path', required=True)
    required.add_argument('--out_dir', type=str, help='output directory', required=True)
    required.add_argument('--n_cns', type=int, help='number of CNs', required=True)
    optional.add_argument('--cns_path', type=str, help='only do smoothing using the cellular neighborhood file (.pkl) at the given path')

    subparsers = parser.add_subparsers(dest='method', help='identification method')

    parser_CC = subparsers.add_parser('CC')
    parser_CC._action_groups.pop()
    required_CC = parser_CC.add_argument_group('required arguments')
    required_CC.add_argument('--m', type=int, help='number of neighbors', required=True)

    parser_CFIDF = subparsers.add_parser('CFIDF')
    parser_CFIDF._action_groups.pop()
    required_CFIDF = parser_CFIDF.add_argument_group('required arguments')
    optional_CFIDF = parser_CFIDF.add_argument_group('optional arguments')
    required_CFIDF.add_argument('--eps', type=float, help='pixel radius of neighborhoods', required=True)
    required_CFIDF.add_argument('--r', type=float, help='resolution of Louvain algorithm', required=True)
    optional_CFIDF.add_argument('--include_neighbors', action='store_true', help='whether to only include neighbors for each cell')
    optional_CFIDF.add_argument('--n_included', type=int, default=100, help='number of neighbors included for each cell (default: 100)')

    parser_CNE = subparsers.add_parser('CNE')
    parser_CNE._action_groups.pop()
    required_CNE = parser_CNE.add_argument_group('required arguments')
    optional_CNE = parser_CNE.add_argument_group('optional arguments')
    required_CNE.add_argument('--eta', type=float, help='scale parameter of the Gaussian distribution\'s std')
    optional_CNE.add_argument('--include_neighbors', action='store_true', help='whether to only include neighbors for each cell')
    optional_CNE.add_argument('--n_included', type=int, default=100, help='number of neighbors included for each cell (default: 100)')

    parser_Spatial_LDA = subparsers.add_parser('Spatial_LDA')
    parser_Spatial_LDA._action_groups.pop()
    required_Spatial_LDA = parser_Spatial_LDA.add_argument_group('required arguments')
    optional_Spatial_LDA = parser_Spatial_LDA.add_argument_group('optional arguments')
    required_Spatial_LDA.add_argument('--eps', type=float, help='pixel radius of neighborhoods', required=True)
    required_Spatial_LDA.add_argument('--b', type=float, help='scale parameter of the Laplace distribution', required=True)
    optional_Spatial_LDA.add_argument('--train_size_fraction', type=float, default=0.99, help='fraction of training samples (default: 0.99)')
    optional_Spatial_LDA.add_argument('--n_processes', type=int, default=8, help='number of parallel processes (default: 8)')

    optional.add_argument('--Naive', type=int, nargs='+', metavar=('s', 'n_neighbors'), action=required_length(1, 2), help='Naive smoothing technique\ns: minimum size of a CN instance\nn_neighbors: effective only when input cell representions (feats) are None, number of nearest neighbors considered for building CC cell representations (default: 10)')
    optional.add_argument('--HMRF', type=float, nargs='+', metavar=('eps beta', 'include_neighbors n_included max_iter max_iter_no_change'), action=required_length(2, 6), help='HMRF smoothing technique\neps: pixel radius of neighborhoods\nbeta: weight of each neighbor in the same CN\ninclude_neighbors: whether to only include neighbors for each cell (default: False)\nn_included: number of neighbors included for each cell (default: 100)\nmax_iter: the maximum number of iterations (default: 50)\nmax_iter_no_chanage: stop if the loss does not change for some iterations (default: 3)')
    optional.add_argument('--seed', type=int, help='seed for reproducibility')
    optional.add_argument('--verbose', action='store_true', help='whether to print out metric values')

    args = parser.parse_args()
    identify(**vars(args))
