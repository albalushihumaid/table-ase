# Aircraft Support Equipment

برنامج صيانة معدات الدعم الأرضي (Flask + PostgreSQL/SQLite).

## تشغيل محلي
    pip install -r requirements.txt
    python app.py        # http://localhost:5000  (SQLite تلقائي)

## النشر الدائم (GitHub + Render + Neon)
1. ارفع المجلد على مستودع GitHub جديد.
2. في Neon: أنشئ مشروعاً وانسخ رابط الاتصال (Connection string).
3. في Render: New > Web Service > اختر المستودع (يقرأ render.yaml).
4. أضف المتغيرات: DATABASE_URL = رابط Neon، و ADMIN_PASSWORD = كلمة سر للتعديل (اختياري).
5. Deploy. البيانات والصور والملفات كلها تُحفظ في Neon.

## ملاحظات
- التطبيق يحمّل بيانات تجريبية (3 معدات) عند أول تشغيل على قاعدة فارغة.
- إذا حددت ADMIN_PASSWORD فالقراءة مفتوحة والتعديل يطلب كلمة السر.
- حد الرفع 25 ميجا للملف. للفيديوهات الكبيرة يفضل مساحة تخزين خارجية لاحقاً.
- ربط الحساس: `window.toolSensor.set(toolId, true/false)`.
