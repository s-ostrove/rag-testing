""" from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration

tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="exact", use_dummy_dataset=True)
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)

input_dict = tokenizer.prepare_seq2seq_batch("who holds the record in 100m freestyle", return_tensors="pt") 

generated = model.generate(input_ids=input_dict["input_ids"]) 
print(tokenizer.batch_decode(generated, skip_special_tokens=True)[0])  """

""" from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration

# Load the tokenizers and models
tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
question_encoder_tokenizer = tokenizer.question_encoder
generator_tokenizer = tokenizer.generator

# Initialize the retriever
retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="exact", passages_path="path/to/passages", use_dummy_dataset=True)

# Load the model 
model = RagSequenceForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)

# Example usage
input_ids = question_encoder_tokenizer("Your question here", return_tensors="pt").input_ids
generated_ids = model.generate(input_ids=input_ids)
output = generator_tokenizer.batch_decode(generated_ids, skip_special_tokens=True) """

""" from transformers import AutoTokenizer, RagRetriever, RagModel

tokenizer = AutoTokenizer.from_pretrained("facebook/rag-token-base")
retriever = RagRetriever.from_pretrained("facebook/rag-token-base", index_name='exact', use_dummy_dataset=True)


model = RagModel.from_pretrained("facebook/rag-token-base", retriever=retriever)

inputs = tokenizer("How many people live in Paris?", return_tensors='pt')

outputs = model(input_ids = inputs["input_ids"])

# train on loss """

""" from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration

tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="exact", use_dummy_dataset=True)
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)

input_dict = tokenizer.prepare_seq2seq_batch("who holds the record in 100m freestyle", return_tensors="pt") 

generated = model.generate(input_ids=input_dict["input_ids"]) 
print(tokenizer.batch_decode(generated, skip_special_tokens=True)[0]) """

from transformers import AutoTokenizer, RagRetriever, RagModel, AutoModel
import torch

try:
    # Initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("facebook/rag-token-base")
    print("Tokenizer loaded successfully.")

    # Initialize the retriever with a real or custom dataset if possible
    retriever = RagRetriever.from_pretrained("facebook/rag-token-base", index_name='exact', use_dummy_dataset = True)
    print("Retriever loaded successfully.")

    # Initialize the model
    model = AutoModel.from_pretrained("facebook/rag-token-base", retriever=retriever)
    print("Model loaded successfully.")
    
    # Example input
    query = "How many people live in Paris?"
    inputs = tokenizer(query, return_tensors='pt')
    print(f"Input tokenized: {inputs}")

    # Generate output
    with torch.no_grad():
        outputs = model(input_ids=inputs["input_ids"])
    print(f"Model output: {outputs}")

except Exception as e:
    print(f"An error occurred: {e}")