#!/bin/bash

echo "========================================"
echo "مؤسسة قدها التعليمية - المساعد التعليمي الذكي"
echo "========================================"
echo ""
echo "جاري تشغيل المشروع كاملاً..."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "❌ Python 3 غير مثبت. يرجى تثبيت Python 3 أولاً."
    exit 1
fi

# Check if Node.js is installed
if ! command_exists node; then
    echo "❌ Node.js غير مثبت. يرجى تثبيت Node.js أولاً."
    exit 1
fi

# Check if npm is installed
if ! command_exists npm; then
    echo "❌ npm غير مثبت. يرجى تثبيت npm أولاً."
    exit 1
fi

echo "[1/3] تشغيل الباك إند..."
cd backend

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "تثبيت تبعيات Python..."
    pip3 install -r requirements.txt
fi

# Start backend in background
echo "تشغيل خادم الباك إند..."
python3 app.py &
BACKEND_PID=$!

cd ..

echo ""
echo "انتظار 5 ثوانٍ لبدء الباك إند..."
sleep 5

echo ""
echo "[2/3] تشغيل الفرونت إند..."
cd frontend

# Install Node.js dependencies
echo "تثبيت تبعيات Node.js..."
npm install

# Start frontend in background
echo "تشغيل خادم الفرونت إند..."
npm start &
FRONTEND_PID=$!

cd ..

echo ""
echo "[3/3] فتح المتصفح..."
sleep 3

# Open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command_exists xdg-open; then
        xdg-open http://localhost:3000
    elif command_exists gnome-open; then
        gnome-open http://localhost:3000
    else
        echo "لا يمكن فتح المتصفح تلقائياً. يرجى فتح http://localhost:3000 يدوياً."
    fi
else
    echo "لا يمكن فتح المتصفح تلقائياً. يرجى فتح http://localhost:3000 يدوياً."
fi

echo ""
echo "========================================"
echo "تم تشغيل المشروع بنجاح!"
echo "========================================"
echo ""
echo "الباك إند: http://localhost:5000"
echo "الفرونت إند: http://localhost:3000"
echo ""
echo "للإيقاف، اضغط Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "إيقاف الخدمات..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "تم إيقاف جميع الخدمات."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 