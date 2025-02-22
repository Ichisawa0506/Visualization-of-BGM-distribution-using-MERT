# -*- coding: utf-8 -*-
"""model5 UMAP.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fsanxM-wxFp4TXEfDGhLGT37LuEFxxF1
"""

#import matplotlib.pyplot as plt
#import matplotlib.colors as mcolors

#colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

# 色名と色見本を表示
#for name, color in colors.items():
#    print(name, color)

#from google.colab import drive
#drive.mount('/content/drive')

!pip install umap-learn==0.5.3

import umap
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# データの読み込み
data = pd.read_csv('/content/features_MERT-v1-95M_Genre.csv')

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
    'wahu': 'grey',
    'chill hop': 'silver',
    'ambient': 'olive',
    'acoustic': 'violet',
    'wahu': 'black',
    'piano': 'brown'
}

# 各層ごとに可視化 & PDF出力
pdf_pages = PdfPages('umap_output.pdf')  # PDFファイルを作成

for i in range(num_layers):
    # 層iの特徴量を選択
    X = data[layer_features[i]].dropna().reset_index(drop=True)
    data_layer = data.loc[X.index].reset_index(drop=True)

    # UMAPによる次元削減
    #reducer = umap.UMAP(random_state=42)  # random_stateを指定して結果を再現可能にする
    reducer = umap.UMAP(min_dist=0.05,
                        n_neighbors = 30,
                        n_components = 2,
                        random_state=42)
    X_reduced = reducer.fit_transform(X)

    # 可視化
    plt.figure(figsize=(20, 20))
    for genre in genres:
        genre_data = X_reduced[data_layer.index[data_layer['genre2'] == genre]]
        plt.scatter(genre_data[:, 0], genre_data[:, 1], c=genre_color_map.get(genre), label=genre)

        # 楽曲名を表示 (genre_dataの最初の5点に表示)
        #for j in range(min(100, len(genre_data))):  # 最大5点まで表示
         #   trackname = data_layer.loc[data_layer.index[data_layer['genre2'] == genre][j], 'trackname']  # 楽曲名を取得
          #  plt.text(genre_data[j, 0], genre_data[j, 1], trackname, fontsize=2)  # 楽曲名を表示

    plt.xlabel('UMAP Dimension 1')
    plt.ylabel('UMAP Dimension 2')
    plt.title(f'UMAP Visualization of Layer {i} Colored by Genre')
    plt.legend()

    plt.show()  # 表示する
    #pdf_pages.savefig()  # 現在の図をPDFに追加
    #plt.close()  # 図を閉じる

pdf_pages.close()  # PDFファイルを閉じる

import numpy as np

genre_sse_by_layer = {}  # ジャンルとlayer毎のSSEを格納する辞書
genre_total_sse = {}  # ジャンル毎のtotal SSEを格納する辞書
layer_total_sse = {} # layer毎のtotal SSEを格納する辞書


for i in range(num_layers):  # layerごとのループを追加
    # --- ここからlayer i のデータを取得する処理 ---
    X = data[layer_features[i]].dropna().reset_index(drop=True)
    data_layer = data.loc[X.index].reset_index(drop=True)

    # UMAPによる次元削減
    reducer = umap.UMAP(min_dist=0.05,
                        n_neighbors = 30,
                        n_components = 2,
                        random_state=42)
    X_reduced = reducer.fit_transform(X)
    # --- ここまでlayer i のデータを取得する処理 ---

    genre_sse_by_layer[i] = {}  # layer i のSSEを格納する辞書を初期化
    layer_total_sse[i] = 0  # layer i のtotal SSEを初期化

    for genre in genres:
        genre_data = X_reduced[data_layer.index[data_layer['genre2'] == genre]]
        genre_centroid = np.mean(genre_data, axis=0)

        sse = 0
        for data_point in genre_data:
            sse += np.sum((data_point - genre_centroid)**2)

        genre_sse_by_layer[i][genre] = sse  # layer i, genre のSSEを格納

        # total SSEを計算
        genre_total_sse[genre] = genre_total_sse.get(genre, 0) + sse
        layer_total_sse[i] += sse # layer i のtotal SSEを加算

# ジャンルとlayer毎のSSEを表示
for i in range(num_layers):
    print(f"Layer {i}:")
    for genre, sse in genre_sse_by_layer[i].items():
        print(f"  ジャンル: {genre}, SSE: {sse}")

# layer毎のtotal SSEを表示
print("\nlayer毎のtotal SSE:")
for i in range(num_layers):
    print(f"  Layer {i}: Total SSE: {layer_total_sse[i]}")

# ジャンル毎のtotal SSEを表示
print("\nジャンル毎のtotal SSE:")
for genre, total_sse in genre_total_sse.items():
    print(f"  ジャンル: {genre}, Total SSE: {total_sse}")

# 全体のSSEを計算する
total_sse_all_layers = sum(layer_total_sse.values())

# 全体のSSEを計算する
total_sse = sum(layer_total_sse.values())

# 各クラスタのSSEを正規化する
normalized_sse = {}
for i in range(num_layers):
    normalized_sse[i] = {}
    for genre, sse in genre_sse_by_layer[i].items():
        normalized_sse[i][genre] = sse / total_sse

# 正規化されたSSEを表示する
for i in range(num_layers):
    print(f"Layer {i}:")
    for genre, sse in normalized_sse[i].items():
        print(f"  ジャンル: {genre}, 正規化SSE: {sse}")

# 正規化されたジャンル毎のtotal SSEを計算・表示
normalized_genre_total_sse = {}
for genre, total_sse in genre_total_sse.items():
    normalized_genre_total_sse[genre] = total_sse / total_sse_all_layers
    print(f"ジャンル: {genre}, 正規化Total SSE: {normalized_genre_total_sse[genre]}")

print(f"\n全layerのTotal SSE: {total_sse_all_layers}") # 全体のSSEも表示 (変更なし)

# Calculate normalized SSE for each layer
layer_normalized_sse = {}
for i in range(num_layers):
    layer_normalized_sse[i] = sum(normalized_sse[i].values())

# Print normalized SSE for each layer
for i in range(num_layers):
    print(f"Layer {i}: 正規化SSE: {layer_normalized_sse[i]}")

import umap
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D  # Import for 3D plotting


# ... (rest of the code remains the same up to UMAP initialization)

# UMAPによる次元削減 (3 dimensions)
reducer = umap.UMAP(min_dist=0.05,
                    n_neighbors=30,
                    n_components=3,  # Change to 3 for 3D
                    random_state=42)
X_reduced = reducer.fit_transform(X)

# 可視化 (3D)
fig = plt.figure(figsize=(20, 20))
ax = fig.add_subplot(111, projection='3d')  # Create a 3D subplot

for genre in genres:
    genre_data = X_reduced[data_layer.index[data_layer['genre2'] == genre]]
    ax.scatter(genre_data[:, 0], genre_data[:, 1], genre_data[:, 2],
               c=genre_color_map.get(genre), label=genre)

    # 楽曲名を表示 (genre_dataの最初の5点に表示)
    for j in range(min(100, len(genre_data))):  # 最大5点まで表示
        trackname = data_layer.loc[data_layer.index[data_layer['genre2'] == genre][j], 'trackname']  # 楽曲名を取得
        ax.text(genre_data[j, 0], genre_data[j, 1], genre_data[j, 2], trackname, fontsize=2)  # 楽曲名を表示 (3D)

ax.set_xlabel('UMAP Dimension 1')
ax.set_ylabel('UMAP Dimension 2')
ax.set_zlabel('UMAP Dimension 3')  # Add z-axis label
ax.set_title(f'UMAP Visualization of Layer {i} Colored by Genre (3D)')
ax.legend()

pdf_pages.savefig()  # 現在の図をPDFに追加
plt.close()  # 図を閉じる

# ... (rest of the code remains the same)

import umap
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Import for 3D plotting

# ... (rest of your code, including data loading, feature selection, etc.)

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
    'wahu': 'grey',
    'chill hop': 'silver',
    'ambient': 'olive',
    'acoustic': 'violet',
    'wahu': 'black',
    'piano': 'brown'
}

# UMAPによる次元削減 (3 dimensions)
reducer = umap.UMAP(min_dist=0.05,
                    n_neighbors=60,
                    n_components=3,  # Change to 3 for 3D
                    random_state=42)
X_reduced = reducer.fit_transform(X)

for i in range(num_layers):
    # ... (code for data preparation and UMAP dimensionality reduction)

    # 可視化 (3D)
    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(111, projection='3d')  # Create a 3D subplot

    for genre in genres:
        genre_data = X_reduced[data_layer.index[data_layer['genre2'] == genre]]
        ax.scatter(genre_data[:, 0], genre_data[:, 1], genre_data[:, 2],
                   c=genre_color_map.get(genre), label=genre)

        # 楽曲名を表示 (genre_dataの最初の5点に表示)
        for j in range(min(100, len(genre_data))):  # 最大5点まで表示
            trackname = data_layer.loc[data_layer.index[data_layer['genre2'] == genre][j], 'trackname']  # 楽曲名を取得
            ax.text(genre_data[j, 0], genre_data[j, 1], genre_data[j, 2], trackname, fontsize=2)  # 楽曲名を表示 (3D)

    ax.set_xlabel('UMAP Dimension 1')
    ax.set_ylabel('UMAP Dimension 2')
    ax.set_zlabel('UMAP Dimension 3')  # Add z-axis label
    ax.set_title(f'UMAP Visualization of Layer {i} Colored by Genre (3D)')
    ax.legend()

    plt.show()  # Display the plot directly

    # ... (rest of your code)

import umap
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D  # Import for 3D plotting

# ... (rest of your code, including data loading, feature selection, etc.)
# データの読み込み
data = pd.read_csv('/content/features_MERT-v1-95M_Genre_no_pop.csv')

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
    'wahu': 'grey',
    'chill hop': 'silver',
    'ambient': 'olive',
    'acoustic': 'violet',
    'wahu': 'black',
    'piano': 'brown'
}

# UMAPによる次元削減 (3 dimensions)
reducer = umap.UMAP(min_dist=0.05,
                    n_neighbors=80,
                    n_components=3,  # Change to 3 for 3D
                    random_state=42)
X_reduced = reducer.fit_transform(X)

# PDFファイルを作成
pdf_pages = PdfPages('umap_output_3d_no_pop.pdf')

for i in range(num_layers):
    # ... (code for data preparation and UMAP dimensionality reduction with n_components=3)

    # 可視化 (3D)
    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(111, projection='3d')  # Create a 3D subplot

    for genre in genres:
        genre_data = X_reduced[data_layer.index[data_layer['genre2'] == genre]]
        ax.scatter(genre_data[:, 0], genre_data[:, 1], genre_data[:, 2],
                   c=genre_color_map.get(genre), label=genre)

        # 楽曲名を表示 (genre_dataの最初の5点に表示)
        for j in range(min(100, len(genre_data))):  # 最大5点まで表示
            trackname = data_layer.loc[data_layer.index[data_layer['genre2'] == genre][j], 'trackname']  # 楽曲名を取得
            ax.text(genre_data[j, 0], genre_data[j, 1], genre_data[j, 2], trackname, fontsize=2)  # 楽曲名を表示 (3D)

    ax.set_xlabel('UMAP Dimension 1')
    ax.set_ylabel('UMAP Dimension 2')
    ax.set_zlabel('UMAP Dimension 3')  # Add z-axis label
    ax.set_title(f'UMAP Visualization of Layer {i} Colored by Genre (3D)')
    ax.legend()

    pdf_pages.savefig()  # 現在の図をPDFに追加
    plt.close()  # 図を閉じる

# PDFファイルを閉じる
pdf_pages.close()