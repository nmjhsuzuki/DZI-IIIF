# coding: utf-8

# ======================================================================
# DZI-IIIF
# DeepZoom(dzi)形式のファイルをIIIF Image APIでアクセスできるようにする
# ======================================================================
# 2020-05-21 Ver.0.1 
# ======================================================================
# dzi-iiif.cgi: エントリーポイント
# ======================================================================

# --- 利用者環境に応じて設定する情報 ここから

import os
if (os.name == 'nt'): # Windows
    path = os.path.join('C:'+os.sep, 'DZI-IIIF')
    spath = os.path.join(path, 'scripts') # pythonスクリプトディレクトリへのパス
    dpath = os.path.join(path, 'images') # データディレクトリへのパス
    lpath = os.path.join(path, 'logs') # ログディレクトリへのパス
else: # Mac or Linux
    spath = os.path.join(os.sep, 'usr', 'local' 'DZI-IIIF', 'scripts') # pythonスクリプトディレクトリへのパス
    dpath = os.path.join(os.sep, 'var', 'DZI-IIIF', 'images') # データディレクトリへのパス
    lpath = os.path.join(os.sep, 'var', 'log', 'DZI-IIIF') # ログディレクトリへのパス
#fi

# デバッグモードを設定
#dbg = False
dbg = True

# --- ここまで

# pythonスクリプトディレクトリをシステムパスに追加
import sys
sys.path.append(spath)

# グローバル変数の輸入
import dziiiif_common as glo

# パス情報をグローバル変数に登録
glo.scripts_path = spath
glo.data_path = dpath
glo.logs_path = lpath

# デバッグモードを設定
glo.debug = dbg

# メインモジュールを実行
import dziiiif_main

# おわり
