import io
import json
import os
import re
from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
from gtts import gTTS
from google import genai
from google.genai import types

app = Flask(__name__)

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم اختيار أي صورة'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'الملف المرفوع فارغ'}), 400

    client = get_gemini_client()
    if not client:
        return jsonify({
            'error': 'مفتاح GEMINI_API_KEY غير معرّف في بيئة السيرفر.'
        }), 500

    try:
        image = Image.open(file.stream)
        # تصغير أبعاد الصورة إذا كانت ضخمة لسرعة الاستجابة
        image.thumbnail((1600, 1600))

        prompt = """
        أنت معلم لغة عبرية خبير للمرحلة الابتدائية في مدرسة رندة زربا.
        حلل صفحة كتاب اللغة العبرية المرفقة واستخرج محتواها التعليمي بدقة للأطفال.

        أعد النتيجة حصراً بصيغة JSON بدون أي نصوص أو markdown إضافي، وبالمخطط التالي:
        {
          "lesson_title_hebrew": "العنوان بالعبرية مع التشكيل",
          "lesson_title_arabic": "ترجمة العنوان بالعربية",
          "items": [
            {
              "hebrew_print": "العبارة أو الجملة بخط الطباعة المدرسي مع التشكيل الدقيق",
              "hebrew_clean": "نفس العبارة بدون تشكيل لخط اليد والنطق",
              "arabic": "الترجمة العربية الواضحة للطفلة"
            }
          ]
        }
        قسّم المحتوى إلى جمل وبنود قصيرة وسهلة القراءة ومطابقة للصفحة تماماً.
        """

        # الموديلات الرسمية فائقة السرعة والخفة
        models_to_try = ['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.8-flash']
        response = None
        last_error = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[image, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    break
            except Exception as e:
                last_error = e
                continue

        if not response or not response.text:
            raise last_error or Exception("تعذر تحليل الصورة، يرجى المحاولة مرة أخرى.")

        raw_text = response.text.strip()
        clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_text)
        data = json.loads(clean_json)

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': f'خطأ أثناء المعالجة: {str(e)}'}), 500

@app.route('/api/tts')
def tts_stream():
    text = request.args.get('text', '').strip()
    if not text:
        return jsonify({'error': 'لا يوجد نص للنطق'}), 400

    clean_text = re.sub(r'[\u0591-\u05C7]', '', text)

    try:
        fp = io.BytesIO()
        tts = gTTS(text=clean_text, lang='he', slow=True)
        tts.write_to_fp(fp)
        fp.seek(0)
        return send_file(fp, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': f'فشل إنشاء الصوت: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
