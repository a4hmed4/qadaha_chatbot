# دليل الاتصال واستكشاف الأخطاء - المساعد التعليمي الذكي 🤖

## 🔗 فحص الاتصال

### 1. فحص حالة الخادم الخلفي (Backend)
```bash
# فحص إذا كان الخادم يعمل
curl http://localhost:5000/health

# أو افتح في المتصفح
http://localhost:5000/health
```

**الاستجابة المتوقعة:**
```json
{
  "status": "healthy",
  "service": "Qadaha Educational Chatbot",
  "database": "connected",
  "total_documents": 123,
  "timestamp": "2025-01-XX XX:XX:XX"
}
```

### 2. فحص قاعدة البيانات (MongoDB)
```bash
# فحص إذا كان MongoDB يعمل
mongo --eval "db.runCommand('ping')"

# أو
mongosh --eval "db.runCommand('ping')"
```

### 3. فحص Ollama
```bash
# فحص إذا كان Ollama يعمل
curl http://localhost:11434/api/tags

# فحص النموذج المطلوب
ollama list
```

## 🚀 خطوات التشغيل الصحيحة

### الطريقة الأولى: التشغيل التلقائي
```bash
# Windows
start_project.bat

# Linux/Mac
chmod +x start_project.sh
./start_project.sh
```

### الطريقة الثانية: التشغيل اليدوي

#### 1. تشغيل MongoDB
```bash
# Linux
sudo systemctl start mongod

# macOS
brew services start mongodb-community

# Windows
# تشغيل MongoDB كخدمة من خلال Services
```

#### 2. تشغيل Ollama
```bash
# تشغيل Ollama
ollama serve

# في نافذة أخرى، تحميل النموذج
ollama pull gemma3:1b
```

#### 3. تشغيل Backend
```bash
# تثبيت التبعيات
pip install -r requirements.txt

# تشغيل الخادم
python app.py
```

#### 4. تشغيل Frontend
```bash
# الانتقال إلى مجلد Frontend
cd frontend

# تثبيت التبعيات
npm install

# تشغيل التطبيق
npm start
```

## 🔍 استكشاف الأخطاء الشائعة

### مشكلة 1: "غير متصل" في الواجهة

**الأسباب المحتملة:**
- الخادم الخلفي غير مشغل
- MongoDB غير مشغل
- Ollama غير مشغل
- مشكلة في الشبكة

**الحلول:**
1. تأكد من تشغيل `python app.py`
2. تأكد من تشغيل MongoDB
3. تأكد من تشغيل Ollama
4. اضغط على زر "إعادة الاتصال" في الواجهة

### مشكلة 2: خطأ في قاعدة البيانات

**الأعراض:**
```
Error: Database connection error
```

**الحلول:**
1. تأكد من تشغيل MongoDB
2. تحقق من إعدادات الاتصال في `config.yaml`
3. تأكد من وجود قاعدة البيانات `Math_Problems`

### مشكلة 3: خطأ في Ollama

**الأعراض:**
```
Error: Model not found
```

**الحلول:**
1. تأكد من تشغيل `ollama serve`
2. تحميل النموذج: `ollama pull gemma3:1b`
3. تحقق من إعدادات النموذج في `config.yaml`

### مشكلة 4: خطأ في Frontend

**الأعراض:**
```
Error: Network Error
```

**الحلول:**
1. تأكد من تشغيل Backend على المنفذ 5000
2. تحقق من إعدادات CORS
3. أعد تشغيل Frontend

## 📋 قائمة فحص سريعة

### قبل التشغيل:
- [ ] MongoDB مثبت ومشغل
- [ ] Ollama مثبت ومشغل
- [ ] النموذج `gemma3:1b` محمل
- [ ] Python 3.8+ مثبت
- [ ] Node.js 16+ مثبت

### أثناء التشغيل:
- [ ] Backend يعمل على http://localhost:5000
- [ ] Frontend يعمل على http://localhost:3000
- [ ] Health check يعطي استجابة إيجابية
- [ ] قاعدة البيانات متصلة
- [ ] النموذج متاح

## 🛠️ أوامر التشخيص

### فحص حالة النظام
```bash
# فحص المنافذ المستخدمة
netstat -tulpn | grep -E ':(3000|5000|27017|11434)'

# فحص العمليات
ps aux | grep -E '(python|node|mongod|ollama)'

# فحص السجلات
tail -f app.log
```

### إعادة تشغيل الخدمات
```bash
# إعادة تشغيل MongoDB
sudo systemctl restart mongod

# إعادة تشغيل Ollama
pkill ollama
ollama serve

# إعادة تشغيل Backend
pkill -f "python app.py"
python app.py
```

## 📞 الدعم الفني

إذا استمرت المشكلة:

1. **جمع المعلومات:**
   - لقطة شاشة للخطأ
   - محتوى سجلات الخطأ
   - إصدارات البرامج المستخدمة

2. **التواصل مع الدعم:**
   - فريق التطوير في مؤسسة قدها
   - وصف مفصل للمشكلة
   - خطوات إعادة الإنتاج

## 🔄 إعادة تعيين النظام

إذا فشل كل شيء:

```bash
# إيقاف جميع الخدمات
sudo systemctl stop mongod
pkill ollama
pkill -f "python app.py"
pkill -f "npm start"

# إعادة تشغيل النظام
sudo systemctl start mongod
ollama serve
python app.py
# في نافذة أخرى
cd frontend && npm start
```

---

**ملاحظة:** تأكد دائماً من تشغيل الخدمات بالترتيب الصحيح: MongoDB → Ollama → Backend → Frontend 