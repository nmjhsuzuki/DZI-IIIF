#!/usr/local/bin/python3

# coding: utf-8

# ======================================================================
# DZI-IIIF
# DeepZoom(dzi)形式のファイルをIIIF Image APIでアクセスできるようにする
# ======================================================================
# 2020-05-21 Ver.0.1: Initial Version, No info.json handling.
# 2020-05-22 Ver.0.2: Add info.json handling.
# ======================================================================
# dziiiif_common.py: グローバル変数の定義
# ======================================================================
from enum import Enum # 列挙型を使う

# -------------
# システム定数
# -------------

# 画像情報リクエストで返す基底URI
id_uri = ''

# pythonスクリプトディレクトリへのパス
scripts_path = ''
# データディレクトリへのパス
data_path = ''
# ログディレクトリへのパス
logs_path = ''

# 作成する画像の一辺のピクセル値の上限
wh_max = 4000 

# -----------
# ステータス
# -----------

# デバッグモードONOFF
debug = False

# 処理のステータス
# 200: 正常
# 400: 不正アクセス
# 404: 画像ファイルがない or リクエストサイズが限界以上
class status_code(Enum) :
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
status_str = {
    status_code.OK: "OK", 
    status_code.BAD_REQUEST: "Bad Request", 
    status_code.NOT_FOUND: "Not Found",
    status_code.INTERNAL_SERVER_ERROR: "Internal Server Error"
    }
status = status_code.OK

# どこでステータスが変わったか
status_change_at = ''

# 画像の代わりに処理の情報を表示する（デバッグモードのみ）
report_flag = False

# -----------------
# IIIF パラメタ関係
# -----------------

# 入力文字列
iiif = ''

# 画像の識別子 = DZI画像格納フォルダへのパス
identifier = ''

# 画像リクエストか画像情報リクエストか
class query_mode(Enum) :
    IMAGE = 1
    INFO = 2
#ssalc
query = query_mode.IMAGE

# 取得する領域
class region_mode(Enum) :
    full = 1
    square = 2
    pixel = 3
    percent = 4
region = region_mode.full
region_x = 0 # 左: pixel or percent で使用
region_y = 0 # 上: pixel or percent で使用
region_w = 0 # 幅: pixel or percent で使用
region_h = 0 # 高: pixel or percent で使用

# 取得する大きさ
class size_mode(Enum) :
    full = 1
    max = 2
    w_align = 3
    h_align = 4
    percent = 5
    wh = 6
    wh_align = 7
size = size_mode.full
size_w = 0
size_h = 0
size_percent = 0

# 回転角度
# 当面は0のみ許可
rotate = '0' # 0-360
#rotate_lr_invert = False # 左右反転フラグ

# 画像の品質 
# 当面は'default'のみ許可
#class quality_mode(Enum) :
#    color = 1
#    gray = 2
#    bitonal = 3
#    default = 4
#quality = quality_mode.default
quality = 'default'

# 画像の書式
# 当面は'jpg'のみ許可
class format_code(Enum) :
    JPG = 1
    TIF = 2
    PNG = 3
    GIF = 4
    JP2 = 5
    PDF = 6
    WEBP = 7
format_strtocode = {
    'jpg': format_code.JPG,
    'tif': format_code.TIF,
    'png': format_code.PNG,
    'gif': format_code.GIF,
    'jp2': format_code.JP2,
    'pdf': format_code.PDF,
    'webp': format_code.WEBP
    }
format_str = {
    format_code.JPG: 'jpg',
    format_code.TIF: 'tif',
    format_code.PNG: 'png',
    format_code.GIF: 'gif',
    format_code.JP2: 'jp2',
    format_code.PDF: 'pdf',
    format_code.WEBP: 'webp'
    }
format_PILstr = {
    format_code.JPG: 'JPEG',
    format_code.TIF: 'TIFF',
    format_code.PNG: 'PNG',
    format_code.GIF: 'GIF',
    format_code.JP2: 'JPEG 2000',
    format_code.PDF: None,
    format_code.WEBP: 'WebP'
    }
format_mimetype = {
    format_code.JPG: 'image/jpeg',
    format_code.TIF: 'image/tiff',
    format_code.PNG: 'image/png',
    format_code.GIF: 'image/gif',
    format_code.JP2: 'image/jp2',
    format_code.PDF: 'application/pdf',
    format_code.WEBP: 'image/webp'
    }
format = format_code.JPG

# -----------------
# DZIファイル関係
# -----------------

# XML namespace
xmlns = ''

# タイルサイズ
dzi_tilesize = 512

# オーバーラップサイズ
dzi_overlap = 1

# フォーマット
dzi_format = 'jpg'

# 画像幅
dzi_w = 0

# 画像高さ
dzi_h = 0

# 分割画像最高レベル
dzi_maxlevel = 0

# -----------------
# 画像の切り出し
# -----------------

# 領域
dzi_region_x = 0
dzi_region_y = 0
dzi_region_w = 0
dzi_region_h = 0

# サイズ
outimage_w = 0
outimage_h = 0

# 生成画像
outimage = None

# 出力画像のクオリティ
outimage_quality = 80

# 出力ファイル
outstream = None

# 出力ファイルのサイズ
outstream_size = 0

# for debug
inimage_path =''


# -----
# 関数
# -----

# 文字列から整数値の読み取り（読めない時はdefault = -1を返す)
def readint(s, default=-1):
    try:
        return int(s)
    except ValueError:
        return default

# 文字列から小数値の読み取り（読めない時はdefault = -1を返す)
def readfloat(s, default=-1):
    try:
        return float(s)
    except ValueError:
        return default

# ステータスが最初に変わった場所を記録
def change_status_at(sc, at):
    global status, status_change_at
    if (status == status_code.OK):
        status = sc
        status_change_at = at
    #fi
#fed

# 領域の文字列化
def regiontostr(x, y, w, h):
    return str(x)+', '+str(y)+', '+str(w)+', '+str(h)

# サイズの文字列化
def sizetostr(w, h):
    return str(w)+', '+str(h)

# グローバル変数の表示
def gloprint(lf='') : # 改行記号 lf を付与できる
#    global path, wh_max
#    global debug, status, status_change_at
#    global iiif, identifier, region, region_x, region_y, region_w, region_h
#    global size, size_w, size_h, size_percent
#    global rotate, quality, format
#    global xmlns, dzi_tilesize, dzi_overlap, dzi_format, dzi_w, dzi_h, dzi_maxlevel
#    global outimage, outimage_quality, outstream, outstream_size
    print('[global variables]'+lf)
    print('[constants]'+lf)
    print('id_uri='+id_uri+lf)
    print('scripts_path='+scripts_path+lf)
    print('data_path='+data_path+lf)
    print('logs_path='+logs_path+lf)
    print('wh_max='+str(wh_max)+lf)
    print('[status]'+lf)
    print('debug='+str(debug)+lf)
    print('status='+status.name+lf)
    print('status_change_at='+status_change_at+lf)
    print('report_flag='+str(report_flag)+lf)
    print('[iiif parameters]'+lf)
    print('iiif='+iiif+lf)
    print('identifier='+identifier+lf)
    print('query='+query.name+lf)
    print('region='+region.name+': '+regiontostr(region_x, region_y, region_w, region_h)+lf)
    print('size='+size.name+': '+sizetostr(size_w, size_h)+'; '+str(size_percent)+'%'+lf)
    print('rotate='+str(rotate)+lf)
    print('quality='+quality+lf)
    print('format='+format_str[format]+lf)
    print('[DZI files]'+lf)
    print('xmlns='+xmlns+lf)
    print('dzi_tilesize='+str(dzi_tilesize)+lf)
    print('dzi_overlap='+str(dzi_overlap)+lf)
    print('dzi_format='+dzi_format+lf)
    print('dzi_w='+str(dzi_w)+lf)
    print('dzi_h='+str(dzi_h)+lf)
    print('dzi_maxlevel='+str(dzi_maxlevel)+lf)
    print('[output image]'+lf)
    print('dzi_region='+regiontostr(dzi_region_x, dzi_region_y, dzi_region_w, dzi_region_h)+lf)
    print('outimage=('+type(outimage).__name__+'): '+sizetostr(outimage_w, outimage_h)+lf)
    print('outimage_quality='+str(outimage_quality)+lf)
    print('outstream=('+type(outstream).__name__+'): '+str(outstream_size)+lf)
    print('[/global variables]'+lf)
    print(lf)
#fed

# HTML形式の表示
def htmlprint() :
    gloprint('<BR>')
#fed
