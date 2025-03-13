import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_API_KEY"), 
            model_name="llama-3.3-70b-versatile"
        )
        print(f"✅ Using model: {self.llm.model_name}")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### JOB POSTING EXTRACTION:
            Extract **only** job postings from the following text and return a structured JSON output.

            **For each job listing, extract:**
            - `role`: The job title.
            - `experience`: Required years of experience. If missing, infer from the description.
            - `skills`: A list of key skills required for the role.
            - `description`: A **detailed** summary of the job responsibilities.

            **If a field is missing, infer based on the job context.**
            **If no job is found, return an empty JSON list.**
            
            ### TEXT ###
            {page_data}

            ### VALID JSON OUTPUT (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke({"page_data": cleaned_text})

        print("🔍 LLM Raw Response:", res)

        try:
            json_parser = JsonOutputParser()
            parsed_jobs = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")

        print("✅ Parsed Jobs:", parsed_jobs)
        return parsed_jobs if isinstance(parsed_jobs, list) else [parsed_jobs]

    def write_mail(self, job, links):
        """
        Generates a cold email using the extracted job details.
        """
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_description}

            ### INSTRUCTION:
            You are Mohan, a business development executive at AtliQ, an AI & Software Consulting company. 
            Your job is to write a **professional cold email** introducing AtliQ’s services and explaining 
            how AtliQ can help with hiring for this role.

            **Key points to include:**
            - A strong subject line.
            - A **concise and engaging** introduction.
            - How AtliQ can help with hiring for this position.
            - Relevant portfolio links: {link_list}
            - A **clear and professional closing statement**.

            Do **not** include any unnecessary explanations or preamble.
            
            ### OUTPUT EMAIL:
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job), 
            "link_list": links
        })

        return res.content
