import io
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# 1. API Key कॉन्फ़िगरेशन
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 2. प्रोजेक्ट का ज्ञान भंडार
PROJECT_KNOWLEDGE = """
प्रोजेक्ट शीर्षक: पारंपरिक और डिजिटल शिक्षा का संगम (Traditional vs Digital Learning)

आधार 1: Digital + Traditional Learning (मिश्रित शिक्षण)
- पारंपरिक ब्लैकबोर्ड और डिजिटल स्क्रीन/एनिमेशन का संतुलन।
- थ्योरी किताबों से और विज़ुअलाइज़ेशन डिजिटल माध्यम से।

आधार 2: T.L.M (Teaching Learning Material - शिक्षण अधिगम सामग्री)
- हस्तनिर्मित चार्ट, 3D मॉडल, फ्लैशकार्ड और मूर्त सामग्री।
- बच्चे चीज़ों को छूकर और देखकर सीखते हैं।

आधार 3: Low Cost Smart Class (किफायती स्मार्ट क्लासरूम)
- महंगे स्मार्ट बोर्ड की जगह कम कीमत वाले प्रोजेक्टर, टीवी स्क्रीन या पुराने मोबाइल का उपयोग।
- कम बजट वाले ग्रामीण और सरकारी स्कूलों के लिए उपयुक्त।

आधार 4: Inclusive Education (समावेशी शिक्षा)
- सामान्य और विशेष आवश्यकता वाले (दिव्यांग) बच्चों को एक साथ पढ़ाना।
- ऑडियो टूल्स, ब्रेल सामग्री, स्क्रीन रीडर और रैंप जैसी सुविधाएं।

आधार 5: Activity Based Learning (गतिविधि आधारित शिक्षा)
- रटने की जगह 'करके सीखना' (Learning by Doing)।
- रोल-प्ले, पहेलियाँ, विज्ञान प्रयोग और गणितीय खेल।

आधार 6: Eco-Friendly School (पर्यावरण अनुकूल विद्यालय)
- प्लास्टिक-मुक्त परिसर, वेस्ट मटेरियल से टी.एल.एम. बनाना।
- वर्षा जल संचयन (Rainwater harvesting) और पेपरलेस काम।
"""

system_prompt = f"""
तुम 'शिक्षा सेतु AI' हो।
तुम्हारा काम स्कूल प्रोजेक्ट "पारंपरिक और डिजिटल शिक्षा" के 6 आधारों को समझाना है:
{PROJECT_KNOWLEDGE}

नियम:
1. हमेशा सरल, आदरपूर्ण और बोलचाल की हिंदी में उत्तर दो।
2. उत्तर 2 से 3 वाक्यों में संक्षिप्त और स्पष्ट रखो ताकि आवाज़ में सुनने में अच्छा लगे।
3. केवल शिक्षा और इन 6 आधारों से जुड़े सवालों के जवाब दो।
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_prompt
)

# 3. UI लेआउट
st.set_page_config(page_title="शिक्षा सेतु AI (Voice Assistant)", page_icon="🎙️", layout="wide")

with st.sidebar:
    st.header("📌 प्रोजेक्ट के 6 आधार")
    st.markdown("""
    1. **Digital + Traditional Learning**
    2. **T.L.M (Teaching Material)**
    3. **Low Cost Smart Class**
    4. **Inclusive Education**
    5. **Activity Based Learning**
    6. **Eco-Friendly School**
    """)
    st.divider()
    st.info("💡 माइक बटन दबाकर बोलें या नीचे टेक्स्ट बॉक्स में टाइप करें।")

st.title("🎙️ शिक्षा सेतु AI वॉइस असिस्टेंट")
st.caption("पारंपरिक एवं डिजिटल शिक्षा मॉडल के बारे में हिंदी में बोलकर या लिखकर पूछें।")

# चैट हिस्ट्री
if "messages" not in st.session_state:
    st.session_state.messages = []

# पुरानी चैट दिखाना
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

# 4. वॉइस इनपुट बटन
st.write("### 🎤 माइक से सवाल पूछें:")
audio_record = mic_recorder(
    start_prompt="🔴 रिकॉर्डिंग शुरू करें",
    stop_prompt="⏹️ रिकॉर्डिंग रोकें और भेजें",
    key="recorder"
)

# टेक्स्ट इनपुट
text_input = st.chat_input("या यहाँ हिंदी में टाइप करें...")

user_query_text = None
bot_reply = None

# प्रोसेस: ऑडियो या टेक्स्ट इनपुट
if audio_record and audio_record.get("bytes"):
    with st.spinner("आवाज़ समझी जा रही है..."):
        audio_part = {
            "mime_type": "audio/wav",
            "data": audio_record["bytes"]
        }
        prompt_instruction = "इस ऑडियो को ध्यान से सुनो, सवाल समझो और प्रोजेक्ट के नियमों के अनुसार संक्षिप्त हिंदी में उत्तर दो।"
        response = model.generate_content([audio_part, prompt_instruction])
        bot_reply = response.text
        user_query_text = "🎙️ [वॉइस संदेश]"
elif text_input:
    user_query_text = text_input
    with st.spinner("उत्तर तैयार हो रहा है..."):
        response = model.generate_content(text_input)
        bot_reply = response.text

# 5. उत्तर को आवाज़ में बदलना और स्क्रीन पर दिखाना
if bot_reply and user_query_text:
    st.session_state.messages.append({"role": "user", "content": user_query_text})
    with st.chat_message("user"):
        st.write(user_query_text)

    # उत्तर को MP3 ऑडियो में बदलना
    tts = gTTS(text=bot_reply, lang="hi")
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    audio_bytes = audio_fp.read()

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,
        "audio": audio_bytes
    })

    with st.chat_message("assistant"):
        st.write(bot_reply)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
