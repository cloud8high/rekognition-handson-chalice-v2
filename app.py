import logging
import traceback
import boto3
import cgi
from chalice import Chalice, BadRequestError
from io import BytesIO

# logger設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Chalice設定
app = Chalice(app_name='rekognition-handson-chalice-v2')

# API Gateway に multipart/form-data をバイナリとして扱うように指示する設定
app.api.binary_types.append('multipart/form-data')

# rekognition インスタンスの作成
rekognition = boto3.client('rekognition')

@app.route('/upload', methods=['POST'], content_types=['multipart/form-data'], cors=True)
def upload():
    # 受け取った情報をバイナリデータとして保存
    body_binary = BytesIO(app.current_request.raw_body)

    # cgi.FieldStorageクラスを用いて、フォームの内容を解析
    environ = {'REQUEST_METHOD': 'POST'}
    headers = {'content-type': app.current_request.headers['content-type']}
    form = cgi.FieldStorage(fp=body_binary, environ=environ, headers=headers)
    
    # ファイルをバイナリ形式で取得（'uploadfile'は送信時に設定した当該ファイルのnameの値）
    file_binary = form.getvalue('uploadfile')

    # 取得した画像ファイルを、Rekognitionに渡して有名人の識別をする
    response = rekognition.recognize_celebrities(
        Image={'Bytes': file_binary}
    )
    logger.info(f'Rekognition response = {response}')

    try:
        # Rekognition のレスポンスから有名人の名前と確度を取り出し、APIのコール元へレスポンスする。
        label   = response['CelebrityFaces'][0]
        name    = label['Name']
        conf    = round(label['Face']['Confidence'])
        output  = { 'name': name, 'confidence': conf }
        logger.info(f'API response = {output}')
        return output

    except IndexError as e:
        # Rekognition のレスポンスから有名人情報を取得出来なかった場合、他の写真で試すように伝える。
        logger.warning(f"Coudn't detect celebrities in the Photo. Exception = {e}")
        logger.warning(traceback.format_exc())
        raise BadRequestError("Couldn't detect celebrities in the uploaded photo. Please upload another photo.")
