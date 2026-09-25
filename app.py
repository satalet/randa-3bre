import os
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# بيانات الدرس الأول التجريبي الجاهز
DEFAULT_LESSON = {
    "title_hebrew": "חַיַּת מַחְמָד בַּבַּיִת",
    "title_arabic": "حيوان أليف في البيت",
    "sentences": [
        {
            "hebrew": "אֲחוֹתִי עוֹלָא וַאֲנִי אוֹהֲבִים כְּלָבִים. בִּקַּשְׁנוּ מֵהַהוֹרִים שֶׁיָּבִיאוּ לָנוּ כֶּלֶב.",
            "arabic": "أختي عُلا وأنا نحب الكلاب. طلبنا من الوالدين أن يحضروا لنا كلباً."
        },
        {
            "hebrew": "יוֹם אֶחָד אָמְרוּ לָנוּ אִמָּא וְאַבָּא שֶׁאָנוּ מְקַבְּלִים חָבֵר חָדָשׁ לַמִּשְׁפָּחָה.",
            "arabic": "في أحد الأيام، قال لنا بابا وماما إننا سنستقبل صديقاً جديداً للعائلة."
        },
        {
            "hebrew": "כָּךְ שָׂמַחְנוּ! קִוִּינוּ שֶׁזֶּה יִהְיֶה כֶּלֶב. בַּסּוֹף הִגִּיעַ הֶחָבֵר הֶחָדָשׁ.",
            "arabic": "هكذا فرحنا! تمنينا أن يكون كلباً. في النهاية وصل الصديق الجديد."
        },
        {
            "hebrew": "יֵשׁ לוֹ אַרְבַּע רַגְלַיִם וְזָנָב כְּמוֹ לְכֶלֶב, אֲבָל בִּמְקוֹם \"הַב, הַב\" שׁוֹמְעִים \"מְיָאוּ, מְיָאוּ\".",
            "arabic": "له أربع أرجل وذيل مثل الكلب، لكن بدل 'هوْ هوْ' نسمع 'مياو مياو'."
        },
        {
            "hebrew": "חֲבָל, כָּל כָּךְ רָצִינוּ כֶּלֶב!",
            "arabic": "يا للأسف، كم أردنا كلباً!"
        },
        {
            "hebrew": "אִמָּא אָמְרָה שֶׁזֶּה חָתוּל חָמוּד וְיָפֶה וּבִקְשָׁה שֶׁנְּמַשֵּׁשׁ אוֹתוֹ בַּעֲדִינוּת וְנִקְרָא לוֹ בְּשֵׁם מְיֻחָד.",
            "arabic": "قالت أمي إنه قط لطيف وجميل وطلبت أن نلمسه برفق ونسميه باسم مميز."
        },
        {
            "hebrew": "\"אָכֵן זֶה חָתוּל עָדִין וְנֶחְמָד\", אָמְרָה עוֹלָא, וְהֶחְלַטְנוּ לִקְרוֹא לוֹ \"קוּשְׁקוּשׁ\".",
            "arabic": "\"حقاً إنه قط رقيق ولطيف\"، قالت عُلا، وقررنا أن نسميه 'كوشكوش'."
        },
        {
            "hebrew": "לְמָחֳרָת לָקַחְנוּ אֶת הֶחָתוּל לְמִרְפְּאַת הַחַיּוֹת בַּשְּׁכוּנָה.",
            "arabic": "في اليوم التالي أخذنا القط إلى عيادة الحيوانات في الحي."
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html', default_lesson=DEFAULT_LESSON)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم رفع صورة'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # هنا يتم استخراج النص وتحليله (الافتراضي يعرض الدرس المحفوظ)
    return jsonify({
        'status': 'success',
        'lesson': DEFAULT_LESSON
    })

if __name__ == '__main__':
    # التشغيل على 0.0.0.0 ليفتح على أي جهاز أو جوال على نفس الشبكة
    app.run(host='0.0.0.0', port=5000, debug=True)
