# coding: utf-8

# ======================================================================
# DZI-IIIF
# DeepZoom(dzi)形式のファイルをIIIF Image APIでアクセスできるようにする
# ======================================================================
# 2020-05-21 Ver.0.1: Initial Version, No info.json handling.
# ======================================================================
# dziiiif_dzifile.py: DZI 形式ファイルの読み込みと加工
# ======================================================================

# * 20200518 メモ suzuki
# 当分 Collection Type の Deep Zoom はサポートしない
# root が Image のものだけサポートする
# * 20200520 メモ suzuki
# 画像処理モジュールとして Pillow のインストールが必要
# >pip install Pillow （管理者モードで実行）

# グローバル変数の輸入
import dziiiif_common as glo

# モジュールの輸入
import os
import xml.etree.ElementTree as ET
import re
from PIL import Image
import math
import io
import sys

# XMLファイル（定義情報）の名前
dzi_xmlfile = 'dzc_output.xml'

# 画像フォルダの名前
dzi_imgfiles = 'dzc_output_files'

# タグ名から xml namespace 名を分離
def getxmlns(s):
    m = re.search(r'^\{[^\}]*\}', s)
    return m.group()
#fed

# タグ名からxml namespaceを除いた名前を求める
def stripxmlns(s):
    m = re.search(r'[^\{\}]*$', s)
    return m.group();
#fed

# XMLファイルの解析を試みる
# root を返す
def tryXMLparse(s):
    try:
        return ET.parse(s).getroot()
    except ET.ParseError:
        return ET.fromstring('<X xmlns="Illegal_XML_file"></X>')
#fed

# XMLファイルの読み込み
def getxmlinfo():
    xmlpath = os.path.join(glo.data_path, glo.identifier, dzi_xmlfile) # XMLファイルへのパスを生成
    if os.path.isfile(xmlpath): 
        root = tryXMLparse(xmlpath) # XMLファイルの読み込み
        glo.xmlns = getxmlns(root.tag)
        if (stripxmlns(root.tag) == 'Image'): # rootタグが Image なら必要なデータを読み出す
            a = root.attrib
            glo.dzi_tilesize = glo.readint(a['TileSize'])
            glo.dzi_overlap= glo.readint(a['Overlap'])
            glo.dzi_format= a['Format']
            f = False
            for child in root:
                if (stripxmlns(child.tag) == 'Size'):
                    a = child.attrib
                    glo.dzi_w = glo.readint(a['Width'])
                    glo.dzi_h = glo.readint(a['Height'])
                    glo.dzi_maxlevel = math.ceil(max(math.log2(glo.dzi_w), math.log2(glo.dzi_h)))
                    f = True
                else: 
                    pass
                #fi
            #rof
            if (not f):
                glo.change_status_at(glo.status_code.NOT_FOUND, 'dzifile.getxmlinfo; Size tag')
        else:
            glo.change_status_at(glo.status_code.NOT_FOUND, 'dzifile.getxmlinfo; Image tag')
        #fi
    else:
        glo.change_status_at(glo.status_code.NOT_FOUND, 'dzifile.getxmlinfo; XML file')
    #fi
#fed

# x を 0 <= x < dzi_w の範囲に収める
def adjustX(x):
    return min(max(x, 0), glo.dzi_w - 1)

# y を 0 <= y < dzi_h の範囲に収める
def adjustY(y):
    return min(max(y, 0), glo.dzi_h - 1)

# 切り取る画像領域の確定
def getregion():
    if (glo.region == glo.region_mode.full):
        x1 = 0
        y1 = 0
        w = glo.dzi_w
        h = glo.dzi_h
    elif (glo.region == glo.region_mode.square):
        wh = min(glo.dzi_w, glo.dzi_h) # 短い方に合わせる
        x1 = int((glo.dzi_w - wh) / 2.0)
        y1 = int((glo.dzi_h - wh) / 2.0)
        w = wh
        h = wh
    elif (glo.region == glo.region_mode.pixel):
        x1 = adjustX(glo.region_x)
        y1 = adjustY(glo.region_y)
        x2 = adjustX(glo.region_x + glo.region_w)
        y2 = adjustY(glo.region_y + glo.region_h)
        w = max(x2 - x1, 0) 
        h = max(y2 - y1, 0)
    elif (glo.region == glo.region_mode.percent):
        x = math.floor(dzi_w * glo.region_x / 100.0)
        y = math.floor(dzi_h * glo.region_y / 100.0)
        w = math.floor(dzi_w * glo.region_w / 100.0)
        h = math.floor(dzi_h * glo.region_h / 100.0)
        x1 = adjustX(x)
        y1 = adjustY(y)
        x2 = adjustX(x + w)
        y2 = adjustY(y + h)
        w = max(x2 - x1, 0)
        h = max(y2 - y1, 0)
    else:
        glo.change_status_at(glo.status_code.INTERNAL_SERVER_ERROR, 'dzifile.getregion') # 起こるはずないんだけど
    #fi
    if (w == 0 or h == 0): # 領域が０もしくは画像外
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'dzifile.getregion; w == 0 || h == 0')
    #fi
    glo.dzi_region_x = x1
    glo.dzi_region_y = y1
    glo.dzi_region_w = w
    glo.dzi_region_h = h
#fed

# 画像サイズの確定
def getsize():
    if (glo.size == glo.size_mode.full or glo.size == glo.size_mode.max ):
        glo.outimage_w = glo.dzi_region_w
        glo.outimage_h = glo.dzi_region_h
    elif (glo.size == glo.size_mode.w_align):
        glo.outimage_w = glo.size_w
        glo.outimage_h = math.floor(glo.size_w * glo.dzi_region_h / glo.dzi_region_w)
    elif (glo.size == glo.size_mode.h_align):
        glo.outimage_w = math.floor(glo.size_h * glo.dzi_region_w / glo.dzi_region_h)
        glo.outimage_h = glo.size_h
    elif (glo.size == glo.size_mode.percent):
        glo.outimage_w = math.floor(glo.dzi_region_w * glo.size_percent / 100.0)
        glo.outimage_h = math.floor(glo.dzi_region_h * glo.size_percent / 100.0)
    elif (glo.size == glo.size_mode.wh):
        glo.outimage_w = glo.size_w
        glo.outimage_h = glo.size_h
    elif (glo.size == glo.size_mode.wh_align):
        dzi_ratio = glo.dzi_region_w /  glo.dzi_region_h # 大きいほど縦長，小さいほど横長
        size_ratio = glo.size_w / glo.size_h
        if (dzi_ratio >= size_ratio): # 画像の方が指定サイズより横長：幅を優先で納める
            glo.outimage_w = glo.size_w
            glo.outimage_h = math.floor(glo.size_w * glo.dzi_region_h / glo.dzi_region_w)
        else: # 画像の方が指定サイズより縦：高さを優先で納める
            glo.outimage_w = math.floor(glo.size_h * glo.dzi_region_w / glo.dzi_region_h)
            glo.outimage_h = glo.size_h
        #fi
    else:
        glo.change_status_at(glo.status_code.INTERNAL_SERVER_ERROR, 'dzifile.getsize') # 起こるはずないんだけど
    #fi
    if (glo.outimage_w == 0 or glo.outimage_h == 0): # 画像サイスが０
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'dzifile.getsize; outimage_w == 0 || outimage_h == 0')
    #fi
    if (glo.outimage_w > glo.wh_max or glo.outimage_h > glo.wh_max): # 画像サイスが制限を超えている
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'dzifile.getsize; outimage_w > wh_max || outimage_h > wh_max')
    #fi

#fed

# 出力ファイルの生成
def makeoutputimage():
    mag_ratio = max(glo.outimage_w / glo.dzi_region_w, glo.outimage_h / glo.dzi_region_h) # 拡大・縮小率
    tileimage_index = math.floor(math.log2(1 / mag_ratio)) # 読み込むタイル画像の倍率（逆数のlog2の指数）
    tileimage_folder_id = str(glo.dzi_maxlevel - tileimage_index).strip() # タイル画像のフォルダ
    # タイル画像座標系における領域
    scaledimage_x = math.floor(glo.dzi_region_x / (2 ** tileimage_index))
    scaledimage_y = math.floor(glo.dzi_region_y / (2 ** tileimage_index))
    scaledimage_w = math.floor(glo.dzi_region_w / (2 ** tileimage_index))
    scaledimage_h = math.floor(glo.dzi_region_h / (2 ** tileimage_index))
    # 読み込むタイル画像のインデックスと領域
    tileimage_i1 = math.floor(scaledimage_x / glo.dzi_tilesize)
    tileimage_i2 = math.floor((scaledimage_x + scaledimage_w - 1) / glo.dzi_tilesize)
    tileimage_j1 = math.floor(scaledimage_y / glo.dzi_tilesize)
    tileimage_j2 = math.floor((scaledimage_y +scaledimage_h - 1) / glo.dzi_tilesize)
    tileimage_x = tileimage_i1 * glo.dzi_tilesize
    tileimage_y = tileimage_j1 * glo.dzi_tilesize
    tileimage_w = (tileimage_i2 - tileimage_i1 + 1) * glo.dzi_tilesize
    tileimage_h = (tileimage_j2 - tileimage_j1 + 1) * glo.dzi_tilesize
    # タイル画像から読み込む入力画像の領域
    inimage_x = scaledimage_x - tileimage_x
    inimage_y = scaledimage_y - tileimage_y
    inimage_w = scaledimage_w
    inimage_h = scaledimage_h
    # 読み込むタイル画像
    image1 = Image.new('RGB', (tileimage_w, tileimage_h), (0, 0, 0))
    # 画像の読み込み
    for i in range(tileimage_i1, tileimage_i2 + 1):
        for j in range (tileimage_j1, tileimage_j2 + 1):
            inimage_fn = str(i).strip()+"_"+str(j).strip()+"."+glo.dzi_format # ファイル名
            inimage_path = os.path.join(glo.data_path, glo.identifier, dzi_imgfiles, tileimage_folder_id, inimage_fn) # タイル画像ファイルへのパスを生成
            glo.inimage_path = inimage_path
            if (os.path.isfile(inimage_path)):
                inimage = Image.open(inimage_path)
                x1 = glo.dzi_overlap if (i > tileimage_i1) else 0
                y1 = glo.dzi_overlap if (j > tileimage_j1) else 0
                x2 = x1 + glo.dzi_tilesize
                y2 = y1 + glo.dzi_tilesize
                cimg = inimage.crop((x1, y1, x2, y2))
                image1.paste(cimg, ((i - tileimage_i1) * glo.dzi_tilesize, (j - tileimage_j1) * glo.dzi_tilesize))
            else:
                glo.change_status_at(glo.status_code.NOT_FOUND, 'dzifile.makeoutputimage; DZI image file')
                break
            #fi
        #rof
    #rof
    # 読んだタイル画像から画像を切り出す
    if (glo.status == glo.status_code.OK):
        image2 = image1.crop((inimage_x, inimage_y, inimage_x + inimage_w, inimage_y + inimage_h))
        glo.outimage = image2.resize((glo.outimage_w, glo.outimage_h))
        o = io.BytesIO()
        glo.outimage.save(o, format=glo.format_PILstr[glo.format], quality=glo.outimage_quality)
        glo.outstream = o.getvalue()
        glo.outstream_size = len(glo.outstream)
    #fi
#fed

