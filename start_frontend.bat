@echo off
echo ========================================
echo مؤسسة قدها التعليمية - المساعد التعليمي الذكي
echo ========================================
echo.
echo جاري تشغيل الفرونت إند...
echo.

cd frontend

echo تثبيت التبعيات...
call npm install

echo.
echo تشغيل خادم التطوير...
echo.
echo سيتم فتح المتصفح تلقائياً على العنوان:
echo http://localhost:3000
echo.

call npm start

pause 