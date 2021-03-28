# 有名人識別サービス - AWS Chalice 編
![rekognition-demo-1](https://user-images.githubusercontent.com/40209684/112740687-f52cae80-8fb9-11eb-89ef-50de3baa0210.gif)

## 本リポジトリについて
以前執筆した以下の記事を、AWS Chalice と Vue.js を用いて作り直してみた取り組みです。  
[【AWSハンズオン】サーバレスアーキテクチャで、有名人識別サービスを作ろう！ - Qiita](https://qiita.com/hayate_h/items/2091dda98bb07f758f06)

## AWS Chalice について
- AWS Chalice とは、AWS が OSS として開発・提供している、Python を用いたサーバレスフレームワークです。
- API Gateway と Lambda を用いた API を簡単に構築することができます。
- ファーストステップとしては、AWS 公式の以下のハンズオンを実施することをおすすめします。
    - [AWS 怠惰なプログラマ向けお手軽アプリ開発手法 2019](https://feature-ai-service.dma9ecr5ksxts.amplifyapp.com/chalice/)

## アーキテクチャ
1. クライアントPCから API Gateway 経由で有名人の画像を Lambda にアップロードします。
2. 画像ファイルの受信をトリガーに、Lambda 関数が起動します。
3. Lambda 関数内で Amazon Rekognition の recognize_celebrities 機能に画像ファイルを送り、画像内の有名人を識別します。
4. 取得した有名人の情報を出力用に整形して、API Gateway を通して返します。
5. 呼び出し元のブラウザ上で、識別結果が表示されます。


## API のデプロイ手順

#### 前提
Git, Python, pip が入っていること。AWS CLI が設定済であること。  
AWS CLI の設定方法については[こちら](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-configure-quickstart.html)

#### python と pip が同じバージョンを向いていることを確認します。
```
$ python -V
Python 3.7.9
$ pip -V
pip 9.0.3 from /usr/lib/python3.7/site-packages (python 3.7)
```

#### 必要に応じて仮想環境を作成・利用します。
```
$ pip install virtualenv
$ virtualenv ~/.virtualenvs/chaliceenv
$ source ~/.virtualenvs/chaliceenv/bin/activate
```

#### 必要なパッケージをインストールします。
```
$ pip install chalice
$ pip install boto3
```

#### 本リポジトリからソースコードをクローンします。
```
$ git clone https://github.com/cloud8high/rekognition-handson-chalice-v2.git
```

#### chaliice deploy コマンドで、APIを作成します。
```
$ cd rekognition-handson-chalice-v2/
$ chalice deploy
Creating deployment package.
Creating IAM role: rekognition-handson-chalice-v2-dev
Creating lambda function: rekognition-handson-chalice-v2-dev
Creating Rest API
Resources deployed:
  - Lambda ARN: arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:function:rekognition-handson-chalice-v2-dev
  - Rest API URL: https://XXXXXXXXXX.execute-api.ap-northeast-1.amazonaws.com/api/
```

デプロイが完了した場合、上記の`Rest API URL`	がAPIのURLとなります。


## アップロード画面（HTMLファイル）の準備方法・開き方

#### 対象ファイル
./frontend-file/ ディレクトリ配下の index.html と main.js がアップロード画面を構成するファイルです。  
（同ディレクトリ配下の simple_page.html はJavaScript を利用していないシンプルなアップロード画面となります。）

#### アップロード先URLの確認
今回の app.py ファイルでは、画像解析処理を `/upload` のパスで設定しています。  
そのため、chalice deploy コマンド後に表示したAPIのURLの末尾に `/upload` をつけたものがアップロード先のパスとなります。  
例：`https://XXXXXXXXXX.execute-api.ap-northeast-1.amazonaws.com/api/upload`

#### アップロード先URLの上書き
./frontend-file/main.js ファイル内の `** API Gateway URL をここに貼り付け! **`に、上記のパスを上書きします。

#### アップロード画面（index.html ファイル）の開き方
今回、JavaScript を利用していることもあり、index.html の開き方について**注意点が３つ**あります。

1. index.html と main.js は同じディレクトリに配置してください。
2. Internet Explorer では動作しません。（ES2018の文法を使用しているため、Chrome などを推奨します。）
3. index.html は http スキーマでブラウザから読み込んでください。　**← 重要！**

３点目について補足説明をします。  
index.html ファイルをブラウザにドラッグ&ドロップして開いた場合、アップロード処理が**正常に作動しません**。  
これは、index.html ファイルを file スキーマの形式でブラウザから読み込んだ場合、Same Origin Policy のセキュリティー制限によって、画像アップロードの JavaScript 処理が正常に動かないためです。  
そのため、以下の方法で**ローカルサーバーを立て、http スキーマで index.html ファイルにアクセスする必要があります。**  
Pythonを用いて簡単にサーバーを起動できます。index.html と main.js が存在するディレクトリで、ターミナルから以下のコマンドを実行してください。

```
$ cd frontend-file/
$ python -m http.server 8080
```
サーバー起動後に`http://0.0.0.0:8080/`にアクセスしてください。作成したHTMLファイルが開けるはずです。  
サーバーを停止する場合は `Ctrl + C` で止めてください。  
なお、index.html や main.js を更新した際、サーバーを再起動しても更新後のファイルがロードされないことがあります。  
その際はターミナルを一度停止し、開き直してサーバーも再起動することで解決します。


## ソースコードのポイント
#### multipart/form-data で送ったファイルが Chalice で正常に読み込めない。
- 問題： multipart/form-data 形式で送ったファイルが utf-8 に再エンコードされてしまう。
- 解決： `app.api.binary_types.append('multipart/form-data')`を挿入することで解決。
- 参考：本トラブルの詳細と解決法について、以下ブログに記載しました。ご参照ください。
    - Qiita


## 参考資料等
- Chalice
  - [Documentation — AWS Chalice](https://aws.github.io/chalice/)
  - https://github.com/aws/chalice/issues/796#issuecomment-717424162
- Vue.js
  - 改訂2版 基礎から学ぶ Vue.js \[2.x対応!]　p.133
- JavaScript
  - [JavaScript Primer - 迷わないための入門書 #jsprimer](https://jsprimer.net/)


## 個人備忘録
#### 公開時に注意するファイル
以下ファイルはプロジェクト固有の情報を含む可能性があるので、公開前に必ず確認
```
.chalice/deployed/dev.json
.frontend-file/main.js
.frontend-file/simple_page.html
```

#### profile を指定した chalice deploy コマンドについて
プロファイルを指定してデプロイする場合、リージョンを指定する必要がある。
```
$ export AWS_DEFAULT_REGION=ap-northeast-1
$ chalice deploy --profile $PROFILE_NAME
```
