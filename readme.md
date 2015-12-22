# ROHM Sensor Shield Graph tool
ROHMセンサーシールドに搭載した５つのセンサーのデータをRaspberry Piで動作するグラフツールで表示をするためのプログラムです。

# 使用方法
使用するためには諸々のソフトウエアライブラリをインストールする必要があります。以下の手順に従ってインストールしてください。
必要なモジュールのインストールが完了した後、Python3ツールからgw_sensor.pyを実行するとグラフツールを起動します。

gw_sensor.pyを起動した後、startボタンを押してください。
センサーノード側を起動し、センサーノード側をリセットすると、センサーノードからセンサーの情報が送信され、その情報がスクロール画面に表示されます。
その後、graphタブに移動し「logging」ボタンを押すとセンサーデータのロギングを開始します。

## 必要なモジュールのインストール(その1)
sudo apt-get install python3-dev tk tk-dev

## 必要なモジュールのインストール(その2)
pipのインストール
以下のサイトからget-pip.pyをダウンロード
sambaでファイルを保存するのが便利
https://pip.pypa.io/en/latest/installing/

sudo python3 get-pip.py

## 必要なモジュールのインストール(その3)
 numpyのインストール
・Numpyのサイトから「Getting Numpy」-->「SourceForge site for NumPy」-->「Download numpy-1.10.2.zip (4.6 MB)」をダウンロード
http://www.numpy.org/

・ダウンロードしたフォルダに移送して次のコマンドを実行してください。
sudo python3 setup.py build
sudo python3 setup.py install

## 必要なモジュールのインストール(その4)
sudo pip install six python-dateutil pyparsing

## matplotlibのインストールとそのためのスワップメモリ作成
### スワップメモリを作成
```
# create swap file of 512 MB
sudo dd if=/dev/zero of=/swapfile bs=1024 count=524288
# modify permissions
sudo chown root:root /swapfile
sudo chmod 0600 /swapfile
# setup swap area
sudo mkswap /swapfile
# turn swap on
sudo swapon /swapfile
```
### matplotlibのインストール
sudo pip install matplotlib
