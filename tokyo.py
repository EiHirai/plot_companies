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

# データセットの準備
tokyo_raw = pd.read_csv('./data/tokyo_full.csv')
tokyo_raw['count'] = 1

# 23区以外を落とす
tokyo = tokyo_raw.dropna(subset=['city'])
df_tokyo = tokyo.groupby(['city_id'], as_index=False).agg({'count': lambda x: sum(x)})

def calc_RGB_value(norm_count: float):
    '''0-1スケールに圧縮された数値をRGBの16進数表記として返す. 一番安い物件が水色, 高い物件がオレンジとなるようにする
    Args:
        norm_count (float): 0-1スケールに圧縮された数値
    Returns:
        str
        ex: #54b0c5
    '''
    R_val = 41 + (255 - 41) * norm_count
    G_val = 182 + (150 - 182) * norm_count
    B_val = 246 + (0 - 246) * norm_count
    return cl.to_hex((R_val / 255, G_val / 255, B_val / 255, 1))

def add_color_col(df):
    '''colorカラムを追加
    Args:
        df (pd.DataFrame): countカラムを含むデータフレーム
    Returns:
        pd.DataFrame
        'color'カラムを追加して返す
    '''
    norm = cl.Normalize(vmin=df['count'].min(), vmax=df['count'].max())
    norm_count_ = [norm(v) for v in df['count']]  # 企業数を0,1スケールにする
    color_ = [calc_RGB_value(norm_count) for norm_count in norm_count_]
    df['norm_count'] = norm_count_
    df['color'] = color_
    return df

df_tokyo = add_color_col(df_tokyo)

folium_map_tokyo = folium.Map(
    location=[35.731005,139.452995],
    zoom_start=9,
    tiles='cartodbpositron') # マップ作成

def add_to_m(i):
    m = folium.GeoJson(
        s3r.read_json_file('prd-data-store', 'location/geojson/city/_' + str(int(df_tokyo.city_id[i])) + '.json'),
        name='region_name',
        style_function = lambda x: {
                                'fillOpacity': df_tokyo.norm_count[i] * 2,
                                'fillColor': df_tokyo.color[i],
                                'color': 'white',
        })
    return m

for i in range(len(df_tokyo)):
    try:
        m = add_to_m(i)
        m.add_to(folium_map_tokyo)
        if i % 100 == 0:
            print('=== ' + str(i) + ': success ===')
    except:
        traceback.print_exc()

print('Completed')

folium_map_tokyo.save('./tokyo.html')
df_tokyo.to_csv('./df_tokyo.csv')