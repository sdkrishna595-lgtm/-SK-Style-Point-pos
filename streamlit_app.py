import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import qrcode
from io import BytesIO

# ১. পেজ সেটআপ ও প্রফেশনাল ডিজাইন
st.set_page_config(page_title="SK Style Point PRO", layout="wide", page_icon="✂️")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e1e1e; color: white; font-weight: bold; border: 2px solid #d32f2f; }
    .invoice-card { background: white; padding: 40px; border: 1px solid #000; border-radius: 5px; font-family: 'Courier New', monospace; color: black; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_content_html=True)

# ২. সেশন স্টেট (ডাটাবেজ)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'services' not in st.session_state:
    st.session_state.services = {"চুল কাটা": 200, "শেভ": 100, "ফেসিয়াল": 500, "হেয়ার কালার": 1000}
if 'products' not in st.session_state:
    st.session_state.products = {"শ্যাম্পু": [450, 10], "হেয়ার জেল": [250, 5]}
if 'staff' not in st.session_state:
    st.session_state.staff = ["কামাল", "জামাল", "রহিম"]
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=["ID", "তারিখ", "কাস্টমার", "বিবরণ", "স্টাফ", "মোট বিল", "পেইড", "বাকি", "কমিশন"])

# ৩. লগইন গেটওয়ে
if not st.session_state.auth:
    st.title("🔐 SK Style Point - Admin Portal")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        pin = st.text_input("সিকিউরিটি পিন দিন", type="password")
        if st.button("সিস্টেম আনলক করুন"):
            if pin == "1234":
                st.session_state.auth = True
                st.rerun()
            else: st.error("ভুল পিন! সঠিক পিন দিন।")
    st.stop()

# ৪. সাইডবার মেনু
st.sidebar.title("🛠 কন্ট্রোল প্যানেল")
menu = st.sidebar.radio("নেভিগেশন", ["🛒 ক্যাশ মেমো", "📊 সেলস রিপোর্ট", "📦 ইনভেন্টরি ও স্টাফ", "⚙️ সেটিংস ও লগআউট"])

# --- বিভাগ ১: ক্যাশ মেমো ---
if menu == "🛒 ক্যাশ মেমো":
    st.header("📝 নতুন ইনভয়েস তৈরি")
    with st.form("billing_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        c_name = c1.text_input("👤 কাস্টমারের নাম", "Guest")
        c_phone = c2.text_input("📞 ফোন নম্বর")
        selected_staff = st.selectbox("🙋‍♂️ সার্ভিস প্রদানকারী স্টাফ", st.session_state.staff)
        
        col_s, col_p = st.columns(2)
        sel_s = col_s.multiselect("✂️ সার্ভিস বেছে নিন", list(st.session_state.services.keys()))
        sel_p = col_p.multiselect("🧴 প্রোডাক্ট বেছে নিন", list(st.session_state.products.keys()))
        
        c3, c4, c5 = st.columns(3)
        discount = c3.number_input("💰 ডিসকাউন্ট (৳)", min_value=0)
        paid_amt = c4.number_input("💵 নগদ জমা (৳)", min_value=0)
        comm_pct = c5.slider("👨‍🔧 স্টাফ কমিশন (%)", 0, 100, 20)
        
        submit = st.form_submit_button("✅ মেমো জেনারেট করুন")

    if submit:
        s_total = sum(st.session_state.services[s] for s in sel_s)
        p_total = sum(st.session_state.products[p][0] for p in sel_p)
        gross_total = (s_total + p_total) - discount
        due_amt = gross_total - paid_amt
        comm_amt = (s_total * comm_pct) / 100
        
        inv_id = f"SK-{datetime.now().strftime('%y%m%d')}-{len(st.session_state.sales)+1}"
        new_sale = {
            "ID": inv_id, "তারিখ": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            "কাস্টমার": f"{c_name} ({c_phone})", "বিবরণ": f"{len(sel_s)} Ser, {len(sel_p)} Prod",
            "স্টাফ": selected_staff, "মোট বিল": gross_total, "পেইড": paid_amt, "বাকি": due_amt, "কমিশন": comm_amt
        }
        st.session_state.sales = pd.concat([st.session_state.sales, pd.DataFrame([new_sale])], ignore_index=True)
        
        # ডিজিটাল মেমো ডিজাইন
        st.markdown(f"""
        <div class="invoice-card">
            <h2 style="text-align: center; color: #d32f2f; margin-bottom: 5px;">SK STYLE POINT</h2>
            <p style="text-align: center; margin-top: 0; font-size: 14px;">কালীর বাজার, কবির হাট, নোয়াখালী</p>
            <hr>
            <p><b>মেমো নং:</b> {inv_id} | <b>তারিখ:</b> {new_sale['তারিখ']}</p>
            <p><b>কাস্টমার:</b> {c_name} | <b>স্টাফ:</b> {selected_staff}</p>
            <hr>
            <table style="width: 100%;">
                <tr><td>আইটেম সাবটোটাল:</td><td style="text-align: right;">{s_total + p_total} ৳</td></tr>
                <tr><td>ডিসকাউন্ট:</td><td style="text-align: right;">- {discount} ৳</td></tr>
                <tr style="font-size: 18px; font-weight: bold; color: blue;"><td>সর্বমোট বিল:</td><td style="text-align: right;">{gross_total} ৳</td></tr>
                <tr style="font-weight: bold;"><td>নগদ জমা:</td><td style="text-align: right;">{paid_amt} ৳</td></tr>
                <tr style="color: red;"><td>বাকি:</td><td style="text-align: right;">{due_amt} ৳</td></tr>
            </table>
            <hr>
            <p style="font-size: 14px;"><b>বিকাশ (পার্সোনাল): 01872438453</b></p>
            <p style="text-align: center; font-weight: bold; color: green; margin-bottom:0;">ধন্যবাদ, আবার আসবেন!</p>
        </div>
        """, unsafe_content_html=True)
        
        # QR Code তৈরি
        qr_data = f"SK Style Point\nInvoice: {inv_id}\nAmount: {gross_total} TK\nBkash: 01872438453"
        qr = qrcode.make(qr_data)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, width=150, caption="পেমেন্টের জন্য স্ক্যান করুন")
        st.info("💡 টিপস: মেমোটি প্রিন্ট করতে কিবোর্ডে Ctrl+P চাপুন।")

# --- বিভাগ ২: সেলস রিপোর্ট ---
elif menu == "📊 সেলস রিপোর্ট":
    st.header("📈 ব্যবসায়িক হিসাব-নিকাশ")
    df = st.session_state.sales
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("মোট ক্যাশ সংগ্রহ", f"{df['পেইড'].sum()} ৳")
        c2.metric("মোট বাকি", f"{df['বাকি'].sum()} ৳")
        c3.metric("স্টাফ কমিশন", f"{df['কমিশন'].sum()} ৳")
        
        st.subheader("বিক্রয় তালিকা")
        st.dataframe(df, use_container_width=True)
        
        fig = px.bar(df, x="তারিখ", y="মোট বিল", color="স্টাফ", title="দৈনিক বিক্রয় গ্রাফ")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("এখনো কোনো লেনদেন হয়নি।")

# --- বিভাগ ৩: ইনভেন্টরি ও স্টাফ ---
elif menu == "📦 ইনভেন্টরি ও স্টাফ":
    st.subheader("ম্যানেজমেন্ট কন্ট্রোল")
    tab1, tab2, tab3 = st.tabs(["✂️ সার্ভিস", "🧴 প্রোডাক্ট", "👥 স্টাফ"])
    
    with tab1:
        st.write("বর্তমান সার্ভিস ও রেট:", st.session_state.services)
        n_s = st.text_input("নতুন সার্ভিস নাম")
        p_s = st.number_input("সার্ভিস রেট", min_value=0)
        if st.button("সার্ভিস সেভ করুন"):
            st.session_state.services[n_s] = p_s; st.rerun()

    with tab2:
        st.write("বর্তমান প্রোডাক্ট স্টক:", st.session_state.products)
        p_n = st.text_input("প্রোডাক্টের নাম")
        p_p = st.number_input("বিক্রয় মূল্য")
        p_q = st.number_input("স্টক পরিমাণ")
        if st.button("প্রোডাক্ট সেভ করুন"):
            st.session_state.products[p_n] = [p_p, p_q]; st.rerun()

    with tab3:
        st.write("বর্তমান স্টাফগণ:", st.session_state.staff)
        st_n = st.text_input("নতুন স্টাফের নাম")
        if st.button("স্টাফ যোগ করুন"):
            st.session_state.staff.append(st_n); st.rerun()

# --- বিভাগ ৪: সেটিংস ---
elif menu == "⚙️ সেটিংস ও লগআউট":
    st.header("⚙️ সিস্টেম কনফিগারেশন")
    if st.button("🗑️ সব সেলস ডাটা ডিলিট করুন"):
        st.session_state.sales = pd.DataFrame(columns=["ID", "তারিখ", "কাস্টমার", "বিবরণ", "স্টাফ", "মোট বিল", "পেইড", "বাকি", "কমিশন"])
        st.success("সব ডাটা মুছে ফেলা হয়েছে!")
    
    if st.button("🚪 লগআউট (Logout)"):
        st.session_state.auth = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Power by: Gemini AI | SK Style Point v2.5")