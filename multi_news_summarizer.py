
import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Setup Gemini API
genai.configure(api_key="AIzaSyCeX8muB03xzKivygj153T72IcXp9h9uZ0")  # Replace with your actual key

generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)


# Function to extract article text from a URL
def extract_article_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = ' '.join(p.get_text() for p in paragraphs if len(p.get_text()) > 50)
        return content[:3000]  # Limit to avoid token overflow
    except Exception as e:
        return f"Error fetching content: {e}"


# Streamlit App
st.set_page_config(page_title="Multi-News Summarizer", layout="centered")
st.title("🗞 Multi-News Summarizer & Fact Extractor")
st.markdown("Paste multiple news article URLs below. This app will summarize and find common insights.")

urls_input = st.text_area("🔗 Enter one URL per line", height=200)
analyze = st.button("🔍 Analyze All Links")

if analyze:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]

    if not urls:
        st.warning("Please enter at least one valid URL.")
    else:
        with st.spinner("Fetching and analyzing articles..."):
            summaries = []
            full_texts = []

            for url in urls:
                article = extract_article_text(url)
                full_texts.append(article)

                try:
                    prompt = f"Summarize the following news article:\n\n{article}\n\nReturn the key points clearly."
                    chat = model.start_chat(history=[])
                    response = chat.send_message(prompt)
                    summaries.append(response.text)
                except Exception as e:
                    summaries.append(f"Error summarizing: {e}")

            # Combine summaries and generate common insight
            combined_prompt = f"""
You are a research assistant. Below are summaries of news articles from multiple sources:

{chr(10).join(f"- {s}" for s in summaries)}

Your tasks:
1. Identify common facts or consistent points across these sources.
2. Highlight any conflicting claims or misinformation if any.
3. Generate a research summary including key trends or insights.

Avoid generic summaries. Be analytical.
"""
            try:
                chat = model.start_chat(history=[])
                overall_response = chat.send_message(combined_prompt)
                st.success("✅ Summary Complete")
                st.subheader("🧩 Combined Summary & Insights")
                st.markdown(overall_response.text)

                with st.expander("📝 Individual Summaries"):
                    for i, summary in enumerate(summaries):
                        st.markdown(f"*Article {i + 1}:*")
                        st.markdown(summary)
                        st.markdown("---")

            except Exception as e:
                st.error(f"Final summary error: {e}")