import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import MiniBatchKMeans
from tqdm import tqdm


def CC(ds, n_cns, m, seed):
    data = ds.data
    feats = []
    for sample in tqdm(data):
        for image in tqdm(data[sample], leave=False):
            locs = data[sample][image].locs
            n_neighbors_real = m if data[sample][image].n_cells >= m else data[sample][image].n_cells
            _, indices = NearestNeighbors(n_neighbors=n_neighbors_real).fit(locs).kneighbors(locs)
            for nbs in indices:
                feats.append(data[sample][image].cts_oh[nbs].mean(axis=0))
    feats = np.array(feats)
    cns = ds.flat_to_dic(MiniBatchKMeans(n_clusters=n_cns, random_state=seed).fit_predict(feats))
    return cns, feats
