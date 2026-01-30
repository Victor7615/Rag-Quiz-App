import json
from langchain_community.document_loaders import PyPDFLoader, YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def process_resource(file_path=None, youtube_url=None, api_key=None):
    """Ingests PDF or YouTube and returns a VectorStore."""
    
    docs = []
    
    if file_path:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif youtube_url:
        loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=False)
        docs = loader.load()
    
    # 1. Chunking (Critical for RAG)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, # Large chunk size for context-heavy questions
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    # 2. Embedding & Indexing
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    return vectorstore

def generate_quiz(vectorstore, num_questions=5, api_key=None):
    """Generates a quiz from the vector store."""
    
    # Retrieve general context (Top 4 chunks)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # --- FIX IS HERE: Use .invoke() instead of .get_relevant_documents() ---
    docs = retriever.invoke("summary key concepts")
    
    context_text = "\n\n".join([d.page_content for d in docs])
    
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, openai_api_key=api_key)
    
    prompt_template = """
    You are a strict examiner. Generate {num} multiple-choice questions based ONLY on the text below.
    
    TEXT:
    {context}
    
    OUTPUT JSON FORMAT:
    [
        {{
            "question": "Question text...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Why A is correct..."
        }}
    ]
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"num": num_questions, "context": context_text})
    
    try:
        return json.loads(response)
    except:
        return []