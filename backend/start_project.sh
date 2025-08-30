#!/bin/bash

echo "========================================"
echo "   المساعد التعليمي الذكي - Qadaha Chatbot"
echo "========================================"
echo

echo "بدء تشغيل المشروع..."
echo

echo "1. تشغيل Backend (Python/Flask)..."
python app.py &
BACKEND_PID=$!

echo
echo "انتظار 5 ثوانٍ لبدء تشغيل Backend..."
sleep 5

echo
echo "2. تشغيل Frontend (React)..."
cd frontend && npm start &
FRONTEND_PID=$!

echo
echo "========================================"
echo "تم تشغيل المشروع بنجاح!"
echo
echo "يمكنك الوصول للتطبيق على:"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:5000"
echo "========================================"
echo

# انتظار إشارة الإيقاف
trap "echo 'إيقاف المشروع...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# انتظار إلى ما لا نهاية
wait 