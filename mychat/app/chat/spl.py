import string
import fitz
import os
import xml.dom.minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
from underthesea import word_tokenize, sent_tokenize
from django.core.files.uploadedfile import UploadedFile
import docx

def process_data2(files):
    text_list = []
    for uploaded_file in files:
        if isinstance(uploaded_file, UploadedFile):
            with uploaded_file.open() as pdf_file:
                pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text = ""
                for page_number in range(len(pdf_document)):
                    page = pdf_document.load_page(page_number)
                    text += page.get_text()
                pdf_document.close()
                text_list.append({'source': uploaded_file.name, 'text': text.replace('\n', ' ')})
    return text_list

def process_data(files):
    text = ""
    for uploaded_file in files:
        if isinstance(uploaded_file, UploadedFile):
            with uploaded_file.open() as pdf_file:
                pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
                for page_number in range(len(pdf_document)):
                    page = pdf_document.load_page(page_number)
                    text += page.get_text()
                pdf_document.close()
    return text.replace('\n', ' ')

def tokenize_sentences(text):
    sentences = sent_tokenize(text)
    return sentences

def tokenize_words(sentence):
    sentence = word_tokenize(sentence)
    sents = [] 
    for sent in sentence:
        sents.append(''.join(sent.lower()))
    words = [word for word in sents if word not in string.punctuation]
    return words

def text_to_xml(text):
    root = Element('document')

    sentences = tokenize_sentences(text)
    for sentence in sentences:
        sentence_element = SubElement(root, 'sentence')
        sentence_element.text = sentence

        words = tokenize_words(sentence)
        for word in words:
            word_element = SubElement(sentence_element, 'word')
            word_element.text = word

    tree = ElementTree(root)
    tree.write(r'data.xml', encoding='utf-8', xml_declaration=True)

    with open(r'data.xml', 'r+', encoding='utf-8') as file:
        xml_string = file.read()
        file.seek(0)
        file.write(xml.dom.minidom.parseString(xml_string).toprettyxml())
        
def text_to_xml(text, file_path):
    root = Element('document')

    sentences = tokenize_sentences(text)
    for sentence in sentences:
        sentence_element = SubElement(root, 'sentence')
        sentence_element.text = sentence

        words = tokenize_words(sentence)
        for word in words:
            word_element = SubElement(sentence_element, 'word')
            word_element.text = word

    tree = ElementTree(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

    with open(file_path, 'r+', encoding='utf-8') as file:
        xml_string = file.read()
        file.seek(0)
        file.write(xml.dom.minidom.parseString(xml_string).toprettyxml())

def get_sentences_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sentences = [sentence.text.strip() for sentence in root.findall('.//sentence')]
    return sentences

def get_words_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    words = []
    for sentence in root.findall('.//sentence'):
        sentence_words = [word.text.strip() for word in sentence.findall('.//word')]
        words.extend(sentence_words)
    return words

def get_xml_files(directory):
    xml_files = []
    for file in os.listdir(directory):
        if file.endswith(".xml"):
            xml_files.append(file)
    return xml_files


def extract_text_from_pdf(pdf_file):
    try:
        document = fitz.open(pdf_file)
        full_text = ""      
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            page_text = page.get_text()
            full_text += page_text
        document.close()
        return full_text.replace('\n', '')
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def extract_text_from_word(file_path):
    doc = docx.Document(file_path)
    return " ".join([para.text for para in doc.paragraphs])