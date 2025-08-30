@echo off
echo ========================================
echo    المساعد التعليمي الذكي - مؤسسة قدها
echo ========================================
echo.

echo بدء تشغيل المشروع...
echo.

echo 1. تشغيل Backend (Python/Flask)...
start "Backend - مؤسسة قدها" cmd /k "python app.py"

echo.
echo انتظار 5 ثوانٍ لبدء تشغيل Backend...
timeout /t 5 /nobreak > nul

echo.
echo 2. تشغيل Frontend (React)...
start "Frontend - مؤسسة قدها" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo تم تشغيل المشروع بنجاح!
echo.
echo يمكنك الوصول للتطبيق على:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:5000
echo ========================================
echo.
echo مؤسسة قدها التعليمية - المساعد التعليمي الذكي
echo.
pause 