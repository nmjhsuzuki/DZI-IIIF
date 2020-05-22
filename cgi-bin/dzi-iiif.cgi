#!/usr/local/bin/python3

# coding: utf-8

# ======================================================================
# DZI-IIIF
# DeepZoom(dzi)形式のファイルをIIIF Image APIでアクセスできるようにする
# ======================================================================
# 2020-05-21 Ver.0.1: Initial Version, No info.json handling.
# 2020-05-22 Ver.0.2: Add info.json handling.
# ======================================================================
# dzi-iiif.cgi: エントリーポイント
# ======================================================================

# --- 利用者環境に応じて設定する情報 ここから ---

# 画像情報リクエストで返す基底URI
uri = 'http://localhost/cgi-bin/dzi-iiif.cgi?IIIF='

# 各種ディレクトリの設定
import os
if (os.name == 'nt'): # Windows
    lpath = os.path.join('C:'+os.sep, 'DZI-IIIF')
    spath = os.path.join(lpath, 'scripts') # pythonスクリプトディレクトリへのパス
    dpath = os.path.join(lpath, 'images') # データディレクトリへのパス
    lpath = os.path.join(lpath, 'logs') # ログディレクトリへのパス
else: # Mac or Linux
# マシン単位のインストールサンプル
#    spath = os.path.join(os.sep, 'usr', 'local' 'DZI-IIIF', 'scripts') # pythonスクリプトディレクトリへのパス
#    dpath = os.path.join(os.sep, 'var', 'DZI-IIIF', 'images') # データディレクトリへのパス
#    lpath = os.path.join(os.sep, 'var', 'log', 'DZI-IIIF') # ログディレクトリへのパス
# 個人アカウント単位のインストールサンプル
    lpath = os.path.join('~user', 'DZI-IIIF')
    spath = os.path.join(lpath, 'scripts') # pythonスクリプトディレクトリへのパス
    dpath = os.path.join(lpath, 'images') # データディレクトリへのパス
    lpath = os.path.join(lpath, 'logs') # ログディレクトリへのパス
#fi

# 作成する画像の一辺のピクセル値の上限
whmax = 2000

# デバッグモードを設定
#dbg = False
dbg = True

# --- 利用者環境に応じて設定する情報 ここまで ---

# pythonスクリプトディレクトリをシステムパスに追加
import sys
sys.path.append(spath)

# グローバル変数の輸入
import dziiiif_common as glo

# 基底URIをグローバル変数に登録
glo.id_uri = uri

# パス情報をグローバル変数に登録
glo.scripts_path = spath
glo.data_path = dpath
glo.logs_path = lpath

# 作成する画像の一辺のピクセル値の上限
glo.wh_max = whmax

     # デバッグモードを設定
glo.debug = dbg

# メインモジュールを実行
import dziiiif_main

# おわり
