# kintai-paccho
Slackから勤怠入力するSlack Botだぱっちょ。

[KING OF TIME](https://www.kingtime.jp/) のみに対応しています。


## 事前準備
Slack Appの作成。
参考: https://slack.dev/bolt-python/tutorial/getting-started

Socket Mode は ON にする

<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/setup1.png" alt="" style="width: 600px;">

必要な権限

<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/setup2.png" alt="" style="width: 600px;">

<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/setup2-2.png" alt="" style="width: 600px;">


Slash コマンドの登録

<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/setup3.png" alt="" style="width: 600px;">



## 起動方法

```
$ git clone git@github.com:showwin/kintai-paccho.git
$ cd kintai-paccho

# 環境変数を設定
$ cp .envrc.example .envrc
$ direnv allow

$ poetry install
$ poetry run python run.py
```

supervisor などで監視すると良いと思います。

## フォーマット

```
$ make fmt
```

## テスト

```
$ make test
```

## botとの接し方

### Lv.0
登録する

bot をチャンネルに呼ぶか、botに直接以下のメッセージを送る。

`/employee-code <your-code>` で登録。従業員番号はKing of Timeログイン後に画面右上の自分の名前の横に出てくる数字のこと。

![](https://github.com/showwin/kintai-paccho/raw/master/doc/how_to_use_setup.png)



### Lv.1
`おはー` と `おつー`  で出勤と退勤

<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/how_to_use_1.png" alt="" style="width: 300px;">


### Lv.2
途中で休憩するとき

<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/how_to_use_2.png" alt="" style="width: 300px;">
<img src="https://github.com/showwin/kintai-paccho/raw/master/doc/how_to_use_3.png" alt="" style="width: 300px;">


## 注意事項
可愛いアイコンたちは **著作権に違反しない範囲で** ご自身でご設定ください :pray:
