# coding: utf-8

# ======================================================================
# DZI-IIIF
# DeepZoom(dzi)形式のファイルをIIIF Image APIでアクセスできるようにする
# ======================================================================
# 2020-05-21 Ver.0.1: Initial Version, No info.json handling.
# ======================================================================
# dziiiif_main.py: メインモジュール
# ======================================================================

# グローバル変数の輸入
import dziiiif_common as glo

# モジュールの輸入
import sys
import cgi
if glo.debug : 
    import cgitb
    cgitb.enable(logdir = glo.logs_path)
#fi

# パラメタの取得
import dziiiif_params as para
para.get(cgi.FieldStorage())

# 画像の読み込みと加工
import dziiiif_dzifile as dzi
if (glo.status == glo.status_code.OK) : dzi.getxmlinfo()
if (glo.status == glo.status_code.OK) : dzi.getregion()
if (glo.status == glo.status_code.OK) : dzi.getsize()
if (glo.status == glo.status_code.OK) : dzi.makeoutputimage()

# 出力
print ('Status: '+str(glo.status.value)+' '+glo.status_str[glo.status])
if ((not glo.report_flag) and (glo.status == glo.status_code.OK)) :
    print('Content-Type: '+glo.format_mimetype[glo.format])
    print('Content-Length: %d' % glo.outstream_size)
    print('')
    sys.stdout.flush()
    sys.stdout.buffer.write(glo.outstream)
else:
    print ('Content-Type: text/html; charset=UTF-8')
    print ('')
    print ('<!DOCTYPE html>')
    print ('<HTML>')
    print ('<HEAD>')
    print ('<TITLE>DZI-IIIF Report</TITLE>')
    print ('</HEAD>')
    print ('<BODY>')
    print ('<H1>DZI-IIIF Report</H1>')
    print ('<P>' )
    print ('Status: '+str(glo.status.value)+' '+glo.status_str[glo.status])
    print ('<BR/><BR/>')
    glo.htmlprint()
    print ('</P>')
    print ('</BODY>')
    print ('</HTML>')
#fi
