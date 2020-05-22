# coding: utf-8

# ======================================================================
# DZI-IIIF
# DeepZoom(dzi)形式のファイルをIIIF Image APIでアクセスできるようにする
# ======================================================================
# 2020-05-21 Ver.0.1 
# ======================================================================
# dziiiif_params.py: パラメタの解釈
# ======================================================================

# 解釈する文字列
# IIIF=[/]<identifier (including '/')>/<region>/<size>/<rotate>/<quality>.<format> （必須）
# REPORT=<any> （任意；画像ではなく処理情報を表示；デバッグモードOnでのみ有効，値は任意だが何かは必要）
# * 20200514 メモ suzuki
# IIIF Image API の仕様では，identifier が / を含むときはURI encoding されていないと
# いけないようだが，「国立国会図書館デジタルコレクションIIIFインターフェース詳細仕様」
# のように，identifierがURI encoding されていない / を含むことを容認している場合も
# あるため，region 以下は正しく URI encoding されているという前提で，identifier を
# 推定することとする．

# 当分はレベル１準拠を満たすように作る．

# グローバル変数の輸入
import dziiiif_common as glo

# モジュールの輸入
import urllib.parse # URIdecoding

# region(x,y,w,h)の読み込み
# 辞書を返す
# * 20200517 メモ suzuki
# IIIF Image API の仕様には，整数の表記に関する規定は明記されて
# いないが，おそらく10進数表記を想定していると思われる．
# この実装では python が int と認識できる書式はすべて受け付ける．
def readregion(s):
    d = {}
    t = s.split(',')
    n = len(t)
    d['x'] = glo.readint(t[0] if (n >= 1) else '')
    d['y'] = glo.readint(t[1] if (n >= 2) else '')
    d['w'] = glo.readint(t[2] if (n >= 3) else '')
    d['h'] = glo.readint(t[3] if (n >= 4) else '')
    return d

# percentregion(x,y,w,h)の読み込み
# 辞書を返す
# * 20200517 メモ suzuki
# IIIF Image API の仕様では，浮動小数点数の表記は最大10桁の10進数
# （つまり指数表記は不可）で，1に満たない場合は'0.'で始まる数字列
# （最大8桁？）と定められているが，この実装ではpythonがfloatと認
# 識できる書式はすべて受け付ける．

def readpercentregion(s):
    d = {}
    t = s.split(',')
    n = len(t)
    d['x'] = glo.readfloat(t[0] if (n >= 1) else '')
    d['y'] = glo.readfloat(t[1] if (n >= 2) else '')
    d['w'] = glo.readfloat(t[2] if (n >= 3) else '')
    d['h'] = glo.readfloat(t[3] if (n >= 4) else '')
    return d

# size(w,h)の読み込み
def readsize(s):
    d = {}
    t = s.split(',')
    n = len(t)
    d['w'] = glo.readint(t[0]) if (n >= 1) else -1
    d['h'] = glo.readint(t[1]) if (n >= 2) else -1
    return d

# percentの読み込み
def readpercent(s):
    return glo.readfloat(s)

# 文字列からのパラメタの取得
def get(s) :
    if (glo.debug and ('REPORT' in s)): 
        glo.report_flag = True # 処理情報表示モードON
    #fi
    if ('IIIF' not in s):
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; IIIF param is not found')
        return
    #fi
    glo.sss = s
    glo.iiif = s['IIIF'].value if ('IIIF' in s) else ''
    t1 = glo.iiif.split('/'); # / をトークンとして分割
    if (len(t1[0]) == 0): t1 = t1[1:]  # 先頭の / を無視
    n = len(t1) # トークンの数
    t2 = t1[n - 1].split('.') # 最後のトークンを . で分割
    m = len(t2)
    # 各トークンは URI エンコーディングされている前提
    quality = urllib.parse.unquote(t2[0]).strip().lower() if (m >= 1) else ''
    glo.quality = quality
    format = urllib.parse.unquote(t2[1]).strip().lower() if (m >= 2) else ''
    glo.format = glo.format_strtocode[format]
    rotate = urllib.parse.unquote(t1[n - 2]).strip() if (n >= 5) else ''
    glo.rotate = rotate
    size = urllib.parse.unquote(t1[n - 3]).strip() if (n >= 5) else ''
    region = urllib.parse.unquote(t1[n - 4]).strip() if (n >= 5) else ''
    identifier = urllib.parse.unquote(('/'.join(t1[0:n-4]))).strip() if (n >= 5) else ''
    # format は当分 jpg のみ許可（レベル１準拠）
    if (glo.format != glo.format_code.JPG): 
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; format != jpg')
    # quality は当分 default のみ許可（レベル１準拠）
    if (quality != 'default'): 
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; quality != default')
    # rotate は当分 0 のみ許可（レベル１準拠）
    if (rotate != '0'): 
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; rotate != 0')
    # identifier はそのまま
    glo.identifier = identifier
    # region の parse
    # squareとpercentは当分不許可
    if (region.lower() == 'full'): 
        glo.region = glo.region_mode.full # 'full' なら full
    elif (region.lower() == 'square'): 
        glo.region = glo.region_mode.square # 'square' なら square
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; region == square') # squareは当分不許可
    elif (region.lower().startswith('pct:')):
        glo.region = glo.region_mode.percent # 'pct:'で始まるなら percent
        pxywh = readpercentregion(region[4:])
        glo.region_x = pxywh['x']
        glo.region_y = pxywh['y']
        glo.region_w = pxywh['w']
        glo.region_h = pxywh['h']
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; region == percent') # percentは当分不許可
    else:
        glo.region = glo.region_mode.pixel # デフォルトは pixel
        xywh = readregion(region)
        glo.region_x = xywh['x']
        glo.region_y = xywh['y']
        glo.region_w = xywh['w']
        glo.region_h = xywh['h']
    # sizeのparse
    # max,wh_align,whは当分不許可
    if (size.lower() == 'full'):
        glo.size = glo.size_mode.full
    elif (size.lower() == 'max'):
        glo.size = glo.size_mode.max
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; size == max') # maxは当分不許可
    elif (size.lower().startswith('pct:')):
        glo.size = glo.size_mode.percent
        glo.size_percent = readpercent(size[4:])
    elif (size.lower().startswith('!')):
        glo.size = glo.size_mode.wh_align
        wh = readsize(size[1:])
        glo.size_w = wh['w']
        glo.size_h = wh['h']
        glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; size == wh_align') # wh_alignは当分不許可
    else: # w_alignかh_alignかwh
        wh = readsize(size)
        glo.size_w = wh['w']
        glo.size_h = wh['h']
        if (glo.size_w < 0 and glo.size_h < 0):
            glo.size = glo.size_mode.wh
            glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; size == wh') # whは当分不許可
        elif (glo.size_w < 0):
            glo.size = glo.size_mode.h_align
        elif (glo.size_h < 0):
            glo.size = glo.size_mode.w_align
        else:
            glo.size = glo.size_mode.wh
            glo.change_status_at(glo.status_code.BAD_REQUEST, 'params.get; size == wh') # whは当分不許可            glo.status = glo.status_code.BAD_REQUEST # whは当分不許可
