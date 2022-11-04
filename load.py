import argparse
import numpy as np
import pandas as pd
import json
from dataset import Dataset
import pickle
import os

COMMON_COLS = ['Group', 'Sample', 'Image', 'X', 'Y', 'CT']


def preprocess_CRC(df):
    df = df.rename(columns={'groups': 'Group', 'patients': 'Sample', 'File Name': 'Image', 'X:X': 'X', 'Y:Y': 'Y', 'ClusterName': 'CT'})
    df = df[df['CT'] != 'dirt']
    df['Group'] = df['Group'].apply(lambda r: ('CLR' if r == 1 else 'DII'))
    df['CT'] = df['CT'].apply(lambda r: r[0].upper() + r[1:])
    df = df[COMMON_COLS + ['CD4+ICOS+', 'CD4+Ki67+', 'CD4+PD-1+', 'CD8+ICOS+', 'CD8+Ki67+', 'CD8+PD-1+', 'Treg-ICOS+', 'Treg-Ki67+', 'Treg-PD-1+']]
    return df


def preprocess_T2D(df):
    df = df.sort_values(by=['Group', 'Donor', 'Islet', 'Cell'])
    df['X'], df['Y'] = (df['XMin'] + df['XMax']) / 2, (df['YMin'] + df['YMax']) / 2
    df = df.drop(['XMin', 'XMax', 'YMin', 'YMax', 'Helper T cell', 'Cytotoxic T cell', 'Inactive T cell', 'M1 mac', 'M2 mac', 'M1/M2 mac', 'Other mac', 'HLA-DR+ EC', 'CD34+ EC', 'HLA-DR+ CD34+ EC'], axis=1)
    ct2nct = {'α cell': 'Alpha cells', 'δ cell': 'Delta cells', 'β cell': 'Beta cells', 'γ cell': 'Gamma cells', 'ɛ cell': 'Epsilon cells', 'T cell': 'T cells', 'Macrophage': 'Macrophages', 'Other immune cell': 'Other immune cells', 'EC': 'Endothelial cells', 'Pericyte': 'Pericytes'}
    df = df.rename(columns=ct2nct).rename(columns={'Donor': 'Sample', 'Islet': 'Image'})
    def annotate(row):
        for ct in ct2nct.values():
            if row[ct] == 1:
                return ct
        return np.nan
    df['CT'] = df.apply(lambda r: annotate(r), axis=1)
    df = df.dropna(subset=['CT'])
    df = df[COMMON_COLS + ['Arg1 Positive Classification', 'Ki67 Positive Classification']]
    return df


def preprocess_HLT(df):
    # df1['isb'] = True
    # pickle.dump(image2cells, open('data/HLT_df.pkl', 'wb'))
    df = df.rename(columns={'sample': 'Image', 'x_in_file': 'X', 'y_in_file': 'Y', 'Cluster name': 'CT'})
    df = df[(df['Image'] != 'tonsil6677') & ((df['Image'] != 'tonsil8953') | ((df['X'] < 19200) & (df['Y'] > 4000)))]
    df = df[(df['CT'] != 'ECM near CD3+ cells') & (df['CT'] != 'ECM near CD45+ cells')]
    df[['CT']] = df[['CT']].replace({
        'Blood vessels near ECM': 'Blood vessels',
        'Epithelial cells near CD45+ cells': 'Epithelial cells',
        'Granulocytes near ECM': 'Granulocytes',
        'Macrophages near ECM': 'Macrophages',
        'Stromal cells near CD45+ cells': 'Stromal cells',
        'Activated T-Helper cells (CD278/CD4)': 'Activated T-helper cells (CD278/CD4)',
        'T Follicular Helper cells': 'T follicular helper cells',
        'T-Helper cells (CD4)': 'T-helper cells (CD4)',
        'T-Killer cells (CD8)': 'T-killer cells (CD8)'
    })
    df['Group'] = 0
    df['Sample'] = df['Image'].apply(lambda r: r if r == 'LN' or r == 'spleen' else 'tonsil')
    df = df[COMMON_COLS]
    return df


def load(df_path, df_name, out_dir, ct_order_path):
    df = pd.read_csv(df_path)
    if df_name == 'CRC':
        df = preprocess_CRC(df)
    elif df_name == 'T2D':
        df = preprocess_T2D(df)
    elif df_name == 'HLT':
        df = preprocess_HLT(df)
    ct_order = json.load(open(ct_order_path))['ct_order'] if ct_order_path else None
    ds = Dataset(df, df_name, ct_order)
    df.to_csv(os.path.join(out_dir, f'{df_name}_df.csv'), index=False)
    pickle.dump(ds, open(os.path.join(out_dir, f'{df_name}_ds.pkl'), 'wb'))


parser = argparse.ArgumentParser(description='Preprocess a cell table and make it a dictionary dataset.', formatter_class=argparse.RawTextHelpFormatter)
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

required.add_argument('--df_path', type=str, help='input table (.csv) path', required=True)
required.add_argument('--df_name', type=str, help='table name', required=True)
required.add_argument('--out_dir', type=str, help='output directory', required=True)
optional.add_argument('--ct_order_path', type=str, help='input CT order file (.json) path')

args = parser.parse_args()
load(**vars(args))
