# 🚗 مُقيّم ميزانية السيارة (Car Purchase Budget Estimator)

تطبيق Flask بواجهة احترافية بيستخدم نموذج تعلّم آلي مُدرّب مسبقًا (AdaBoost + ExtraTrees Regressor)
عشان يتوقع الميزانية المتوقعة إن العميل هيصرفها على شراء سيارة، بناءً على بياناته المالية:
النوع، السن، الدخل السنوي، مديونية البطاقة الائتمانية، وصافي الثروة.

## 📁 هيكل المشروع

```
car-value-predictor/
├── app.py                 # Flask backend
├── model/
│   ├── Model.pkl           # AdaBoostRegressor (ExtraTrees base) — مضغوط
│   ├── Scaler.pkl           # StandardScaler لعمود "net worth" فقط
│   └── Columns.pkl          # أسماء الأعمدة الأصلية
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/script.js
├── requirements.txt
├── Procfile                # لأوامر التشغيل في Render / Railway / Heroku
├── render.yaml              # إعداد جاهز للـ Deploy على Render بضغطة واحدة
├── runtime.txt
└── .gitignore
```

## ⚙️ تفاصيل تقنية مهمة

- **الموديل:** `AdaBoostRegressor` (base estimator: `ExtraTreesRegressor`, 120 estimator)، مُدرّب بـ `scikit-learn==1.6.1`.
- **الـ Features المُستخدمة بالترتيب:** `gender, age, annual Salary, credit card debt, net worth`
- **الـ Scaling:** عمود `net worth` فقط بيتعمله `StandardScaler` قبل ما يدخل الموديل، باقي الأعمدة بتدخل خام.
- **ترميز النوع (Gender):** `Female = 0`, `Male = 1` — ده الترميز الشائع لنفس الداتاسيت المستخدمة (Car Purchase Decision Dataset). لو الترميز اللي استخدمته وقت التدريب مختلف، غيّر `GENDER_MAP` في `app.py`.
- ملف الموديل الأصلي كان حجمه ~330MB، اتضغط بـ `joblib` لحوالي **85MB** عشان يتوافق مع حد رفع الملفات على GitHub (100MB) من غير الحاجة لـ Git LFS.
- ثبّتنا نسخة `scikit-learn==1.6.1` و`numpy>=2.0,<3.0` في `requirements.txt` عشان تطابق البيئة اللي اتدرب فيها الموديل، وتتجنب مشاكل التوافق.

## 🖥️ تشغيل المشروع محليًا

```bash
# 1. أنشئ بيئة افتراضية
python -m venv venv
source venv/bin/activate      # على ويندوز: venv\Scripts\activate

# 2. ثبّت المكتبات
pip install -r requirements.txt

# 3. شغّل التطبيق
python app.py
```

هيفتح على: `http://127.0.0.1:5000`

## 📤 رفع المشروع على GitHub

```bash
cd car-value-predictor
git init
git add .
git commit -m "Initial commit: Car purchase budget estimator"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

> ملحوظة: ملف الموديل داخل `model/Model.pkl` حجمه ~85MB، وده تحت حد GitHub (100MB) فمينفعش يترفض. لو حبيت زيادة الأمان استخدم [Git LFS](https://git-lfs.com):
> ```bash
> git lfs install
> git lfs track "model/*.pkl"
> git add .gitattributes
> ```

## 🚀 Deployment على Render (الطريقة الموصى بيها)

1. اعمل حساب على [render.com](https://render.com) واربطه بحساب GitHub بتاعك.
2. من الداشبورد: **New +** → **Web Service** → اختار الـ repo بتاعك.
3. Render هيكتشف ملف `render.yaml` تلقائيًا ويظبط الإعدادات، أو يدويًا حدد:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
4. اضغط **Create Web Service**، وانتظر الـ Build (بياخد كام دقيقة بسبب حجم الموديل).
5. هتاخد رابط مباشر زي: `https://car-value-predictor.onrender.com`

### بدائل أخرى
- **Railway:** [railway.app](https://railway.app) → New Project → Deploy from GitHub Repo → بيكتشف Flask تلقائيًا عن طريق `Procfile`.
- **PythonAnywhere:** مناسب لو عايز استضافة مجانية بسيطة بدون CI/CD، بترفع الملفات يدويًا أو عن طريق git clone.

## 🔍 نقاط API

| Method | Route      | الوظيفة |
|--------|-----------|---------|
| GET    | `/`        | الصفحة الرئيسية (الفورم) |
| POST   | `/predict` | بياخد JSON ويرجع التوقع |
| GET    | `/health`  | فحص حالة تحميل الموديل |

مثال جسم الطلب لـ `/predict`:
```json
{
  "gender": "male",
  "age": 42,
  "salary": 62812,
  "debt": 11609,
  "net_worth": 238961
}
```

## ⚠️ إخلاء مسؤولية

التقدير الناتج من الموديل إحصائي بناءً على بيانات تاريخية، ومش قرار مالي أو استشارة ائتمانية،
ومينفعش يتاخد كأساس وحيد لأي قرار شراء فعلي.
