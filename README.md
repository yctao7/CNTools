# CNTools

## Loading data
Usage:
```
python load.py [-h] --df_path DF_PATH --df_name DF_NAME --out_dir OUT_DIR [--ct_order_path CT_ORDER_PATH]
```
Description of arguments can be accessed by ```python load.py -h```.
```
Preprocess a cell table and make it a dictionary dataset.

required arguments:
  --df_path DF_PATH     input table (.csv) path
  --df_name DF_NAME     table name
  --out_dir OUT_DIR     output directory

optional arguments:
  --ct_order_path CT_ORDER_PATH
                        input CT order file (.json) path
```

## Identifying and smoothing cellular neighborhoods
Usage:
```
python identify.py [-h] --ds_path DS_PATH --out_dir OUT_DIR --n_cns N_CNS [--cns_path CNS_PATH] [--Naive s [n_neighbors ...]]
                   [--HMRF eps beta [include_neighbors n_included max_iter max_iter_no_change ...]] [--seed SEED] [--verbose]
                   {CC,CFIDF,CNE} ...
```
Description of general arguments for idenfication and smoothing can be accessed by ```python identify.py -h```.
```
Identify and smooth CNs.

positional arguments:
  {CC,CFIDF,CNE}        identification method

required arguments:
  --ds_path DS_PATH     input dataset (.pkl) path
  --out_dir OUT_DIR     output directory
  --n_cns N_CNS         number of CNs

optional arguments:
  --cns_path CNS_PATH   only do smoothing using the cellular neighborhood file (.pkl) at the given path
  --Naive s [n_neighbors ...]
                        Naive smoothing technique
                        s: minimum size of a CN instance
                        n_neighbors: effective only when input cell representions (feats) are None, number of nearest neighbors considered for building CC cell representations (default: 10)
  --HMRF eps beta [include_neighbors n_included max_iter max_iter_no_change ...]
                        HMRF smoothing technique
                        eps: pixel radius of neighborhoods
                        beta: weight of each neighbor in the same CN
                        include_neighbors: whether to only include neighbors for each cell (default: False)
                        n_included: number of neighbors included for each cell (default: 100)
                        max_iter: the maximum number of iterations (default: 50)
                        max_iter_no_chanage: stop if the loss does not change for some iterations (default: 3)
  --seed SEED           seed for reproducibility
  --verbose             whether to print out metric values
```
Description of specific arguments for each idenfication method can be accessed by ```python identify.py <method> -h```. Using CNE as an example,
```
usage: identify.py CNE [-h] [--eta ETA] [--include_neighbors] [--n_included N_INCLUDED]

required arguments:
  --eta ETA             parameter to control Gaussian std

optional arguments:
  --include_neighbors   whether to only include neighbors for each cell
  --n_included N_INCLUDED
                        number of neighbors included for each cell (default: 100)
```

## Analyzing cellular neighborhoods
Jupyter notebooks to be uploaded soon.
