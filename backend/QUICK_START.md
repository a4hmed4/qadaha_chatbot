# دليل البدء السريع - المساعد التعليمي الذكي لمؤسسة قدها

## 🚀 تشغيل سريع

### الطريقة الأولى: تشغيل مباشر (Windows)
```bash
# انقر مرتين على الملف
start_project.bat
```

### الطريقة الثانية: تشغيل مباشر (Linux/Mac)
```bash
# إعطاء صلاحيات التنفيذ
chmod +x start_project.sh

# تشغيل المشروع
./start_project.sh
```

### الطريقة الثالثة: تشغيل يدوي

#### 1. تشغيل Backend
```bash
# تثبيت التبعيات
pip install -r requirements.txt

# تشغيل الخادم
python app.py
```

#### 2. تشغيل Frontend (في terminal جديد)
```bash
# الانتقال لمجلد Frontend
cd frontend

# تثبيت التبعيات
npm install

# تشغيل التطبيق
npm start
```

### الطريقة الرابعة: استخدام Docker
```bash
# تشغيل جميع الخدمات
docker-compose up -d

# عرض السجلات
docker-compose logs -f
```

## 🌐 الوصول للتطبيق

- **الواجهة الأمامية**: http://localhost:3000
- **واجهة API**: http://localhost:5000

## 📋 المتطلبات الأساسية

### للطريقة اليدوية:
- Python 3.8+
- Node.js 16+
- MongoDB
- Ollama

### للطريقة Docker:
- Docker
- Docker Compose

## 🔧 إعداد MongoDB

### تثبيت MongoDB
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Windows
# قم بتحميل MongoDB من الموقع الرسمي
```

### تشغيل MongoDB
```bash
# Linux/macOS
sudo systemctl start mongod

# Windows
# تشغيل MongoDB كخدمة
```

## 🤖 إعداد Ollama

### تثبيت Ollama
```bash
# تحميل من الموقع الرسمي
curl -fsSL https://ollama.ai/install.sh | sh
```

### تحميل النموذج
```bash
# تحميل النموذج المطلوب
ollama pull gemma3:1b
```

## 📁 هيكل المشروع
```
qadaha_chatbot/
├── app.py                    # خادم Flask
├── frontend/                 # تطبيق React
├── resources/               # الوثائق التعليمية
├── models/                  # نماذج الذكاء الاصطناعي
├── start_project.bat        # تشغيل سريع (Windows)
├── start_project.sh         # تشغيل سريع (Linux/Mac)
└── docker-compose.yml       # إعداد Docker
```

## 🐛 استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في الاتصال بـ MongoDB**
   - تأكد من تشغيل MongoDB
   - تحقق من إعدادات الاتصال في `config.yaml`

2. **خطأ في الاتصال بـ Ollama**
   - تأكد من تشغيل Ollama
   - تحقق من تحميل النموذج المطلوب

3. **خطأ في Frontend**
   - تأكد من تشغيل Backend أولاً
   - تحقق من إعدادات Proxy في `package.json`

4. **مشاكل في التبعيات**
   - احذف مجلد `node_modules` وأعد التثبيت
   - احذف مجلد `__pycache__` وأعد تشغيل Python

## 📞 الدعم

للمساعدة الإضافية، راجع ملف `README.md` الرئيسي أو تواصل مع فريق التطوير في مؤسسة قدها.

---

**مؤسسة قدها التعليمية** 🎓
*المساعد التعليمي الذكي* 