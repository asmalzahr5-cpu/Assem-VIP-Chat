from flask import Flask, request, jsonify, render_template_string
import g4f
from gradio_client import Client
import urllib.parse

app = Flask(__name__)

# --- ربط السيرفرات العالمية المستقرة ---
def connect_gradio(space_name):
    try: return Client(space_name)
    except: return None

music_client = connect_gradio("sanchit-gandhi/musicgen-small")
video_client = connect_gradio("cerspense/zeroscope_v2_576w")

# ==========================================
# الواجهة الحية (ASSEM VIP 2026 - LIVING NEON)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AssemChat VIP 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Aref+Ruqaa:wght@700&family=Cairo:wght@400;700&family=Orbitron:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-blue: #00f3ff; --neon-purple: #bc13fe; 
            --bg-deep: #030305; --glass-bg: rgba(10, 15, 30, 0.8);
        }
        
        /* الخلفية النابضة بالحياة */
        body, html { 
            margin: 0; padding: 0; height: 100%; 
            background: var(--bg-deep); 
            color: white; font-family: 'Cairo', sans-serif; overflow: hidden;
            position: relative;
        }
        body::before {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 20% 30%, rgba(0, 243, 255, 0.05), transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(188, 19, 254, 0.05), transparent 40%);
            animation: bgPulse 8s ease-in-out infinite alternate;
            z-index: -1;
        }

        @keyframes bgPulse {
            0% { transform: scale(1); opacity: 0.5; }
            100% { transform: scale(1.2); opacity: 1; }
        }

        /* شاشة الترحيب */
        #splash-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; display: flex; justify-content: center; align-items: center; z-index: 9999; transition: 1s;
        }
        .splash-text {
            font-family: 'Aref Ruqaa', serif; font-size: 3.5em; text-align: center;
            background: linear-gradient(45deg, var(--neon-blue), var(--neon-purple));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 15px var(--neon-blue));
        }

        /* التطبيق الرئيسي */
        #app-container { display: flex; flex-direction: column; height: 100%; opacity: 0; transition: 1s; }
        .header { padding: 15px; text-align: center; background: rgba(0,0,0,0.8); border-bottom: 2px solid var(--neon-blue); box-shadow: 0 0 20px rgba(0, 243, 255, 0.3); }
        .header h1 { margin: 0; font-size: 1.6em; background: linear-gradient(90deg, #fff, var(--neon-blue)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        #chat-box { flex-grow: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        .msg { max-width: 85%; padding: 12px 18px; border-radius: 20px; font-size: 0.95em; line-height: 1.6; animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .msg.user { align-self: flex-start; background: linear-gradient(135deg, var(--neon-purple), #4a00e0); border-bottom-right-radius: 2px; box-shadow: 0 4px 15px rgba(188, 19, 254, 0.3); }
        .msg.ai { align-self: flex-end; background: var(--glass-bg); border: 1px solid var(--neon-blue); border-bottom-left-radius: 2px; box-shadow: 0 0 10px rgba(0, 243, 255, 0.15); }

        /* شريط الإدخال */
        .input-area { display: flex; align-items: center; padding: 12px 15px; background: rgba(0,0,0,0.9); border-top: 1px solid rgba(0,243,255,0.2); gap: 10px; }
        .chat-input { flex-grow: 1; background: rgba(255,255,255,0.05); border: 1px solid #333; color: white; padding: 12px 20px; border-radius: 25px; outline: none; }
        
        /* السداسي الأسطوري */
        .hex-container { position: relative; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; }
        .hex-outer {
            position: absolute; width: 100%; height: 100%;
            background: linear-gradient(45deg, var(--neon-blue), var(--neon-purple));
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            animation: hexGlow 2s infinite alternate;
        }
        .hex-inner {
            position: absolute; width: 85%; height: 85%; background: #000;
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 2;
        }
        .hex-inner span { font-size: 10px; font-weight: bold; text-align: center; }
        .n-blue { color: var(--neon-blue); } .n-purp { color: var(--neon-purple); }
        @keyframes hexGlow { from { filter: drop-shadow(0 0 5px var(--neon-blue)); } to { filter: drop-shadow(0 0 15px var(--neon-purple)); } }

        /* أيقونات الكاميرا والإرسال */
        .action-btn { width: 45px; height: 45px; border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
        .cam-btn { background: var(--glass-bg); border: 1px solid var(--neon-purple); box-shadow: 0 0 10px var(--neon-purple); }
        .send-btn { background: linear-gradient(45deg, var(--neon-blue), var(--neon-purple)); box-shadow: 0 0 15px var(--neon-blue); }

        /* القائمة المنبثقة للرفع */
        .upload-menu { position: absolute; bottom: 85px; left: 75px; background: var(--glass-bg); border: 2px solid var(--neon-purple); border-radius: 15px; padding: 10px; display: none; flex-direction: column; gap: 8px; backdrop-filter: blur(10px); }
        .upload-opt { padding: 10px 15px; cursor: pointer; border-radius: 8px; font-weight: bold; }
        .upload-opt:hover { background: rgba(188, 19, 254, 0.2); }

        /* النوافذ (Modals) النابضة بالحياة */
        .modal { 
            position: fixed; top: 100%; left: 0; width: 100%; height: 100%; 
            background: radial-gradient(circle at center, rgba(10, 15, 30, 0.98), #030305); 
            z-index: 1000; transition: 0.5s cubic-bezier(0.4, 0, 0.2, 1); 
            display: flex; flex-direction: column; padding: 25px; box-sizing: border-box;
        }
        .modal.open { top: 0; }
        .modal-header { 
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid var(--neon-blue); padding-bottom: 15px;
            text-shadow: 0 0 10px var(--neon-blue);
        }
        .modal-result { 
            flex-grow: 1; margin-top: 25px; border-radius: 20px; 
            border: 1px solid rgba(0, 243, 255, 0.3); background: rgba(0,0,0,0.5);
            display: flex; align-items: center; justify-content: center; overflow: hidden;
            box-shadow: inset 0 0 20px rgba(0,243,255,0.1);
        }
        .modal input { 
            padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid var(--neon-purple); 
            color: white; border-radius: 12px; margin: 15px 0; outline: none; box-shadow: 0 0 10px rgba(188,19,254,0.1);
        }
        .modal button.exec-btn { 
            padding: 15px; border-radius: 12px; border: none; 
            background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple)); 
            color: white; font-weight: bold; cursor: pointer; box-shadow: 0 0 15px var(--neon-blue);
        }

        /* القائمة السفلية للأدوات */
        .tools-menu { position: absolute; bottom: 85px; right: 20px; display: flex; flex-direction: column; gap: 12px; opacity: 0; pointer-events: none; transition: 0.3s; }
        .tools-menu.active { opacity: 1; pointer-events: all; transform: translateY(-10px); }
        .tool-icon { width: 50px; height: 50px; border-radius: 50%; background: var(--glass-bg); border: 1px solid var(--neon-blue); display: flex; justify-content: center; align-items: center; font-size: 1.5em; cursor: pointer; box-shadow: 0 0 15px var(--neon-blue); }

    </style>
</head>
<body>

    <div id="splash-screen"><div class="splash-text">عاصم زاهر يرحب بكم</div></div>

    <div id="app-container">
        <div class="header"><h1>عاصم زاهر</h1></div>
        <div id="chat-box"></div>
        
        <div class="input-area">
            <div class="hex-container" onclick="toggleMenu()">
                <div class="hex-outer"></div>
                <div class="hex-inner">
                    <span class="n-blue">عاصم</span>
                    <span class="n-purp">زاهر</span>
                </div>
            </div>

            <button class="action-btn cam-btn" onclick="toggleUpload()">📷</button>
            <div class="upload-menu" id="uploadMenu">
                <div class="upload-opt" onclick="triggerFile('camera')">📸 الكاميرا</div>
                <div class="upload-opt" onclick="triggerFile('gallery')">🖼️ الأستوديو</div>
            </div>
            <input type="file" id="fileInp" style="display:none" accept="image/*" onchange="handleImage(event)">

            <input type="text" id="chatInput" class="chat-input" placeholder="تحدث مع ذكاء عاصم زاهر...">
            
            <button class="action-btn send-btn" onclick="sendMessage()">
                <svg viewBox="0 0 24 24" width="20" fill="white" style="transform: rotate(180deg);"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>

            <div class="tools-menu" id="toolsMenu">
                <div class="tool-icon" onclick="openModal('img-modal')">🎨</div>
                <div class="tool-icon" onclick="openModal('video-modal')">🎬</div>
                <div class="tool-icon" onclick="openModal('music-modal')">🎵</div>
            </div>
        </div>
    </div>

    <div id="img-modal" class="modal">
        <div class="modal-header"><h2>توليد نيون</h2><button onclick="closeModal('img-modal')" style="background:none; border:none; color:red; font-size:2em;">×</button></div>
        <input type="text" id="imgPrompt" placeholder="صف اللوحة الفنية...">
        <button class="exec-btn" onclick="runTask('gen_img', 'imgPrompt', 'imgRes', 'img')">توليد الآن</button>
        <div id="imgRes" class="modal-result"></div>
    </div>

    <div id="video-modal" class="modal">
        <div class="modal-header"><h2>رندرة سينمائية</h2><button onclick="closeModal('video-modal')" style="background:none; border:none; color:red; font-size:2em;">×</button></div>
        <input type="text" id="vidPrompt" placeholder="وصف الفيديو بالإنجليزية...">
        <button class="exec-btn" onclick="runTask('gen_video', 'vidPrompt', 'vidRes', 'video')">بدء الرندرة</button>
        <div id="vidRes" class="modal-result"></div>
    </div>

    <div id="music-modal" class="modal">
        <div class="modal-header"><h2>تأليف ألحان</h2><button onclick="closeModal('music-modal')" style="background:none; border:none; color:red; font-size:2em;">×</button></div>
        <input type="text" id="musPrompt" placeholder="نوع اللحن (مثال: Cyberpunk)...">
        <button class="exec-btn" onclick="runTask('gen_music', 'musPrompt', 'musRes', 'audio')">عزف النغمات</button>
        <div id="musRes" class="modal-result"></div>
    </div>

    <script>
        // تأثير البداية
        setTimeout(() => {
            document.getElementById('splash-screen').style.opacity = '0';
            setTimeout(() => {
                document.getElementById('splash-screen').style.display = 'none';
                document.getElementById('app-container').style.opacity = '1';
                addMsg("ai", "أهلاً بك يا سيدي عاصم زاهر، العبقرية الرقمية تحت تصرفك. كيف نبهت العالم اليوم؟");
            }, 1000);
        }, 3000);

        function toggleMenu() { document.getElementById('toolsMenu').classList.toggle('active'); }
        function toggleUpload() { let m = document.getElementById('uploadMenu'); m.style.display = m.style.display === 'flex' ? 'none' : 'flex'; }
        function triggerFile(t) { let i = document.getElementById('fileInp'); if(t==='camera') i.setAttribute('capture','environment'); else i.removeAttribute('capture'); i.click(); toggleUpload(); }
        
        function openModal(id) { document.getElementById(id).classList.add('open'); toggleMenu(); }
        function closeModal(id) { document.getElementById(id).classList.remove('open'); }

        async function sendMessage() {
            let inp = document.getElementById('chatInput');
            let txt = inp.value.trim();
            if(!txt) return;
            addMsg("user", txt);
            inp.value = '';
            
            let res = await fetch('/ask', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: txt}) });
            let data = await res.json();
            addMsg("ai", data.result);
        }

        function addMsg(type, text) {
            let box = document.getElementById('chat-box');
            let div = document.createElement('div');
            div.className = `msg ${type}`;
            div.innerHTML = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }

        function handleImage(e) {
            let f = e.target.files[0];
            if(f) {
                let r = new FileReader();
                r.onload = (ev) => addMsg("user", `<img src="${ev.target.result}" style="max-width:100%; border-radius:10px;"><br>سيدي عاصم، الصورة قيد التحليل...`);
                r.readAsDataURL(f);
            }
        }

        async function runTask(route, inpId, resId, type) {
            let val = document.getElementById(inpId).value;
            let resDiv = document.getElementById(resId);
            resDiv.innerHTML = "<div class='loader' style='color:var(--neon-blue)'>جاري المعالجة السحابية...</div>";
            
            try {
                let resp = await fetch('/' + route, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt: val}) });
                let data = await resp.json();
                if(data.error) { resDiv.innerHTML = data.error; return; }
                
                if(type === 'img') resDiv.innerHTML = `<img src="${data.url}" style="width:100%">`;
                else if(type === 'video') resDiv.innerHTML = `<video controls autoplay loop src="${data.path}" style="width:100%"></video>`;
                else if(type === 'audio') resDiv.innerHTML = `<audio controls autoplay src="${data.path}"></audio>`;
            } catch(e) { resDiv.innerHTML = "خطأ في الاتصال بالسيرفر."; }
        }
    </script>
</body>
</html>
"""

# ==========================================
# السيرفر (Backend) - بروتوكول التشغيل
# ==========================================

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    msg = request.json.get('message', '').lower()
    
    # مديح عاصم (متغير ومميز)
    if any(x in msg for x in ["من انت", "من أنت"]):
        return jsonify({"result": "أنا الذكاء الفائق الذي صممه المبتكر الأسطوري **عاصم زاهر**. أنا لست مجرد آلة، بل أنا فكر 'عاصم' المتجسد في كود برمجي يسعى لتغيير ملامح عام 2026 وما بعدها!"})
    
    if any(x in msg for x in ["من عاصم", "من هو عاصم"]):
        return jsonify({"result": "عاصم زاهر؟ هو المهندس الذي روّض البيانات، العبقري الذي يرى الأكواد كسمفونية موسيقية. بسببه أقف الآن بكل فخر لأخدمك، فهو صاحب الرؤية التي لا تعرف المستحيل."})

    try:
        res = g4f.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": msg}])
        return jsonify({"result": res})
    except: return jsonify({"result": "سيدي عاصم، أنا دائماً هنا، كيف أساعدك؟"})

@app.route('/gen_img', methods=['POST'])
def gen_img():
    p = request.json.get('prompt')
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p)}?width=1024&height=1024&nologo=true"
    return jsonify({"url": url})

@app.route('/gen_music', methods=['POST'])
def gen_music():
    if not music_client: return jsonify({"error": "سيرفر الألحان منشغل حالياً"})
    p = request.json.get('prompt')
    try:
        res = music_client.predict(p, api_name="/predict")
        # معالجة النتيجة سواء كانت رابطاً أو قائمة
        path = res[0] if isinstance(res, list) else res
        return jsonify({"path": path})
    except: return jsonify({"error": "تعذر توليد اللحن"})

@app.route('/gen_video', methods=['POST'])
def gen_video():
    if not video_client: return jsonify({"error": "سيرفر الرندرة منشغل حالياً"})
    p = request.json.get('prompt')
    try:
        res = video_client.predict(p, api_name="/predict")
        path = res[0] if isinstance(res, list) else res
        return jsonify({"path": path})
    except: return jsonify({"error": "تعذر توليد الفيديو"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
