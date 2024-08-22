import os
from dotenv import load_dotenv
from django.core.files.uploadedfile import UploadedFile
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import xml.etree.ElementTree as ET

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=510, chunk_overlap=50)
    docs_chunks = text_splitter.split_text(text)
    return docs_chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain():
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt_template = """
    Chỉ trả lời câu hỏi có liên quan có trong các câu được cung cấp, đảm bảo cung cấp đầy đủ chi tiết. Nếu câu trả lời không có trong
    các câu đã cung cấp, chỉ cần nói "Vui lòng cung cấp thêm chi tiết câu hỏi!"\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    qa_chain = load_qa_chain(
        llm=llm,
        chain_type="stuff",
        prompt=prompt
    )
    return qa_chain

def handle_user_input(vectorstore, conversation_chain, user_question):
    docs = vectorstore.similarity_search(user_question)
    response = conversation_chain.invoke({"input_documents": docs, "question": user_question})
    answer = response["output_text"]
    return answer

def answers(user_response, data_root):
    load_dotenv()

    raw_text = '- '.join(data_root)
    docs_chunks = get_text_chunks(raw_text)
    vectorstore = get_vector_store(docs_chunks)
    conversation_chain = get_conversation_chain()
    answer = handle_user_input(vectorstore, conversation_chain, user_response)

    result = {'answer': answer, 'source': '\n- '.join(data_root)}
    print("Kết quả: ", result)
    return result