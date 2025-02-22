# -*- coding: utf-8 -*-
"""model5_3_not_change.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14ll0YWCJqnxBKcjVrmKaPa7H06jPtHJT
"""

#import matplotlib.pyplot as plt
#import matplotlib.colors as mcolors

#colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

# 色名と色見本を表示
#for name, color in colors.items():
#    print(name, color)

import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf

#from google.colab import drive
#drive.mount('/content/drive')

# データの読み込み
data = pd.read_csv('/content/features_MERT-v1-95M_MargeGenre.csv')

from enum import auto
# 層の数
num_layers = 13

layer_features = []
for i in range(num_layers):
    layer_features.append([f"{i}_feature{j}" for j in range(1, 767)])

genres = data['genre2'].unique()

# genreごとに色を割り当てる
genre_color_map = {
    'R&B Jazz': 'red',
    'pop': 'blue',
    'classic': 'green',
    'EDM': 'purple',
    'electro': 'orange',
    'rock': 'yellow',
    'chill hop' : 'silver',
    'ambient' : 'olive',
    'acoustic' : 'violet',
    'wahu' : 'black',
    'piano': 'brown'
}

pdf = matplotlib.backends.backend_pdf.PdfPages("output.pdf")

# 各層ごとに可視化
for i in range(num_layers):
    # 層iの特徴量を選択
    X = data[layer_features[i]].dropna().reset_index(drop=True)
    data_layer = data.loc[X.index].reset_index(drop=True)

    # t-SNEによる次元削減
    tsne = TSNE(n_components=2,
                perplexity=250,
                early_exaggeration=5,
                #learning_rate=100,
                n_iter=500,
                metric='cosine',
                random_state=42)
    X_reduced_tsne = tsne.fit_transform(X)


    # PCAによる次元削減
    pca = PCA(n_components=2)
    X_reduced_pca = pca.fit_transform(X)

    # t-SNEによる可視化
    plt.figure(figsize=(20, 20))
    for genre in genres:
        genre_data = X_reduced_tsne[data_layer.index[data_layer['genre2'] == genre]]
        plt.scatter(genre_data[:, 0], genre_data[:, 1], c=genre_color_map.get(genre), label=genre)

        # ジャンルを表示 (genre_dataの最初の100点に表示)
        for j in range(min(100, len(genre_data))):
            genre_name = genre # ジャンルを取得
            plt.text(genre_data[j, 0], genre_data[j, 1], genre_name, fontsize=3)  # ジャンルを表示

        # 楽曲名を表示 (genre_dataの最初の100点に表示)
        #for j in range(min(100, len(genre_data))):
        #    trackname = data_layer.loc[data_layer.index[data_layer['genre2'] == genre][j], 'trackname']  # 楽曲名を取得
        #    plt.text(genre_data[j, 0], genre_data[j, 1], trackname, fontsize=3)  # 楽曲名を表示

    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.title(f't-SNE Visualization of Layer {i} Colored by Genre')
    plt.legend()
    # plt.show()  # PDFに保存するので、show() は不要
    pdf.savefig()  # PDFに保存
    plt.close() # メモリリークを防ぐために図を閉じる


    # PCAによる可視化
    plt.figure(figsize=(20, 20))
    for genre in genres:
        genre_data = X_reduced_pca[data_layer.index[data_layer['genre2'] == genre]]
        plt.scatter(genre_data[:, 0], genre_data[:, 1], c=genre_color_map.get(genre, 'gray'), label=genre)

        # ジャンルを表示 (genre_dataの最初の100点に表示)
        for j in range(min(100, len(genre_data))):
            genre_name = genre # ジャンルを取得
            plt.text(genre_data[j, 0], genre_data[j, 1], genre_name, fontsize=3)  # ジャンルを表示

        # 楽曲名を表示 (genre_dataの最初の100点に表示)
        #for j in range(min(200, len(genre_data))):
        #    trackname = data_layer.loc[data_layer.index[data_layer['genre2'] == genre][j], 'trackname']  # 楽曲名を取得
        #    plt.text(genre_data[j, 0], genre_data[j, 1], trackname, fontsize=3)  # 楽曲名を表示

    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title(f'PCA Visualization of Layer {i} Colored by Genre')
    plt.legend()
    # plt.show()  # PDFに保存するので、show() は不要
    pdf.savefig()  # PDFに保存
    plt.close() # メモリリークを防ぐために図を閉じる


pdf.close()  # PDFファイルを閉じる

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# 全レイヤーのSSEを格納する辞書（PCAとt-SNEを区別）
layer_sse_pca = {}
layer_sse_tsne = {}

# 各層ごとに処理
for i in range(num_layers):
    # 層iの特徴量を選択
    X = data[layer_features[i]].dropna().reset_index(drop=True)
    data_layer = data.loc[X.index].reset_index(drop=True)

    # ジャンルごとにデータを分割
    genre_data = {}
    for genre in genres:
        genre_data[genre] = data_layer[data_layer['genre2'] == genre][layer_features[i]].dropna().reset_index(drop=True)

    # t-SNEによる次元削減
    tsne = TSNE(n_components=2,
                perplexity=250,
                early_exaggeration=5,
                #learning_rate=100,
                n_iter=500,
                metric='cosine',
                random_state=42)
    X_reduced_tsne = tsne.fit_transform(X)

    # PCAによる次元削減
    pca = PCA(n_components=2)
    X_reduced_pca = pca.fit_transform(X)

    # PCAとt-SNEそれぞれでSSEを計算
    genre_sse_pca = {}
    genre_sse_tsne = {}
    for genre, data_genre in genre_data.items():
        # ジャンルごとのデータ数がクラスタ数より少ない場合はスキップ
        if len(data_genre) < 10:
            print(f"Skipping genre {genre} in layer {i} for PCA and t-SNE due to insufficient data points.")
            continue

        # PCA
        kmeans_pca = KMeans(n_clusters=10, random_state=42)
        kmeans_pca.fit(X_reduced_pca[data_layer.index[data_layer['genre2'] == genre]])  # PCAで次元削減したデータを使用
        genre_sse_pca[genre] = kmeans_pca.inertia_

        # t-SNE
        kmeans_tsne = KMeans(n_clusters=10, random_state=42)
        kmeans_tsne.fit(X_reduced_tsne[data_layer.index[data_layer['genre2'] == genre]])  # t-SNEで次元削減したデータを使用
        genre_sse_tsne[genre] = kmeans_tsne.inertia_

    # 各ジャンルのSSEの総和を計算（PCAとt-SNEそれぞれ）
    total_sse_pca = sum(genre_sse_pca.values())
    total_sse_tsne = sum(genre_sse_tsne.values())

    # レイヤーiのSSEを辞書に格納（PCAとt-SNEそれぞれ）
    layer_sse_pca[i] = total_sse_pca
    layer_sse_tsne[i] = total_sse_tsne

    # 各ジャンルのSSEと総和を表示（PCAとt-SNEそれぞれ）
    print(f"Layer {i}:")
    print("  PCA:")
    for genre, sse in genre_sse_pca.items():
        print(f"    Genre: {genre}, SSE: {sse}")
    print(f"    Total SSE: {total_sse_pca}")
    print("  t-SNE:")
    for genre, sse in genre_sse_tsne.items():
        print(f"    Genre: {genre}, SSE: {sse}")
    print(f"    Total SSE: {total_sse_tsne}\n")

# 各レイヤーのSSEを表示（PCAとt-SNEそれぞれ）
print("SSE for each layer:")
print("PCA:")
for layer, sse in layer_sse_pca.items():
    print(f"Layer {layer}: {sse}")
print("\nt-SNE:")
for layer, sse in layer_sse_tsne.items():
    print(f"Layer {layer}: {sse}")