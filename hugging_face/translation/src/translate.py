from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from src.test import smart_chunk_text
import sys
import os
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi-v2", src_lang="en_XX")
model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi-v2")

tokenizer_vi2en = AutoTokenizer.from_pretrained("vinai/vinai-translate-vi2en-v2", src_lang="vi_VN")
model_vi2en = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en-v2")

def translate_en2vi(en_text: str) -> str:
    input_ids = tokenizer_en2vi(en_text, return_tensors="pt").input_ids
    output_ids = model_en2vi.generate(
        input_ids,
        decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True
    )
    vi_text = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
    vi_text = " ".join(vi_text)
    return vi_text

def translate_vi2en(vi_text: str) -> str:
    input_ids = tokenizer_vi2en(vi_text, return_tensors="pt").input_ids
    output_ids = model_vi2en.generate(
        input_ids,
        decoder_start_token_id=tokenizer_vi2en.lang_code_to_id["en_XX"],
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True
    )
    en_text = tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
    en_text = " ".join(en_text)
    return en_text

def translate_en2vi_long_text(en_text: str, batch_size: int = 8) -> str:
    chunks = smart_chunk_text(en_text, tokenizer_en2vi)
    translations = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        inputs = tokenizer_en2vi(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=1024,
            early_stopping=True
        )

        outputs = model_en2vi.generate(
            **inputs,
            decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
            num_beams=3  # ↓ giảm beam
        )

        vi_texts = tokenizer_en2vi.batch_decode(
            outputs, skip_special_tokens=True
        )

    # for chunk in chunks:
    #     input_ids = tokenizer_en2vi(chunk, return_tensors="pt").input_ids

    #     with torch.no_grad():
    #         output_ids = model_en2vi.generate(
    #             input_ids,
    #             decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
    #             num_beams=3,
    #             early_stopping=True
    #         )
    #     vi_text = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)[0]
    #     translations.append(vi_text)

    return "\n\n".join(vi_texts)