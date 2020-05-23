#!/usr/local/bin/python3

# coding: utf-8

# ======================================================================
# makemanifest
# IIIF manifest の生成
# ======================================================================
# 2020-05-23 Ver.0.1: Initial Version.
# ======================================================================

# モジュールの輸入
import os
import urllib.request
import urllib.error
import json
import codecs

# --- 利用者環境に応じて設定する情報 ここから ---

# 入力: json ファイル (utf-8)
# {<Identifier>: { "label": ..., "description":, "license": ..., "attribution": }, ...}
indata_path = os.path.join(os.getcwd(), 'data.json')

# 出力: json ファイル (utf-8)
# manifest は <identifier>.json という名前で作られる．
# 出力ディレクトリ
#outdata_dir_path = os.getcwd()
outdata_dir_path =os.path.join('C:'+os.sep, 'inetpub', 'wwwroot', 'IIIF')
    
# info.json を問い合わせる IIIF サーバ の URI
iiif_server_uri_header = 'http://localhost/cgi-bin/dzi-iiif.cgi?IIIF='

# manifest が置かれる URI
manifest_uri_header = 'http://localhost/IIIF'

# サムネイル画像の大きさ（横幅）
thumbnail_width = 400

# --- 利用者環境に応じて設定する情報 ここまで ---

def getdatabyURI(uri):
    try:    
        with urllib.request.urlopen(uri) as f:
            return (f.read().decode('utf-8'))
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        #fi
        exit()
    #yrt
#fed

# 入力ファイルは存在するか
if (not os.path.isfile(indata_path)):
    print(indata_path+' is not found.')
    exit()
#fi

# json ファイルの読み込み
with codecs.open(indata_path, 'r', 'utf_8') as f:
    indata = json.load(f)
#htiw

for identifier, dict in indata.items(): # identifier と属性値辞書を取得
    print(identifier)
    iiif_server_uri_header_plus_identifier = iiif_server_uri_header + '/' + identifier
    manifest_uri_header_plus_identifier = manifest_uri_header + '/' + identifier
    # 画像サイズの情報を IIIF サーバから取得
    sz = json.loads(getdatabyURI(iiif_server_uri_header_plus_identifier + '/info.json'))
    width = sz['width'] if ('width' in sz) else 0
    height = sz['height'] if ('height' in sz) else 0
    #fi
    # 出力データの生成
    outdata = {}
    outdata['@context'] = 'http://iiif.io/api/presentation/2/context.json'
    outdata['@id'] = manifest_uri_header_plus_identifier + '.json'
    outdata['@type'] = 'sc:Manifest'
    if ('label' in dict):
        outdata['label'] = dict['label']
    #fi
    if ('description' in dict):
        outdata['description'] = dict['description']
    #fi
    if ('license' in dict):
        outdata['license'] = dict['license']
    #fi
    if ('attribution' in dict):
        outdata['attribution'] = dict['attribution']
    #fi
    # thumbnail
    tnb = {}
    tnb['@id'] = iiif_server_uri_header_plus_identifier + '/full/' + str(thumbnail_width) + ',/0/default.jpg'
    outdata['thumbnail'] = tnb
    # service
    svc = {}
    svc['@context'] = 'http://iiif.io/api/image/2/context.json'
    svc['@id'] = iiif_server_uri_header_plus_identifier
    svc['profile'] = 'http://iiif.io/api/image/2/level1.json'
    # resource
    rsc = {}
    rsc['@id'] = iiif_server_uri_header_plus_identifier +'/full/full/0/default.jpg'
    rsc['@type'] = 'dctypes:Image'
    rsc['service'] = svc
    # anotation
    ant = {}
    ant['@type'] = 'oa:Annotation'
    ant['motivation'] = 'sc:painting'
    ant['resource'] = rsc
    ant['on'] = manifest_uri_header_plus_identifier + '/canvas'
    # canvas
    cvs = {}
    cvs['@type'] = 'sc:Canvas'
    cvs['@id'] = manifest_uri_header_plus_identifier + '/canvas'
    cvs['width'] = width
    cvs['height'] = height
    cvs['images'] = [ ant ]
    # sequence
    seq = {}
    seq['@type'] = 'sc:Sequence'
    seq['canvases'] = [ cvs ]
    # sequences
    outdata['sequences'] = [ seq ]
    # manifest をファイルに出力
    outdata_path = os.path.join(outdata_dir_path, identifier+'.json')
    with codecs.open(outdata_path, 'w', 'utf_8') as f:
        json.dump(outdata, f, ensure_ascii=False, indent=4)
    #htiw
#rof
