import argparse
from os.path import exists, join
import pandas as pd

# Input args parser
parser = argparse.ArgumentParser(description='Script for taking stock of the data. Inside there directories which should be looked into are listed.')
parser.add_argument('-o', '--out', help='Output file. Defaults to data_stock.csv.', default='data_stock.csv')
parser.add_argument('-i', '--ids', help='Input ID list file (default is valid_subjects.csv).', default='valid_subjects.csv')
parser.add_argument('-r', '--returns', help='Return all IDs or just those with something missing; default: all', default='all', choices=['all', 'missing', 'with_everything'])
parser = parser.parse_args()

# Paths to check
paths = {
    'raw': '/mnt/nasips/COST_mri/rawdata/',
    'hmri':'/mnt/nasips/COST_mri/derivatives/hmri/',
    'freesurfer': '/mnt/nasips/COST_mri/derivatives/freesurfer/',
    'dwi': '/mnt/nasips/COST_mri/derivatives/dwi/'
}

# Load the Ids for which we need to do the check
df = pd.read_csv(parser.ids)
ids = df.ID.values
print(f'{len(ids)} valid subjects loaded from {parser.ids}')

# Iterate all Ids
for d in paths.keys():
    # Add the directory name to the df columns
    df[d] = None
    for i, sub in enumerate(ids):
        if 'sub-' not in str(sub):
            sub = 'sub-'+str(sub)
        # Fully qualified path
        fqp = join(paths[d], str(sub))
        # directory should be there with a fqp
        df.loc[i, d] = exists(fqp)

if parser.returns == 'all':
    df.to_csv(parser.out, index=False)

elif parser.returns == 'missing':
    df = df[df[['hmri', 'dwi', 'freesurfer']] != True].reset_index(drop=True)
    df.to_csv(join(parser.out.split('.csv')[0]+'_missing.csv'), index=False)

elif parser.returns == 'with_everything':
    df = df[df[['hmri', 'dwi', 'freesurfer']] == True].reset_index(drop=True)
    df.to_csv(join(parser.out.split('.csv')[0]+'_with_everything.csv'), index=False)

else:
    print('What have you done???')
    exit()