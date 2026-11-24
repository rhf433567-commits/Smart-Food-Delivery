
# استيراد مكتبة Streamlit لإنشاء لوحة البيانات
import streamlit as st

# استيراد مكتبة Pandas لمعالجة البيانات
import pandas as pd

# إعداد عنوان التطبيق وطريقة عرضه
st.set_page_config(
    page_title="Smart Food Delivery Dashboard",
    page_icon="🚚",
    layout="wide"
)

# إضافة عنوان رئيسي للتطبيق
st.title("Smart Food Delivery Dashboard")

# إضافة وصف مختصر للوحة البيانات
st.write("لوحة تحليل أوقات توصيل طلبات الطعام")


# استخدام التخزين المؤقت لتسريع تحميل البيانات
@st.cache_data
def load_data():

    # تحميل البيانات النظيفة من ملف CSV
    data = pd.read_csv("data/clean.csv")

    # إرجاع البيانات بعد تحميلها
    return data


# استدعاء دالة تحميل البيانات
df = load_data()


# عرض أسماء الأعمدة الموجودة فعلًا في ملف البيانات
st.write("أسماء الأعمدة الموجودة في البيانات:")
st.write(df.columns.tolist())


# تحديد الأعمدة المطلوبة للفلاتر
filter_columns = [
    "Weatherconditions",
    "Road_traffic_density",
    "Type_of_vehicle",
    "Order_Time_Period"
]

# عرض الأعمدة المطلوبة التي لم يتم العثور عليها
missing_columns = [
    column for column in filter_columns
    if column not in df.columns
]

st.write("الأعمدة غير الموجودة:", missing_columns)


# التأكد من أن عمود وقت التوصيل رقمي
df["Time_taken(min)"] = pd.to_numeric(
    df["Time_taken(min)"],
    errors="coerce"
)


# إنشاء عنوان للفلاتر الجانبية
st.sidebar.header("Data Filters")

# إنشاء نسخة من البيانات لتطبيق الفلاتر عليها
filtered_df = df.copy()

# إنشاء فلتر مستقل لكل عمود موجود
for column in filter_columns:

    # تخطي العمود إذا لم يكن موجودًا في البيانات
    if column not in filtered_df.columns:
        continue

    # استخراج القيم الموجودة في العمود
    values = sorted(
        filtered_df[column].dropna().unique().tolist()
    )

    # إضافة خيار عرض جميع القيم
    selected_value = st.sidebar.selectbox(
        column,
        ["All"] + values
    )

    # تطبيق الفلتر إذا اختار المستخدم قيمة محددة
    if selected_value != "All":
        filtered_df = filtered_df[
            filtered_df[column] == selected_value
        ]


# إضافة عنوان للمؤشرات الرئيسية
st.header("Key Performance Indicators")

# حساب عدد الطلبات بعد تطبيق الفلاتر
total_orders = len(filtered_df)

# حساب متوسط وقت التوصيل
average_delivery = filtered_df["Time_taken(min)"].mean()

# حساب متوسط مسافة التوصيل إذا كان العمود موجودًا
average_distance = (
    filtered_df["Distance_km"].mean()
    if "Distance_km" in filtered_df.columns
    else float("nan")
)

# حساب متوسط وقت التحضير إذا كان العمود موجودًا
average_preparation = (
    filtered_df["Preparation_Time"].mean()
    if "Preparation_Time" in filtered_df.columns
    else float("nan")
)


# تقسيم مساحة الصفحة إلى أربعة أعمدة للمؤشرات
col1, col2, col3, col4 = st.columns(4)

# عرض إجمالي الطلبات
col1.metric("Total Orders", f"{total_orders:,}")

# عرض متوسط وقت التوصيل بالدقائق
col2.metric(
    "Average Delivery Time",
    f"{average_delivery:.2f} min"
    if pd.notna(average_delivery) else "N/A"
)

# عرض متوسط مسافة التوصيل بالكيلومترات
col3.metric(
    "Average Distance",
    f"{average_distance:.2f} km"
    if pd.notna(average_distance) else "N/A"
)

# عرض متوسط وقت التحضير
col4.metric(
    "Average Preparation Time",
    f"{average_preparation:.2f} min"
    if pd.notna(average_preparation) else "N/A"
)


# إضافة فاصل بين المؤشرات والرسوم
st.divider()

# إضافة عنوان قسم الرسوم البيانية
st.header("Delivery Time Analysis")


# رسم متوسط وقت التوصيل حسب كثافة المرور
if "Road_traffic_density" in filtered_df.columns:

    # تجميع البيانات حسب كثافة المرور وحساب المتوسط
    traffic_chart = (
        filtered_df.groupby("Road_traffic_density")["Time_taken(min)"]
        .mean()
        .sort_values(ascending=False)
    )

    # إضافة عنوان الرسم
    st.subheader("Average Delivery Time by Traffic Density")

    # عرض الرسم البياني
    st.bar_chart(traffic_chart)


# رسم متوسط وقت التوصيل حسب حالة الطقس
if "Weatherconditions" in filtered_df.columns:

    # تجميع البيانات حسب حالة الطقس وحساب المتوسط
    weather_chart = (
        filtered_df.groupby("Weatherconditions")["Time_taken(min)"]
        .mean()
        .sort_values(ascending=False)
    )

    # إضافة عنوان الرسم
    st.subheader("Average Delivery Time by Weather")

    # عرض الرسم البياني
    st.bar_chart(weather_chart)


# رسم متوسط وقت التوصيل حسب فترة الطلب
if "Order_Time_Period" in filtered_df.columns:

    # تجميع البيانات حسب فترة الطلب وحساب المتوسط
    period_chart = (
        filtered_df.groupby("Order_Time_Period")["Time_taken(min)"]
        .mean()
        .sort_values(ascending=False)
    )

    # إضافة عنوان الرسم
    st.subheader("Average Delivery Time by Order Period")

    # عرض الرسم البياني
    st.bar_chart(period_chart)
