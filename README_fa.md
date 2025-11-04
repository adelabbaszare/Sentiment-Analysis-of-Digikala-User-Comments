<div dir="rtl">

# تحلیل احساسات نظرات کاربران دیجی‌کالا

این پروژه یک تحلیل کامل احساسات (Sentiment Analysis) بر روی نظرات کاربران وب‌سایت دیجی‌کالا انجام می‌دهد. فرآیند پروژه شامل جمع‌آوری خودکار داده‌ها از طریق وب اسکرپینگ، پاک‌سازی و پیش‌پردازش متن فارسی، تحلیل داده اکتشافی (EDA) برای کشف الگوها، و در نهایت، آموزش و ارزیابی چندین مدل یادگیری ماشین برای طبقه‌بندی نظرات به دو دسته مثبت و منفی است.

## ساختار پروژه

ساختار فایل‌ها و پوشه‌ها به صورت زیر سازماندهی شده است:

```
SentimentProject/
├── data/
│   ├── digikala_comments.csv
│   └── ccleaned_digikala_comments.csv
├── notebooks/
│   ├── Sentiment Project Notebook.ipynb
│   ├── Digikala Web Scraping.py
│   ├── persian_stopwords.txt
│   └── B Lotus Bold.ttf
├── figures/
│   ├── positive_wordcloud.png
│   ├── negative_frequent_words.png
│   └── ... (سایر تصاویر)
├── reports/
│   └── final_report.pdf
├── README.md
└── requirements.txt
```

## مراحل اصلی پروژه
- **جمع‌آوری داده‌ها (Web Scraping):** استخراج نظرات کاربران از صفحات محصولات مختلف دیجی‌کالا با استفاده از Selenium و BeautifulSoup.
- **پاک‌سازی و پیش‌پردازش متن (Text Preprocessing):** آماده‌سازی نظرات فارسی برای تحلیل، شامل نرمال‌سازی، توکنایز کردن، ریشه‌یابی کلمات و حذف کلمات توقف (Stopwords).
- **تحلیل داده اکتشافی (Exploratory Data Analysis):** مصورسازی داده‌ها برای درک بهتر توزیع امتیازات، احساسات، و کلمات پرتکرار در نظرات مثبت و منفی از طریق نمودارها و ابر کلمات (Word Clouds).
- **برداری‌سازی متن (Text Vectorization):** تبدیل متن‌های پاک‌سازی شده به بردارهای عددی با استفاده از مدل TF-IDF برای استفاده در مدل‌های یادگیری ماشین.
- **مدل‌سازی و ارزیابی (Modeling and Evaluation):** آموزش و ارزیابی چهار مدل مختلف (Logistic Regression, Naive Bayes, SVM, Random Forest) و مقایسه عملکرد آن‌ها با استفاده از معیارهایی مانند دقت (Accuracy) و ماتریس درهم‌ریختگی (Confusion Matrix).

---

## راه‌اندازی و نصب (Setup and Installation)

برای اجرای این پروژه، مراحل زیر را دنبال کنید.

### ۱. کلون کردن مخزن (Clone Repository)
ابتدا پروژه را از گیت‌هاب (یا هر منبع دیگری) کلون کنید:
```bash
git clone <URL-پروژه-شما>
cd SentimentProject
```

### ۲. ایجاد محیط مجازی (Virtual Environment)
برای جلوگیری از تداخل کتابخانه‌ها، یک محیط مجازی `venv` بسازید:
```bash
python -m venv venv
```

### ۳. فعال‌سازی محیط مجازی
بسته به سیستم‌عامل خود، دستور مناسب را اجرا کنید:

- **در ویندوز (Windows):**
  ```bash
  venv\Scripts\activate
  ```

- **در مک یا لینوکس (macOS/Linux):**
  ```bash
  source venv/bin/activate
  ```
پس از اجرای این دستور، نام محیط مجازی `(venv)` در ابتدای خط فرمان شما نمایش داده می‌شود.

### ۴. نصب کتابخانه‌های مورد نیاز
تمام کتابخانه‌های لازم در فایل `requirements.txt` لیست شده‌اند. آن‌ها را با دستور زیر نصب کنید:
```bash
pip install -r requirements.txt
```
**نکته:** اگر فایل `requirements.txt` را ندارید، می‌توانید آن را با محتوای زیر بسازید:
<details>
  <summary>محتوای فایل requirements.txt</summary>
  
  ```
# Web Scraping
selenium==4.35.0
beautifulsoup4==4.13.4

# Data Manipulation and Numerical Operations
pandas==2.3.2
numpy==1.25.0

# Machine Learning and Feature Extraction
scikit-learn==1.7.1

# Data Visualization
matplotlib==3.10.5
seaborn==0.13.2
wordcloud==1.9.4

# Persian Language Processing (NLP)
hazm==0.10.0
arabic-reshaper==3.0.0
python-bidi==0.6.6
  ```
</details>

### ۵. افزودن محیط مجازی به عنوان کرنل ژوپیتر (Jupyter Kernel)
برای اینکه بتوانید نوت‌بوک را با استفاده از کتابخانه‌های نصب شده در محیط مجازی اجرا کنید، باید این محیط را به عنوان یک کرنل به ژوپیتر معرفی کنید.

- ابتدا مطمئن شوید `ipykernel` نصب است (در فایل `requirements.txt` وجود دارد).
- سپس دستور زیر را در ترمینال (در حالی که محیط مجازی فعال است) اجرا کنید:
  ```bash
  python -m ipykernel install --user --name=sentiment-env --display-name "Python (Sentiment Env)"
  ```
این دستور یک کرنل جدید با نام نمایشی `Python (Sentiment Env)` به ژوپیتر اضافه می‌کند.

---

## نحوه اجرای پروژه

### مرحله اول: جمع‌آوری داده‌ها
۱. وارد پوشه `notebooks` شوید:
   ```bash
   cd notebooks
   ```
۲. اسکریپت وب اسکرپینگ را اجرا کنید تا نظرات جمع‌آوری شده و در پوشه `data` ذخیره شوند:
   ```bash
   python "Digikala Web Scraping.py"
   ```
   این فرآیند ممکن است چند دقیقه طول بکشد.

### مرحله دوم: اجرای نوت‌بوک تحلیل
۱. در ریشه اصلی پروژه (`SentimentProject/`)، ژوپیتر لب یا ژوپیتر نوت‌بوک را اجرا کنید:
   ```bash
   jupyter lab
   # یا
   # jupyter notebook
   ```
۲. در محیط ژوپیتر، به پوشه `notebooks` بروید و فایل `Sentiment Project Notebook.ipynb` را باز کنید.
۳. از منوی بالای نوت‌بوک، کرنل را به `Python (Sentiment Env)` (یا هر نامی که در مرحله ۵ انتخاب کردید) تغییر دهید.
۴. اکنون می‌توانید سلول‌های نوت‌بوک را به ترتیب اجرا کنید.

## خروجی‌ها
پس از اجرای کامل پروژه، فایل‌های زیر تولید خواهند شد:
- **`data/digikala_comments.csv`**: داده‌های خام استخراج شده از دیجی‌کالا.
- **`data/ccleaned_digikala_comments.csv`**: دیتاست نهایی پس از پاک‌سازی و پیش‌پردازش.
- **تصاویر در پوشه `figures/`**: تمام نمودارها، ابرهای کلمات و ماتریس‌های درهم‌ریختگی در این پوشه ذخیره می‌شوند.

</div>