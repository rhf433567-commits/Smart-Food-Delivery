
# استيراد المكتبات
import streamlit as st
import pandas as pd

# إعداد شكل التطبيق
st.set_page_config(
    page_title="Smart Food Delivery",
    page_icon="🚚",
    layout="wide"
)

# عنوان التطبيق
st.title("🚚 Smart Food Delivery")
st.write("منصة تحليل أوقات توصيل طلبات الطعام وتقدير وقت وصول الطلب")

# تحميل البيانات
@st.cache_data
def load_data():
    return pd.read_csv("data/clean.csv")

df = load_data()

# البحث عن اسم العمود الصحيح حتى لو اختلفت التسمية
def find_column(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# تحديد الأعمدة المستخدمة
target = find_column(["Time_taken(min)", "Time_taken(دقيقة)"])
weather = find_column(["Weatherconditions", "Weather_conditions", "الظروف الجوية"])
traffic = find_column(["Road_traffic_density"])
vehicle = find_column(["Type_of_vehicle"])
period = find_column(["Order_Time_Period"])
distance = find_column(["Distance_km"])

# التأكد من وجود عمود وقت التوصيل
if target is None:
    st.error("لم يتم العثور على عمود وقت التوصيل. راجعي أسماء الأعمدة في ملف البيانات.")
    st.write(df.columns.tolist())
    st.stop()

# تحويل وقت التوصيل إلى أرقام
df[target] = pd.to_numeric(df[target], errors="coerce")

# إنشاء التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs([
    "📊 نظرة عامة",
    "🔍 الاكتشافات والتوصيات",
    "⏱️ توقع وقت التوصيل"
])

# --------------------------------------------------
# التبويب الأول: نظرة عامة
# --------------------------------------------------
with tab1:
    st.header("نظرة عامة على الطلبات")

    # إنشاء نسخة من البيانات لتطبيق الفلاتر
    filtered_df = df.copy()

    # إنشاء الفلاتر الجانبية
    st.sidebar.header("تصفية البيانات")

    filter_columns = [
        ("الطقس", weather),
        ("كثافة المرور", traffic),
        ("نوع المركبة", vehicle),
        ("فترة الطلب", period)
    ]

    for label, column in filter_columns:
        if column is not None:
            values = sorted(
                filtered_df[column].dropna().astype(str).unique().tolist()
            )

            selected = st.sidebar.selectbox(
                label,
                ["الكل"] + values,
                key=f"filter_{column}"
            )

            if selected != "الكل":
                filtered_df = filtered_df[
                    filtered_df[column].astype(str) == selected
                ]

    # حساب المؤشرات الرئيسية
    total_orders = len(filtered_df)
    average_time = filtered_df[target].mean()

    average_distance = (
        pd.to_numeric(filtered_df[distance], errors="coerce").mean()
        if distance else None
    )

    preparation = find_column(["Preparation_Time"])
    average_preparation = (
        pd.to_numeric(filtered_df[preparation], errors="coerce").mean()
        if preparation else None
    )

    # عرض المؤشرات
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("إجمالي الطلبات", f"{total_orders:,}")
    col2.metric(
        "متوسط وقت التوصيل",
        f"{average_time:.2f} دقيقة" if pd.notna(average_time) else "غير متاح"
    )
    col3.metric(
        "متوسط المسافة",
        f"{average_distance:.2f} كم"
        if average_distance is not None and pd.notna(average_distance)
        else "غير متاح"
    )
    col4.metric(
        "متوسط وقت التحضير",
        f"{average_preparation:.2f} دقيقة"
        if average_preparation is not None and pd.notna(average_preparation)
        else "غير متاح"
    )

    st.divider()
    st.subheader("بيانات الطلبات بعد تطبيق الفلاتر")
    st.write(f"عدد الطلبات المعروضة: {len(filtered_df):,}")
    st.dataframe(filtered_df.head(20), use_container_width=True)

# --------------------------------------------------
# التبويب الثاني: الاكتشافات والتوصيات
# --------------------------------------------------
with tab2:
    st.header("أهم الاكتشافات من تحليل البيانات")

    # رسم متوسط وقت التوصيل حسب كثافة المرور
    if traffic:
        st.subheader("متوسط وقت التوصيل حسب كثافة المرور")

        traffic_data = (
            df.groupby(traffic)[target]
            .mean()
            .sort_values(ascending=False)
        )

        st.bar_chart(traffic_data)
        st.write(
            "أظهر التحليل أن الازدحام يرتبط بارتفاع وقت التوصيل؛ "
            "حيث بلغ المتوسط 31.18 دقيقة في الازدحام، مقابل 21.27 دقيقة "
            "في الطرق منخفضة الكثافة."
        )

    # رسم متوسط وقت التوصيل حسب الطقس
    if weather:
        st.subheader("متوسط وقت التوصيل حسب حالة الطقس")

        weather_data = (
            df.groupby(weather)[target]
            .mean()
            .sort_values(ascending=False)
        )

        st.bar_chart(weather_data)
        st.write(
            "سجل الطقس الغائم والضباب أعلى متوسط، بواقع 28.92 دقيقة، "
            "بينما سجل الطقس المشمس 21.86 دقيقة."
        )

    # رسم متوسط وقت التوصيل حسب فترة الطلب
    if period:
        st.subheader("متوسط وقت التوصيل حسب فترة الطلب")

        period_data = (
            df.groupby(period)[target]
            .mean()
            .sort_values(ascending=False)
        )

        st.bar_chart(period_data)
        st.write(
            "كانت فترة المساء الأعلى بمتوسط 29.21 دقيقة، "
            "بينما كان الصباح الأقل بمتوسط 21.28 دقيقة."
        )

    st.divider()
    st.subheader("أهم التوصيات")

    st.markdown("""
    1. مراعاة كثافة المرور عند تقدير وقت وصول الطلب.
    2. تعديل الوقت المتوقع حسب الظروف الجوية.
    3. مراعاة فترة الطلب، خصوصًا فترة المساء.
    4. استخدام بيانات الطلبات السابقة لتحسين دقة التوقعات.
    """)

    st.info(
        "هذه النتائج توضح علاقات في البيانات، ولا تعني بالضرورة أن "
        "عاملًا واحدًا هو السبب المباشر في التأخير."
    )

# --------------------------------------------------
# التبويب الثالث: منتج تقدير وقت التوصيل
# --------------------------------------------------
with tab3:
    st.header("⏱️ احسب وقت التوصيل المتوقع")
    st.write("أدخل ظروف طلبك للحصول على تقدير مبني على طلبات مشابهة.")

    # إنشاء مدخلات العميل
    selected_features = {}

    product_inputs = [
        ("حالة الطقس", weather),
        ("كثافة المرور", traffic),
        ("نوع المركبة", vehicle),
        ("فترة الطلب", period)
    ]

    for label, column in product_inputs:
        if column is not None:
            options = sorted(
                df[column].dropna().astype(str).unique().tolist()
            )

            if options:
                selected_features[column] = st.selectbox(
                    label,
                    options,
                    key=f"product_{column}"
                )

    # إدخال المسافة إذا كانت متوفرة
    selected_distance = None

    if distance is not None:
        distance_values = pd.to_numeric(
            df[distance], errors="coerce"
        ).dropna()

        if not distance_values.empty:
            selected_distance = st.number_input(
                "مسافة التوصيل بالكيلومتر",
                min_value=0.0,
                max_value=float(distance_values.max()),
                value=float(distance_values.median()),
                step=0.5
            )

    
    # زر حساب التوقع
    if st.button("احسب وقت التوصيل المتوقع", type="primary"):

        # تحديد الحد الأدنى لعدد الطلبات المشابهة
        minimum_orders = 5

        # تجهيز شروط البحث حسب بيانات العميل
        available_conditions = list(selected_features.items())

        # إنشاء مراحل البحث من الأكثر تطابقًا إلى الأقل
        search_stages = [
            ("جميع الظروف مع المسافة", available_conditions, True),
            ("جميع الظروف بدون المسافة", available_conditions, False),
            (
                "الطقس والمرور",
                [
                    (column, value)
                    for column, value in available_conditions
                    if column in [weather, traffic]
                ],
                False
            ),
            (
                "المرور فقط",
                [
                    (column, value)
                    for column, value in available_conditions
                    if column == traffic
                ],
                False
            ),
            ("جميع الطلبات", [], False)
        ]

        # البحث بالتدريج عن عدد كافٍ من الطلبات
        similar_orders = pd.DataFrame()
        used_stage = ""

        for stage_name, conditions, use_distance in search_stages:

            # إنشاء نسخة من البيانات
            current_orders = df.copy()

            # تطبيق شروط المطابقة
            for column, value in conditions:
                current_orders = current_orders[
                    current_orders[column].astype(str) == value
                ]

            # تطبيق شرط المسافة إذا كانت المرحلة تتطلب ذلك
            if use_distance and selected_distance is not None:
                current_distance = pd.to_numeric(
                    current_orders[distance],
                    errors="coerce"
                )

                current_orders = current_orders[
                    (current_distance - selected_distance).abs() <= 2.5
                ]

            # استبعاد الطلبات التي لا تحتوي على وقت توصيل
            current_orders = current_orders.dropna(subset=[target])

            # الاحتفاظ بالنتيجة إذا وجدنا خمسة طلبات على الأقل
            if len(current_orders) >= minimum_orders:
                similar_orders = current_orders
                used_stage = stage_name
                break

        # عرض التوقع بناءً على الطلبات التي تم العثور عليها
        if len(similar_orders) > 0:

            # حساب وسيط وقت التوصيل
            estimated_time = similar_orders[target].median()

            st.success(
                f"وقت التوصيل المتوقع: {estimated_time:.1f} دقيقة"
            )

            st.write(
                f"عدد الطلبات المستخدمة في التقدير: "
                f"{len(similar_orders):,}"
            )

            st.write(f"طريقة البحث المستخدمة: {used_stage}")

            st.caption(
                "تم حساب التوقع باستخدام وسيط أوقات الطلبات السابقة "
                "التي تشابه ظروف طلبك حسب مرحلة البحث."
            )

        else:
            # إظهار رسالة إذا لم تتوفر بيانات صالحة
            st.error("تعذر حساب وقت التوصيل بسبب عدم توفر بيانات صالحة.")
