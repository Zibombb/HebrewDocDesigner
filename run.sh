#!/bin/bash

# סקריפט הפעלה למערכת ניתוח נתוני מטופלות

echo "🏥 מערכת ניתוח נתוני מטופלות - מרפאת כאבי גב"
echo "================================================="
echo ""

# בדיקת Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 לא מותקן. אנא התקן Python 3.8 ומעלה"
    exit 1
fi

echo "✅ Python נמצא: $(python3 --version)"

# בדיקת pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip לא מותקן"
    exit 1
fi

echo "✅ pip נמצא"

# התקנת תלויות
echo ""
echo "📦 מתקין תלויות..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ שגיאה בהתקנת תלויות"
    exit 1
fi

echo "✅ תלויות הותקנו בהצלחה"
echo ""

# הפעלת Streamlit
echo "🚀 מפעיל את ה-Dashboard..."
echo ""
streamlit run app.py
