from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "microsoft/phi-3-mini-4k-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="auto"
)

prompt = """You are a financial analyst.
Explain in 3 bullet points why rising interest rates hurt banking stocks."""

inputs = tokenizer(prompt, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    temperature=0.7
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
