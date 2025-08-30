@echo off
echo ========================================
echo مؤسسة قدها التعليمية - المساعد التعليمي الذكي
echo ========================================
echo.
echo جاري تشغيل المشروع كاملاً...
echo.

echo [1/3] تشغيل الباك إند...
start "Backend Server" cmd /k "cd backend && python app.py"

echo.
echo انتظار 5 ثوانٍ لبدء الباك إند...
timeout /t 5 /nobreak > nul

echo.
echo [2/3] تشغيل الفرونت إند...
start "Frontend Server" cmd /k "cd frontend && npm install && npm start"

echo.
echo [3/3] فتح المتصفح...
timeout /t 3 /nobreak > nul
start http://localhost:3000

echo.
echo ========================================
echo تم تشغيل المشروع بنجاح!
echo ========================================
echo.
echo الباك إند: http://localhost:5000
echo الفرونت إند: http://localhost:3000
echo.
echo اضغط أي مفتاح لإغلاق هذا النافذة...
pause > nul 