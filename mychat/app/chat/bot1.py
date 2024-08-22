import os
import xml.etree.ElementTree as ET
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .spl import tokenize_words
from sklearn.metrics import jaccard_score
from sklearn.preprocessing import MultiLabelBinarizer

class Document:
    def __init__(self, file_name, sentences):
        self.file_name = file_name
        self.sentences = sentences

def get_sentences_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sentences = [sentence.text.strip() for sentence in root.findall('.//sentence')]
    return sentences

def process_file(file_path):
    sentences = get_sentences_from_xml(file_path)
    return Document(file_name=os.path.basename(file_path), sentences=sentences)

def cosine_response(user_response, database):
    most_similar_sentence = None
    most_similar_value = -1
    corresponding_data = None
    
    for data in database:
        data.sentences.append(user_response)
        
        TfidfVec = TfidfVectorizer(tokenizer=tokenize_words, token_pattern=None)
        tfidf_matrix = TfidfVec.fit_transform(data.sentences)
        
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        
        max_similar_index = similarities[0].argmax()
        max_similar_value = similarities[0][max_similar_index]
        
        if max_similar_value > most_similar_value:
            most_similar_value = max_similar_value
            most_similar_sentence = data.sentences[max_similar_index]
            corresponding_data = data
        
        data.sentences.pop()
    print("Câu trả lời từ cosine_response: ", most_similar_sentence)
    return corresponding_data

def tokenize(text):
    return text.lower().split()

def jaccard_response(question, database):
    question_tokens = tokenize(question)
    mlb = MultiLabelBinarizer()
    best_match_sentences = []

    for data in database:
        for sentence in data.sentences:
            sentence_tokens = tokenize(sentence)
            combined_tokens = [question_tokens, sentence_tokens]
            binary_matrix = mlb.fit_transform(combined_tokens)
            jaccard_index = jaccard_score(binary_matrix[0], binary_matrix[1])
            best_match_sentences.append((sentence, jaccard_index))

    best_match_sentences = sorted(best_match_sentences, key=lambda x: x[1], reverse=True)
    best_match_sentences = [sentence for sentence, _ in best_match_sentences[:5]]

    print("Câu trả lời từ jaccard_response: ", best_match_sentences)
    return best_match_sentences

def response(question, database):
    max_match_count = 0
    best_match_sentences = []
    best_match_file_name = None

    for data in database:
        for sentence in data.sentences:
            match_count = sum(1 for word in question.split() if word.lower() in sentence.lower())
            if match_count > max_match_count:
                max_match_count = match_count
                best_match_sentences = [sentence]
                best_match_file_name = data.file_name
            elif match_count == max_match_count:
                best_match_sentences.append(sentence)

    best_match_sentences = list(set(best_match_sentences))
    best_match_sentences = sorted(best_match_sentences, key=lambda s: sum(1 for word in question.split() if word.lower() in s.lower()), reverse=True)[:10]

    print("10 câu trùng nhiều nhất response: ", best_match_sentences)
    return best_match_sentences

def answers(user_response):
    database_path = Path(__file__).resolve().parent.parent.parent / 'database'
    xml_files = list(database_path.rglob('*.xml'))
    
    database = [process_file(xml_file) for xml_file in xml_files]
    
    answer = response(user_response, database)
    return answer