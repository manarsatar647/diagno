import streamlit as st
from diagno_core import Diagno

st.set_page_config(page_title="SmartDoc – المساعد الطبي الذكي", page_icon="🩺", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
html, body, .stApp, [class*="css"] {font-family: 'Tajawal','Segoe UI',Tahoma,sans-serif !important;}
.stApp {direction: rtl; text-align: right; background: linear-gradient(180deg,#f0faf8 0%,#ffffff 40%);}
#MainMenu, footer {visibility: hidden;}
.block-container {max-width: 780px; padding-top: 1.5rem;}
.hero {background: linear-gradient(135deg,#0f766e,#14b8a6); color:#fff; border-radius:20px;
       padding:28px 24px; text-align:center; box-shadow:0 8px 24px rgba(15,118,110,.25); margin-bottom:16px;}
.hero h1 {color:#fff; margin:0; font-size:2.4rem; font-weight:800;}
.hero p {margin:6px 0 0; font-size:1.05rem; opacity:.95;}
.notice {background:#fff7ed; border:1px solid #fed7aa; color:#9a3412; border-radius:12px;
         padding:12px 16px; font-size:.95rem; margin-bottom:18px;}
.emergency {background:#fef2f2; border:2px solid #ef4444; color:#991b1b; border-radius:14px;
            padding:14px 18px; margin:14px 0; font-weight:500;}
.section {color:#0f766e; font-weight:800; font-size:1.25rem; margin:22px 0 10px;}
.card {background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:18px 20px;
       margin-bottom:14px; box-shadow:0 2px 10px rgba(0,0,0,.05);}
.card.top {border:2px solid #14b8a6; box-shadow:0 4px 16px rgba(20,184,166,.2);}
.card-head {display:flex; align-items:center; gap:12px; margin-bottom:8px;}
.rank {background:#0f766e; color:#fff; width:34px; height:34px; border-radius:50%;
       display:flex; align-items:center; justify-content:center; font-weight:800; flex-shrink:0;}
.card.other .rank {background:#94a3b8;}
.dname {font-size:1.25rem; font-weight:800; color:#0f172a; line-height:1.3;}
.den {font-size:.8rem; color:#64748b; direction:ltr; text-align:right;}
.bar-wrap {background:#e2e8f0; border-radius:99px; height:12px; overflow:hidden; margin:10px 0 4px;}
.bar {height:100%; border-radius:99px; background:linear-gradient(90deg,#14b8a6,#0f766e);}
.card.other .bar {background:linear-gradient(90deg,#94a3b8,#64748b);}
.pct {font-size:.85rem; color:#475569; margin-bottom:8px;}
.desc {color:#334155; line-height:1.8; margin:6px 0 10px;}
.urgent {display:inline-block; background:#fee2e2; color:#b91c1c; border-radius:99px;
         padding:3px 12px; font-size:.85rem; font-weight:700; margin-bottom:8px;}
.tips-title {font-weight:700; color:#0f766e; margin-top:6px;}
.tips {margin:4px 0 0; padding-right:20px; color:#334155; line-height:1.9;}
.chips {display:flex; flex-wrap:wrap; gap:8px;}
.chip {background:#ecfeff; border:1px solid #99f6e4; color:#115e59; border-radius:99px;
       padding:5px 14px; font-size:.92rem;}
.foot {color:#64748b; font-size:.85rem; text-align:center; margin-top:28px; line-height:1.8;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load():
    return Diagno("diagno_model.joblib", "data/content_ar.json")


dg = load()
label = lambda s: dg.sym_ar[s]


def card_html(rank, name, p):
    d = dg.dis[name]
    pct = round(min(max(p, 0.0), 1.0) * 100)
    cls = "top" if rank == 1 else "other"
    urgent = '<div class="urgent">⚠️ قد تتطلب مراجعة عاجلة للطبيب</div>' if d["urgent"] else ""
    tips = "".join(f"<li>{t}</li>" for t in d["precautions"])
    return (f'<div class="card {cls}">'
            f'<div class="card-head"><div class="rank">{rank}</div>'
            f'<div><div class="dname">{d["name_ar"]}</div><div class="den">{name}</div></div></div>'
            f'<div class="bar-wrap"><div class="bar" style="width:{pct}%"></div></div>'
            f'<div class="pct">درجة التطابق: {pct}%</div>'
            f'{urgent}<div class="desc">{d["description"]}</div>'
            f'<div class="tips-title">🛡️ نصائح وقائية أولية</div><ul class="tips">{tips}</ul></div>')


st.markdown('<div class="hero"><h1>🩺 SmartDoc</h1>'
            '<p>المساعد الطبي الذكي للتقييم الأولي</p></div>', unsafe_allow_html=True)
st.markdown('<div class="notice">⚠️ هذا التطبيق للتوعية فقط وليس تشخيصاً طبياً ولا يغني عن مراجعة الطبيب. '
            'في الحالات الطارئة اتصل بالإسعاف أو توجه لأقرب طوارئ.</div>', unsafe_allow_html=True)

st.markdown('<div class="section">1) اختر الأعراض التي تشعر بها</div>', unsafe_allow_html=True)
sel = st.multiselect("ابحث واختر الأعراض (كلما أضفت أعراضاً أكثر صارت النتيجة أدق):",
                     options=sorted(dg.symptoms, key=label), format_func=label, key="sel")

if sel:
    hits = dg.emergency_hits(sel)
    if hits:
        st.markdown('<div class="emergency">🚨 بعض الأعراض المختارة (' + "، ".join(label(h) for h in hits) +
                    ') قد تدل على حالة خطيرة. إذا كانت شديدة أو مفاجئة توجّه لأقرب طوارئ أو اتصل بالإسعاف فوراً '
                    'ولا تعتمد على نتيجة التطبيق.</div>', unsafe_allow_html=True)
    if len(sel) < 3:
        st.info("اختر 3 أعراض على الأقل للحصول على نتيجة أوثق.")

    st.markdown('<div class="section">2) الأمراض المحتملة</div>', unsafe_allow_html=True)
    for i, (name, p) in enumerate(dg.predict(sel, 3), start=1):
        st.markdown(card_html(i, name, p), unsafe_allow_html=True)

    st.markdown('<div class="section">3) هل عندك أعراض أخرى؟</div>', unsafe_allow_html=True)
    st.caption("هذه أعراض تساعد في تضييق التشخيص. أضفها من القائمة أعلاه إذا كنت تشعر بها:")
    chips = "".join(f'<span class="chip">{label(s)}</span>' for s in dg.next_questions(sel, 6))
    st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)
else:
    st.info("اختر عرضاً واحداً على الأقل لتبدأ.")

st.markdown('<div class="foot">النموذج يغطي 41 مرضاً فقط، وقد تظهر نتيجة قريبة لمن يعاني من مرض غير موجود في القائمة.<br>'
            'النتائج تقديرية ومبنية على بيانات تجريبية، ولا تُغني عن الطبيب.</div>', unsafe_allow_html=True)
