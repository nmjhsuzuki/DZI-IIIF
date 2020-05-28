# DZI-IIIF

Deep Zoom 形式(DZI)画像を，IIIF Image API に沿って呼び出せるようにするための Web CGI です．Python3 で書かれています．画像リクエストと画像情報リクエストの双方に対応しています．

Web CGI for giving IIIF Image API Interface to Deep Zoom image (DZI).

# デモンストレーション (DEMO)

Newcastle という名前の Deep Zoom 画像を取得してみます．12枚のスナップ写真を並べたものです．

画像リクエスト(1)：画像全体を横1000ドットに縮小して取得する．
http://suztak.sakura.ne.jp/cgi-bin/dzi-iiif.cgi?IIIF=/Newcastle/full/1000,/0/default.jpg

画像リクエスト(2)：２行目の左から２枚目の写真を，横1000ドットに縮小して取得する．
Tyne 川のほとりにあるコンサート会場 Sage Gateshead (https://sagegateshead.com/) の写真．
http://suztak.sakura.ne.jp/cgi-bin/dzi-iiif.cgi?IIIF=/Newcastle/5508,3672,5184,3456/1000,/0/default.jpg

画像情報リクエスト：オリジナルの画像サイズが21600x10800画素であることがわかる．
http://suztak.sakura.ne.jp/cgi-bin/dzi-iiif.cgi?IIIF=/Newcastle/info.json

# 特徴 (Features)

IIIF (International Image Interoperability Framework) (https://iiif.io) は，
画像へのアクセスを標準化し相互運用性を確保するための国際的なコミュニティ活動です．
画像へのアクセス方法は IIIF Image API (https://iiif.io/api/image/2.1/) によって規定されています．

Deep Zoom (https://en.wikipedia.org/wiki/Deep_Zoom) は，Microsoft が開発した，任意の大きさの画像を取り扱える画像技術の一つです．
現在では，Openseadragon (https://openseadragon.github.io) を用いて，PC・タブレット・
スマートフォン等の Web ブラウザ上に画像を表示することができます．

私が務める国立歴史民俗博物館 (https://www.rekihaku.ac.jp) では，屏風や絵巻などの一辺が数万～数十万画素に及ぶ画像を，
どこでも任意の倍率で表示する超大画像ビューワを2000年に開発し，常設展示・企画展示等で
来館者の利用に供してきました．2016年ごろから Opensedragon を用いたビューワへ移行し，
画像の保持形式として Deep Zoom 形式を用いています．

歴博の資料画像をより多くの方々に使っていただくためには，IIIFへの対応が不可欠と考えて
いますが，Deep Zoom 形式を取り扱える IIIF 画像サーバがなぜか見つけられません．
ならば，ということで，Python の勉強を兼ねて，作ってみました．

現在はレベル１準拠です．

# 必要な環境 (Requirement)

Python3 が必要です．Pillow も必要なので pip install Pillow しておいてください．

Windows10 Professional 64bit（バージョン1909）上で，以下の環境でテストしています．

* IIS 10.0.18362.1
* Python 3.8.3 (64bit版)
* Pillow 7.1.2

さくらのレンタルサーバースタンダード(FreeBSD 9.1-RELEASE-p24 amd64)上で，以下の環境でテストしています．

* Apache 2.4.43
* Python 3.5.9
* Pillow 7.1.2

# Installation

## Windows10 + IIS 環境へのインストール

## さくらのレンタルサーバへのインストール

Requirementで列挙したライブラリなどのインストール方法を説明する

```bash
pip install huga_package
```

# インストールと使い方 (Usage)

DEMOの実行方法など、"hoge"の基本的な使い方を説明する

```bash
git clone https://github.com/hoge/~
cd examples
python demo.py
```

# その他 (Note)

レベル２準拠への対応まで行なう予定です．

# 作者情報 (Author)

* 鈴木卓治 (SUZUKI, Takuzi)
* 国立歴史民俗博物館 (National Museum of Japanese History, Chiba, JAPAN)
* Email: suzuki@rekihaku.ac.jp

# ライセンス (License)

"DZI-IIIF"は[MIT license](https://en.wikipedia.org/wiki/MIT_License)に従います．

"DZI-IIIF" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).

