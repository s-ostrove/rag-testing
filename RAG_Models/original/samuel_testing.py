import logging
import os
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional

import faiss
import torch
from datasets import Features, Sequence, Value, load_dataset

from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizerFast,
    HfArgumentParser,
    RagRetriever,
    RagSequenceForGeneration,
    RagTokenizer,
)

csv_path = "/Users/Samuel/Desktop/SAMUEL MacBook/Samuel Yale/Courses/Thesis/Testing/claritygraph.csv"
dpr_ctx_encoder_model_name = "facebook/dpr-ctx_encoder-multiset-base"

logger = logging.getLogger(__name__)
torch.set_grad_enabled(False)
device = "cuda" if torch.cuda.is_available() else "cpu"

ctx_encoder = DPRContextEncoder.from_pretrained(dpr_ctx_encoder_model_name).to(device=device)
ctx_tokenizer = DPRContextEncoderTokenizerFast.from_pretrained(dpr_ctx_encoder_model_name)
new_features = Features(
    {"text": Value("string"), "title": Value("string"), "embeddings": Sequence(Value("float32"))}
)  # optional, save as float32 instead of float64 to save space

def embed(documents: dict, ctx_encoder: DPRContextEncoder, ctx_tokenizer: DPRContextEncoderTokenizerFast) -> dict:
    """Compute the DPR embeddings of document passages"""
    input_ids = ctx_tokenizer(
        documents["title"], documents["text"], truncation=True, padding="longest", return_tensors="pt"
    )["input_ids"]
    embeddings = ctx_encoder(input_ids.to(device=device), return_dict=True).pooler_output
    return {"embeddings": embeddings.detach().cpu().numpy()}

logger.info("Step 1 – Load the csv")
dataset = load_dataset(
        "csv", data_files=[csv_path], split="train", delimiter=",", column_names=["title", "text"]
    )

def testembed(title, text):
    input_ids = ctx_tokenizer(title, text, truncation=True, padding='longest', return_tensors='pt', max_length=30)['input_ids']
    return ctx_encoder(input_ids.to(device=device), return_dict=True).pooler_output

testembed('hello', 'this is my daughter')