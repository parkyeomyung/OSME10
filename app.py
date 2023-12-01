from flask import Flask, request, jsonify
import openai
import boto3
import json

app = Flask(__name__)

def setup_openai_api(api_key):
    openai.api_key = api_key

def get_openai_api_key():
    # Secret Manager 클라이언트 생성
    client = boto3.client('secretsmanager', region_name='ap-northeast-2')

    # 시크릿 검색
    response = client.get_secret_value(SecretId='OSME-vY5bd8')

    # 시크릿 값 추출
    if 'SecretString' in response:
        secret = response['SecretString']
    else:
        secret = response['SecretBinary']

    # 시크릿 파싱 (JSON 형식인 경우)
    parsed_secret = json.loads(secret)
    return parsed_secret['OSME']  # JSON 내의 실제 키 이름으로 변경

def get_perfume_recommendation(adjective):
    prompt = f"향수 추천가로서, '{adjective}'이(가) 주요 특징인 향수를 1개 추천해주세요. 향수 이름과 그 특징을 설명해주세요."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2000
    )
    return response.choices[0].text.strip()

def create_imaginary_perfume_image(perfume_name, description):
    prompt = f"상상 속의 향수 이미지: 향수 이름은 '{perfume_name}'이고, 설명은 '{description}'입니다."
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256"
    )
    return response.data[0]["url"]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    recommendation = get_perfume_recommendation(message)
    perfume_name, description = recommendation.split(":", 1)
    image_url = create_imaginary_perfume_image(perfume_name.strip(), description.strip())
    return jsonify({'message': recommendation, 'image_url': image_url})

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    api_key = get_openai_api_key()  # AWS Secret Manager에서 API 키를 검색
    setup_openai_api(api_key)
    app.run(host='0.0.0.0', port=5000)
