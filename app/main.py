import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

if "emails_generated" not in st.session_state:
    st.session_state.emails_generated = False

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    url_input = st.text_input("Enter a Job Listing URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")

    if submit_button and not st.session_state.emails_generated:
        try:
            st.session_state.emails_generated = True
            st.write("🔍 Extracting job descriptions...")

            loader = WebBaseLoader([url_input])
            raw_content = loader.load().pop().page_content
            data = clean_text(raw_content)

            # ✅ Debugging: Show extracted content
            print("📝 Extracted Content (First 500 chars):", data[:500])

            portfolio.load_portfolio()  # Ensure correct function call

            jobs = llm.extract_jobs(data)

            if not jobs:
                st.error("❌ No job descriptions extracted. Try a different URL.")
                return

            for job in jobs:
                print("🔍 Extracted Job:", job)  

                skills = job.get("skills", [])

                if not skills:
                    st.warning(f"⚠️ No skills extracted for: {job['role']}")
                    print(f"❌ No skills extracted for: {job['role']}")
                    links = ["No relevant links found."]
                else:
                    print("✅ Skills Extracted:", skills)
                    links = portfolio.query_links(skills)

                email = llm.write_mail(job, links)
                st.code(email, language="markdown")

        except Exception as e:
            st.error(f"❌ An Error Occurred: {e}")
            print("❌ Error Details:", e)

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
