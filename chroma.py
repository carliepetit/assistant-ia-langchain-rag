import warnings
warnings.filterwarnings("ignore")
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import os
import pandas as pd
import chromadb
import uuid
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


class Chroma_db:
    def __init__(self, base_path="data"): 
        self.base_path = base_path
        self.tokenizer, self.model = self.load_model_tk()
        self.collection = self.process_chroma()
    
    def load_model_tk(self):
        # Load tokenizer model from HuggingFace Hub
        tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        return tokenizer, model
    
    def set_embeddings(self, sentences):

        def mean_pooling(model_output, attention_mask):
            token_embeddings = model_output[0] #First element of model_output contains all token embeddings
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        # Tokenize sentences
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform pooling
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings

    def setup_document(self):
        # Importing data and collecting data infos
        category_names = os.listdir(self.base_path)
        category_names = [elem for elem in category_names if len(str(elem).split(".")) == 1]
        category_path = []
        [category_path.append(os.path.join(self.base_path, item)) for item in category_names]

        document = {'id': [],
                    'class': [],
                    'title': [],
                    'content': []
                }
       
        for folder in category_path:
            for unique in os.listdir(folder):
                id = uuid.uuid4().hex[:24] # Generate random id 
                with open(os.path.join(folder, unique), 'r', encoding='utf-8') as file:
                    content = file.read()
                document['id'].append(str(id))
                document['class'].append(folder.split('\\')[1])
                document['title'].append(unique)
                document['content'].append(content)
        return pd.DataFrame(document)

    def process_chroma(self, batch_size=165):
        # Initialization of ChromaDB and adding data 
        chroma_client = chromadb.PersistentClient(path="./chroma_db") 
        collection = chroma_client.get_or_create_collection(name='Articles')

        # Build embeddings once : the first time the script is executed
        if collection.count()==0:
            document = self.setup_document()
            for i in range(0, len(document), batch_size):
                doc_part = document.iloc[i:i+batch_size]
                content_part = doc_part['content'].to_list()
                id_part = doc_part['id'].to_list()
                vector = self.set_embeddings(content_part).tolist()
                collection.add(
                    documents=content_part,
                    ids=id_part,
                    embeddings=vector
                )
        return collection

    def ask_chromadb(self, user_query, nb_context=3):
        # Search with the user question
        query_embedding = self.set_embeddings([user_query]).tolist()

        result = self.collection.query(
            query_embeddings=query_embedding,
            n_results=nb_context,
            #include=["embeddings"]
            )
        
        # Context extraction
        retrieved_docs = result['documents'][0]  
        context = "\n".join(retrieved_docs) if retrieved_docs else "No context found."
        
        # complete prompt
        complete_prompt = [
            {"role": "system", "content": "Tu es un assistant intelligent. Utilise le contexte pour répondre précisément."},
            {"role": "user", "content": f"Contexte : {context}"},
            {"role": "user", "content": f"Question : {user_query}"}
        ]

        return complete_prompt

if __name__ == "__main__":
    # Initialisation
    chroma_instance = Chroma_db()
    
    prompt = chroma_instance.ask_chromadb("Parle-moi de Grand Paris Sud Est Avenir.", nb_context=3)
    print(prompt)