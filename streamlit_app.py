import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import qrcode
from io import BytesIO

# --- ১. প্রাথমিক কনফিগারেশন ---
st.set_page_config(page_title="SK Style Point PRO", layout="wide")

# সেশন ডাটাবেজ সেটআপ
if 'auth' not in st.session_state: st.session_state.auth = False
if 'services' not in st.session_state:
    st.session_state.services = {"চুল কাটা": 200, "শেভ": 100, "ফেসিয়াল": 500}
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([{"নাম": "শ্যাম্পু", "মূল্য": 450}, {"নাম": "জেল", "মূল্য": 250}])
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=["ID", "তারিখ", "কাস্টমার", "স্টাফ", "মোট", "পেইড", "বাকি"])
if 'staff' not in st.session_state:
    st.session_state.staff = ["কামাল", "জামাল", "রহিম"]

# --- ২. সিকিউরিটি লগইন ---
if not st.session_state.auth:
    st.title("🔐 SK Style Point - Login")
    pin = st.text_input("পিন কোড দিন", type="password")
    if st.button("প্রবেশ করুন"):
        if pin == "1234":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ভুল পিন!")
    st.stop()

# --- ৩. মেইন ইন্টারফেস ---
st.sidebar.title("SK STYLE POINT")
choice = st.sidebar.radio("মেনু", ["🛒 ক্যাশ মেমো", "📊 সেলস রিপোর্ট", "📦 স্টক ও স্টাফ"])

if choice == "🛒 ক্যাশ মেমো":
    st.header("📝 নতুন বিল তৈরি")
    
    with st.form("billing"):
        c_name = st.text_input("কাস্টমারের নাম", "Guest")
        c_staff = st.selectbox("স্টাফ নির্বাচন", st.session_state.staff)
        sel_serv = st.multiselect("সার্ভিস সমূহ", list(st.session_state.services.keys()))
        paid = st.number_input("পেইড এমাউন্ট (৳)", min_value=0)
        submitted = st.form_submit_button("বিল সেভ করুন")
        
    if submitted:
        total = sum(st.session_state.services[s] for s in sel_serv)
        due = total - paid
        inv_id = f"SK-{len(st.session_state.sales)+101}"
        
        # ডাটা সেভ
        new_row = {"ID": inv_id, "তারিখ": datetime.now().strftime("%d-%m-%Y"), "কাস্টমার": c_name, "স্টাফ": c_staff, "মোট": total, "পেইড": paid, "বাকি": due}
        st.session_state.sales = pd.concat([st.session_state.sales, pd.DataFrame([new_row])], ignore_index=True)
        
        # ডিজিটাল রশিদের সহজ ডিজাইন (এরর এড়াতে সহজ করা হয়েছে)
        st.success("বিল সফলভাবে সেভ হয়েছে!")
        st.write("---")
        st.markdown(f"### SK STYLE POINT")
        st.write("কালীর বাজার, কবির হাট, নোয়াখালী")
        st.write(f"**মেমো নং:** {inv_id} | **তারিখ:** {new_row['তারিখ']}")
        st.write(f"**কাস্টমার:** {c_name} | **স্টাফ:** {c_staff}")
        st.write(f"**মোট বিল:** {total} ৳")
        st.write(f"**জমা:** {paid} ৳ | **বাকি:** {due} ৳")
        st.write("**বিকাশ:** 01872438453")
        st.write("---")
        
        # QR Code
        qr_img = qrcode.make(f"SK-Style-{inv_id}-{total}TK")
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        st.image(buf, width=120, caption="Scan for Info")
        st.write("ধন্যবাদ, আবার আসবেন!")

elif choice == "📊 সেলস রিপোর্ট":
    st.header("📈 বিক্রয় রিপোর্ট")
    st.dataframe(st.session_state.sales, use_container_width=True)
    if not st.session_state.sales.empty:
        st.write(f"**মোট ক্যাশ সংগ্রহ:** {st.session_state.sales['পেইড'].sum()} ৳")

elif choice == "📦 স্টক ও স্টাফ":
    st.subheader("ম্যানেজমেন্ট")
    st.write("সার্ভিস লিস্ট:", st.session_state.services)
    st.write("স্টাফ লিস্ট:", st.session_state.staff)
    if st.button("লগআউট"):
        st.session_state.auth = False
        st.rerun()
