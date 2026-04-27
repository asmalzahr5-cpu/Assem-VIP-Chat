from flask import Flask, render_template, request, jsonify
import g4f
from gradio_client import Client
import requests

app = Flask(__name__)

# دالة لتجربة الاتصال بالموديلات دون إغلاق البرنامج
def get_client(space_name):
    try:
        return Client(space_name)
    except Exception:
        return None

# تغيير السيرفرات لسيرفرات جديدة أكثر استقراراً
image_gen = "pollinations" # نعتمد عليه كلياً لأنه لا يتوقف
music_client = get_client("facebook/MusicGen") 
# استبدلنا السيرفر المتوقف بسيرفر آخر لتعديل الصور
image_editor = get_client("tencentarc/T2I-Adapter-SDXL") 

@app.route('/')
def index():
    return render_template('index.html')

# 5. صناعة فيديو قصير من النص
@app.route('/make-video', methods=['POST'])
def make_video():
    video_client = get_client("ali-vilab/modelscope-text-to-video")
    if not video_client:
        return jsonify({"error": "سيرفر الفيديو مشغول، جرب لاحقاً"})
    
    prompt = request.json.get('prompt')
    try:
        # سيقوم الموديل بصناعة فيديو مدته ثانيتين تقريباً
        result = video_client.predict(prompt, api_name="/predict")
        return jsonify({"video_path": result})
    except:
        return jsonify({"error": "فشل في صنع الفيديو"})

# 1. النصوص وحل الأسئلة
@app.route('/ask', methods=['POST'])
def ask():
    query = request.json.get('message')
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": query}]
        )
        return jsonify({"result": response})
    except:
        return jsonify({"result": "عذراً، سيرفر النصوص مشغول حالياً."})

# 2. توليد الصور (مستقر جداً)
@app.route('/generate-image', methods=['POST'])
def gen_img():
    prompt = request.json.get('prompt')
    url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true&width=1024&height=1024"
    return jsonify({"url": url})

# 3. تعديل الصور (معالجة الخطأ إذا كان السيرفر متوقف)
@app.route('/edit-image', methods=['POST'])
def edit_img():
    if not image_editor:
        return jsonify({"error": "سيرفر تعديل الصور متوقف حالياً، جرب لاحقاً."})
    
    prompt = request.json.get('prompt')
    img_url = request.json.get('img_url')
    try:
        result = image_editor.predict(img_url, prompt, api_name="/predict")
        return jsonify({"url": result})
    except:
        return jsonify({"error": "فشل في تعديل الصورة."})

if __name__ == '__main__':
    # تشغيل السيرفر على الشبكة المحلية
    app.run(host='0.0.0.0', port=5000, debug=True)

