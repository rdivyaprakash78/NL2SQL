
from transformers import DistilBertTokenizer, DistilBertModel
import torch
import numpy as np

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertModel.from_pretrained("distilbert-base-uncased")
def generate_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    embedding = np.array(embedding)
    embedding = embedding.flatten()
    embedding = embedding.tolist()

    return embedding