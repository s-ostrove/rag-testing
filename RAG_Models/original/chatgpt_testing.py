from datasets import load_dataset
from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizer,
    AutoTokenizer,
    RagRetriever,
    RagSequenceForGeneration
)
import numpy as np
import faiss
import torch
import safetensors
from functools import partial

# Load CSV dataset
csv_path = "/Users/Samuel/Desktop/SAMUEL MacBook/Samuel Yale/Courses/Thesis/Testing/testgraph2.csv"
dataset = load_dataset("csv", data_files=[csv_path], split="train", delimiter=",", column_names=["title", "text"])

# Initialize DPR Context Encoder and Tokenizer
dpr_ctx_encoder_model_name = "facebook/dpr-ctx_encoder-multiset-base"
dpr_tokenizer = DPRContextEncoderTokenizer.from_pretrained(dpr_ctx_encoder_model_name)
dpr_encoder = DPRContextEncoder.from_pretrained(dpr_ctx_encoder_model_name)

# Define embedding function
def testembed(docs: dict, encoder: DPRContextEncoder = dpr_encoder, tokenizer: DPRContextEncoderTokenizer = dpr_tokenizer):
    input_ids = tokenizer(docs['title'], docs['text'], return_tensors='pt')['input_ids']
    embeddings = encoder(input_ids, return_dict = True).pooler_output
    return {'embeddings': embeddings[0]}

from functools import partial

embedded = dataset.map(partial(testembed))

# Initialize FAISS index
index = faiss.IndexHNSWFlat(768, 128, faiss.METRIC_INNER_PRODUCT)
# faiss.normalize_L2(embedded['embeddings'])  # Normalizing embeddings for cosine similarity
embedded.add_faiss_index("embeddings", custom_index=index)

# Set device to CPU
device = torch.device('cpu')

# Load RAG components
rag_variant = "facebook/rag-sequence-base"
tokenizer = AutoTokenizer.from_pretrained(rag_variant)
retriever = RagRetriever.from_pretrained(rag_variant, index_name='custom', indexed_dataset=embedded)
model = RagSequenceForGeneration.from_pretrained(rag_variant, retriever=retriever).to(device)

# Prepare input for generation
query = "Who is Jim?"
input_dict = tokenizer.prepare_seq2seq_batch(query, return_tensors="pt")

# Ensure input_ids are on the correct device
input_ids = input_dict["input_ids"].to(device)

# Generate response
generated = model.generate(input_ids=input_ids, num_return_sequences=1)

output_text = tokenizer.decode(generated[0], skip_special_tokens=True)

print(output_text)