# CNTools

## Load a cell table.
```
usage: load.py [-h] --df_path DF_PATH --df_name DF_NAME --out_dir OUT_DIR [--ct_order_path CT_ORDER_PATH]

Preprocess a cell table and make it a dictionary dataset.

required arguments:
  --df_path DF_PATH     input table (.csv) path
  --df_name DF_NAME     table name
  --out_dir OUT_DIR     output directory

optional arguments:
  --ct_order_path CT_ORDER_PATH
                        input CT order file (.json) path
```
Usage: python load.py -h

## Identify and smooth cellular neighborhoods.
Usage: python identify.py -h

## Analyze cellular neighborhoods.
Usage: Jupyter notebooks will be uploaded soon.
