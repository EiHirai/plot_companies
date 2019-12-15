import pandas as pd
pd.options.display.max_columns=None
pd.set_option("display.max_colwidth", 1000) #カラム内文字列1000文字まで表示
import numpy as np
import folium
import json
import re
import os
import math
import traceback
import matplotlib.colors as cl
from RW_S3 import *

s3r = S3Reader()

shibuya_1 = pd.read_csv('./data/shibuya_1_addlatlon.csv')
shibuya_2 = pd.read_csv('./data/shibuya_2_addlatlon.csv')
shibuya = pd.concat([shibuya_1, shibuya_2])

shibuya['latlon'] = ['{:.3f} {:.3f}'.format(lat, lon) for lat, lon in zip(shibuya.latitude, shibuya.longitude)]

shibuya['count'] = 1
df_shibuya = shibuya.groupby(['latlon'], as_index=False).agg({'count': lambda x: sum(x)})

df_shibuya['latitude'] = df_shibuya['latlon'].apply(lambda x: x.split(' ')[0])
df_shibuya['longitude'] = df_shibuya['latlon'].apply(lambda x: x.split(' ')[1])
df_shibuya['count_log'] = df_shibuya['count'].apply(lambda x: math.log(x))

def calc_RGB_value(norm_count: float):
    '''0-1スケールに圧縮された数値をRGBの16進数表記として返す. 一番安い物件が水色, 高い物件がオレンジとなるようにする
    Args:
        norm_count (float): 0-1スケールに圧縮された数値
    Returns:
        str
        ex: #54b0c5
    '''
    R_val = 230 + (255 - 230) * norm_count
    G_val = 242 + (150 - 242) * norm_count
    B_val = 255 + (0 - 255) * norm_count
    return cl.to_hex((R_val / 255, G_val / 255, B_val / 255, 1))

def add_color_col_log(df):
    '''colorカラムを追加
    Args:
        df (pd.DataFrame): countカラムを含むデータフレーム
    Returns:
        pd.DataFrame
        'color'カラムを追加して返す
    '''
    norm = cl.Normalize(vmin=df['count_log'].min(), vmax=df['count_log'].max())
    norm_count_ = [norm(v) for v in df['count_log']]  # 企業数を0,1スケールにする
    color_ = [calc_RGB_value(norm_count) for norm_count in norm_count_]
    df['color'] = color_
    return df

df_shibuya = add_color_col_log(df_shibuya)

folium_map_shibuya = folium.Map(
    location=[35.731005,139.452995],
    zoom_start=9,
    tiles='cartodbdark_matter') # マップ作成

def plot_to_m(i):
    m = folium.CircleMarker(location=(df_shibuya.latitude[i], df_shibuya.longitude[i]),
                            radius=5,
                            color=df_shibuya.color[i],
                            fill=True
                            )
    return m

for i in range(len(df_shibuya)):
    try:
        m = plot_to_m(i)
        m.add_to(folium_map_shibuya)
        if i % 100 == 0:
            print('=== ' + str(i) + ': success ===')
    except:
        traceback.print_exc()

print('Completed')

folium_map_shibuya.save('./shibuya_3.html')
df_shibuya.to_csv('./data/df_shibuya_3.csv')