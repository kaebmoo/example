import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel

# Load pre-trained Multilingual BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
model = BertModel.from_pretrained('bert-base-multilingual-cased')

def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    # Use the embeddings from the [CLS] token
    cls_embedding = outputs.last_hidden_state[:, 0, :].detach().numpy()
    return cls_embedding

# Sample Thai texts
text1 = "การเรียนรู้ของเครื่องคือการวิเคราะห์ข้อมูล."
text2 = "การวิเคราะห์ข้อมูลโดยใช้เทคนิคการเรียนรู้ของเครื่อง."

text1 = "ตะวัน"
text2 = "สุริยา"

# Get BERT embeddings
embedding1 = get_bert_embedding(text1)
embedding2 = get_bert_embedding(text2)

# Compute cosine similarity
similarity = cosine_similarity(embedding1, embedding2)
print(f"Cosine similarity: {similarity[0][0]}")
