import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import re
import random

# 페이지 설정
st.set_page_config(page_title="단어 테스트 생성기", layout="centered")

st.title("📝 나만의 영단어 테스트")

# 사이드바 설정 (API 키 및 옵션)
with st.sidebar:
    st.header("설정")
    default_api_key = "AQ.Ab8RN6JeD7GDknfM9jFK3SNq7eMlc0iKMp8pEAk9NZLgw17wzA"
    api_key = st.text_input("Gemini API Key를 입력하세요", value=default_api_key, type="password")
    show_all = st.checkbox("모든 뜻 보여주기", value=False)
    st.info("API Key는 저장되지 않으며 1회성으로만 사용됩니다.")

# 파일 업로드 (여러 장 지원)
uploaded_files = st.file_uploader("단어장 사진을 업로드하세요 (여러 장 가능)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# 세션 상태 초기화 (단어 목록 저장용)
if "word_list" not in st.session_state:
    st.session_state.word_list = []

def extract_words_from_image(image, api_key):
    genai.configure(api_key=api_key)
    # 요청하신 gemini-3.6-flash 모델 적용
    model = genai.GenerativeModel('gemini-3.6-flash') 
    
    prompt = """
    이 이미지에서 영어 단어와 그에 해당하는 한글 뜻을 모두 추출해줘.
    반드시 아래와 같은 JSON 배열 형식으로만 출력하고, 다른 설명은 절대 추가하지 마.
    
    규칙:
    1. 'word': 영어 단어 (예: borrow)
    2. 'first_meaning': 뜻 중에서 가장 처음 나오는 핵심 뜻 1개만 (예: 빌리다)
    3. 'all_meanings': 책에 적힌 모든 뜻 (예: (다른 사람의 것을) 빌리다, 빌려가다)
    
    형식 예시:
    [
      {"word": "borrow", "first_meaning": "빌리다", "all_meanings": "(다른 사람의 것을) 빌리다, 빌려가다"},
      {"word": "lend", "first_meaning": "빌려주다", "all_meanings": "(다른 사람에게) 빌려주다, 대출하다"}
    ]
    """
    response = model.generate_content([prompt, image])
    
    # 마크다운 기호 제거 및 JSON 파싱
    raw_text = response.text.strip()
    clean_text = re.sub(r'```json|```', '', raw_text).strip()
    
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        st.error("단어를 추출하는 중 오류가 발생했습니다. 사진을 다시 확인해주세요.")
        return []

# '단어장 생성' 버튼
if uploaded_files and api_key:
    if st.button("테스트지 생성하기", type="primary"):
        with st.spinner("단어를 분석하고 있습니다. 잠시만 기다려주세요..."):
            all_extracted_words = []
            for file in uploaded_files:
                img = Image.open(file)
                words = extract_words_from_image(img, api_key)
                all_extracted_words.extend(words)
            
            st.session_state.word_list = all_extracted_words
        st.success("테스트지가 완성되었습니다!")

# 테스트지 출력 영역
if st.session_state.word_list:
    st.divider()
    
    # 헤더와 단어 섞기 버튼을 같은 줄에 배치
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.subheader("💡 단어 테스트")
    with col_btn:
        if st.button("🔀 단어 섞기"):
            random.shuffle(st.session_state.word_list)
            st.rerun() # 화면을 새로고침하여 섞인 결과를 즉시 반영
    
    for i, item in enumerate(st.session_state.word_list):
        # 레이아웃 나누기
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 체크박스 옵션에 따라 보여줄 뜻 결정
            meaning_text = item['all_meanings'] if show_all else item['first_meaning']
            st.markdown(f"**{i+1}.** {meaning_text}")
        
        with col2:
            # Streamlit의 expander를 활용해 정답 숨기기/보기 기능 구현
            with st.expander("정답 보기"):
                st.markdown(f"<h3 style='text-align: center; color: #1E88E5;'>{item['word']}</h3>", unsafe_allow_html=True)
