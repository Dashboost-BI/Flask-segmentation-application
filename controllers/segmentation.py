from python.config import app
import simplejson as json
from collections import Counter
from sklearn.tree import DecisionTreeRegressor
from sklearn.cluster import KMeans
from pandas.api.types import is_numeric_dtype
import numpy as np
import pandas as pd

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def order_cluster(cluster_field_name, target_field_name, df, ascending):
    new_cluster_field_name = 'new_' + cluster_field_name
    df_new = df.groupby(cluster_field_name)[
        target_field_name].mean().reset_index()
    df_new = df_new.sort_values(
        by=target_field_name, ascending=ascending).reset_index(drop=True)
    df_new['index'] = df_new.index
    df_final = pd.merge(
        df, df_new[[cluster_field_name, 'index']], on=cluster_field_name)
    df_final = df_final.drop([cluster_field_name], axis=1)
    df_final = df_final.rename(columns={"index": cluster_field_name})
    return df_final


def nicefy(n):
    n = round(n, 2)
    if ((n >= 1000) & (n < 1000000)):
        return str(round(n/1000, 3))+'K'
    elif ((n >= 1000000) & (n < 1000000000)):
        return str(round(n/1000000, 3))+'M'
    elif n >= 1000000000:
        return str(round(n/1000000000, 3))+'B'
    return str(n)


def segmentation(df, main, index):
    N_CLUSTERS = 4
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    features = [x for x in df.columns if ((x != index) and (x != main))]

    histogram = {}
    for column in features:
        if is_numeric_dtype(df[column]):
            hist = np.histogram(df[column], bins=10)
            hist_x = []
            for range_ in range(len(hist[1])-1):
                hist_x.append(nicefy(hist[1][range_]) +
                              '-' + nicefy(hist[1][range_]+1))
            y = hist[0]
        else:
            hist = dict(Counter(df[column].values.tolist()))
            hist_x = list(hist.keys())
            y = list(hist.values())
        histogram[column] = {
            'x': hist_x,
            'y': y
        }
    corr_heatmap = {
        'values': df.corr().values,
        'columns': df.corr().columns.tolist()
    }

    estimator = DecisionTreeRegressor().fit(
        df[features].values, df[main].values)
    feature_importance = {
        'importance': estimator.feature_importances_,
        'features': features
    }

    plots = {}
    scores = {}
    for feature in features:
        kmeans = KMeans(n_clusters=N_CLUSTERS)
        kmeans.fit(df[[main, feature]])
        df['cluster'] = kmeans.predict(df[[main, feature]])
        df[f'score of {feature}'] = df['cluster']
        df = order_cluster(f'score of {feature}', main, df, True)

        df[f'score of {feature}'] = df[f'score of {feature}'].values.astype(
            'str')

        plots[feature] = {}
        for score in df[f'score of {feature}'].unique():
            plots[feature][score] = df[df[f'score of {feature}'] == score][[main, feature]].values.tolist() 
        score = dict(Counter(df[f'score of {feature}'].values.tolist()))
        score_x = list(score.keys())
        score_y = list(score.values())
        scores[feature] = {'x': score_x, 'y': score_y}
        df[f'score of {feature}'] = df[f'score of {feature}'].values.astype(
            'int')

    df = df.drop('cluster', axis=1)
    plots = json.dumps(plots)
    results = {
        'scores': scores,
        'histogram': histogram,
        'corr_heatmap': corr_heatmap,
        'feature_importance': feature_importance,
    }
    results = json.dumps(results, cls=NpEncoder)
    results = {
        'results': results,
        'plots': plots,
        'features': features,
        'df': df.to_html(classes='table table-striped dataex-html5-selectors')
    }
    return results