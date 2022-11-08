import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
from tqdm import tqdm


def CNE(ds, n_cns, eta, include_neighbors, n_included, seed):
    data = ds.data
    feats = []
    for sample in tqdm(data):
        for image in tqdm(data[sample], leave=False):
            locs = data[sample][image].locs
            if not include_neighbors:
                pdists = pairwise_distances(locs)
                min_neighbor_dists = (pdists + 1e12 * (pdists == 0)).min(axis=1, keepdims=True)
                pdists += (pdists == 0) * min_neighbor_dists
                prob = np.exp(-pdists ** 2 / ((eta * min_neighbor_dists) ** 2))
                feats.append(prob @ data[sample][image].cts_oh)
            else:
                pdists, indices = NearestNeighbors(n_neighbors=n_included).fit(locs).kneighbors(locs)
                min_neighbor_dists = (pdists + 1e12 * (pdists == 0)).min(axis=1, keepdims=True)
                pdists += (pdists == 0) * min_neighbor_dists
                prob = np.exp(-pdists ** 2 / ((eta * min_neighbor_dists) ** 2))
                feats.append((np.expand_dims(prob, axis=1) @ data[sample][image].cts_oh[indices]).squeeze(axis=1))
    feats = np.concatenate(feats)
    feats_normed = normalize(feats, norm='l1', axis=1) * np.log(ds.n_cells / (ds.ct_counts + 1))
    cns = ds.flat_to_dic(KMeans(n_clusters=n_cns, random_state=seed).fit_predict(feats_normed))
    return cns, feats_normed
