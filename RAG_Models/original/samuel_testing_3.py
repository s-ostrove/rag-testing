from datasets import load_dataset

csv_path = "/Users/Samuel/Desktop/SAMUEL MacBook/Samuel Yale/Courses/Thesis/Testing/testgraph2.csv"

dataset = load_dataset(
        "csv", data_files=[csv_path], split="train", delimiter=",", column_names=["title", "text"]
    )

from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizer,
)

dpr_ctx_encoder_model_name = "facebook/dpr-ctx_encoder-multiset-base"

dpr_tokenizer = DPRContextEncoderTokenizer.from_pretrained(dpr_ctx_encoder_model_name)
dpr_encoder = DPRContextEncoder.from_pretrained(dpr_ctx_encoder_model_name)

import numpy as np

def testembed(docs: dict, encoder: DPRContextEncoder = dpr_encoder, tokenizer: DPRContextEncoderTokenizer = dpr_tokenizer):
    input_ids = tokenizer(docs['title'], docs['text'], return_tensors='pt')['input_ids']
    embeddings = encoder(input_ids, return_dict = True).pooler_output
    return {'embeddings': embeddings[0]}

from functools import partial

embedded = dataset.map(partial(testembed))

import faiss

index = faiss.IndexHNSWFlat(768, 128, faiss.METRIC_INNER_PRODUCT)
embedded.add_faiss_index("embeddings", custom_index=index)

import torch
device = torch.device('cpu')

from transformers import AutoTokenizer, RagRetriever, RagSequenceForGeneration

tokenizer = AutoTokenizer.from_pretrained("facebook/rag-sequence-base")
retriever = RagRetriever.from_pretrained("facebook/rag-sequence-base", index_name='custom', indexed_dataset=embedded)
model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-base", retriever=retriever).to(device)

input_dict = tokenizer.prepare_seq2seq_batch("how many countries are in europe", return_tensors="pt") 

print(input_dict['input_ids'])

generated = model.generate(input_ids=input_dict["input_ids"])