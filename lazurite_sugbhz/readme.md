# ROHM Sensor Graph tool
ROHMセンサーシールドに搭載したセンサーのデータをRaspberry Piで動作するグラフツールで表示をするためのプログラムです。
対応しているセンサーは次の通り。
*照度／近接センサ	RPR0521RS
*地磁気センサ		BM1423
*温度/気圧センサ	BM1383
*6軸センサ			KXG03(加速度、ジャイロ)
*UVセンサ			ML8511

# 使い方
*1) lazurite_subghzフォルダ
Lazurite Sub-GHz用のプログラムとライブラリです。
LibrariesフォルダのファイルをLazuriteIDE\Librariesにコピーしてください。

lazurite_subghzフォルダ内の、rohm_sensor.cとrohm_sensor.ssfをLazuriteIDEで読み込み、LazuriteSub-GHzに書き込んで使用してください。
なお、SUBGHZ_CH, SUBGHZ_PANID, 送信先アドレス(SUBGHZ_GATEWAY), SUBGHZ_BITRATE, SUBGHZ_PWRは、Raspberry Pi側の設定と合わせる必要があります。

*2) raspberry_piフォルダ
Raspberry Pi用の関連ファイルです。
予めmatplotlibが動作する環境を準備してください。
詳細はフォルダ内のsetup.pdfを参照してください。

*3) 操作方法
*3-1) Raspberry Pi側を起動し、ch, panid, bitrateを合わせてから"start"ボタンを押してください。
*3-2) Lazurite Sub-GHz側をリセットしてください。
　　接続されているセンサーの種類やデータ形式がLazurite Sub-GHzからRaspberry Piに送信されます。
*3-3)SensorGraphタブを押してloggingボタンを押してください。
　　ただしくセンサーのパラメータを受信できないと、Loggingボタンが有効になりません。
　　

