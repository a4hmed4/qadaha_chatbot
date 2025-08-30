#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار بسيط لنظام المساعد التعليمي الذكي
"""

import requests
import json
import time

def test_backend_connection():
    """اختبار الاتصال بالـ backend"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ الاتصال بالـ backend يعمل بشكل صحيح")
            return True
        else:
            print(f"❌ خطأ في الاتصال بالـ backend: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ لا يمكن الاتصال بالـ backend. تأكد من تشغيله على المنفذ 5000")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        return False

def test_chat_endpoint():
    """اختبار نقطة نهاية المحادثة"""
    try:
        test_message = "مرحباً، كيف حالك؟"
        payload = {
            "message": test_message,
            "conversation_history": [],
            "session_id": "test_session"
        }
        
        response = requests.post(
            'http://localhost:5000/chat',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print("✅ نقطة نهاية المحادثة تعمل بشكل صحيح")
                print(f"📝 الرد: {data['response'][:100]}...")
                return True
            else:
                print("❌ الرد لا يحتوي على حقل 'response'")
                return False
        else:
            print(f"❌ خطأ في نقطة نهاية المحادثة: {response.status_code}")
            print(f"الرد: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ لا يمكن الاتصال بنقطة نهاية المحادثة")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار المحادثة: {str(e)}")
        return False

def test_frontend_connection():
    """اختبار الاتصال بالـ frontend"""
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ الاتصال بالـ frontend يعمل بشكل صحيح")
            return True
        else:
            print(f"❌ خطأ في الاتصال بالـ frontend: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ لا يمكن الاتصال بالـ frontend. تأكد من تشغيله على المنفذ 3000")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("=" * 50)
    print("🧪 اختبار نظام المساعد التعليمي الذكي")
    print("=" * 50)
    print()
    
    # اختبار الاتصال بالـ backend
    print("1. اختبار الاتصال بالـ backend...")
    backend_ok = test_backend_connection()
    print()
    
    # اختبار نقطة نهاية المحادثة
    if backend_ok:
        print("2. اختبار نقطة نهاية المحادثة...")
        chat_ok = test_chat_endpoint()
        print()
    else:
        chat_ok = False
        print("⏭️ تخطي اختبار المحادثة بسبب فشل الاتصال بالـ backend")
        print()
    
    # اختبار الاتصال بالـ frontend
    print("3. اختبار الاتصال بالـ frontend...")
    frontend_ok = test_frontend_connection()
    print()
    
    # ملخص النتائج
    print("=" * 50)
    print("📊 ملخص النتائج:")
    print("=" * 50)
    
    if backend_ok:
        print("✅ Backend: يعمل بشكل صحيح")
    else:
        print("❌ Backend: لا يعمل")
    
    if chat_ok:
        print("✅ Chat API: يعمل بشكل صحيح")
    else:
        print("❌ Chat API: لا يعمل")
    
    if frontend_ok:
        print("✅ Frontend: يعمل بشكل صحيح")
    else:
        print("❌ Frontend: لا يعمل")
    
    print()
    
    if backend_ok and chat_ok and frontend_ok:
        print("🎉 جميع الاختبارات نجحت! النظام يعمل بشكل صحيح.")
        print("🌐 يمكنك الوصول للتطبيق على: http://localhost:3000")
    else:
        print("⚠️ بعض الاختبارات فشلت. راجع الأخطاء أعلاه.")
        print("💡 تأكد من تشغيل جميع الخدمات المطلوبة.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 