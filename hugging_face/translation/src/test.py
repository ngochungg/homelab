import re

def split_into_sentences(text):
    # Tách câu đơn giản, đủ tốt cho tiếng Anh
    return re.split(r'(?<=[.!?])\s+', text)


def smart_chunk_text(
    text,
    tokenizer,
    max_tokens=900,
    min_sentences=3,
    max_sentences=5
):
    paragraphs = text.split("\n\n")
    chunks = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        sentences = split_into_sentences(para)
        current_chunk = []
        current_tokens = 0

        for sent in sentences:
            sent_tokens = len(tokenizer(sent)["input_ids"])

            # nếu vượt token hoặc đủ 5 câu → chốt chunk
            if (
                current_tokens + sent_tokens > max_tokens
                or len(current_chunk) >= max_sentences
            ):
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0

            current_chunk.append(sent)
            current_tokens += sent_tokens

            # nếu đạt tối thiểu 3 câu & gần max_tokens → chốt sớm
            if (
                len(current_chunk) >= min_sentences
                and current_tokens > max_tokens * 0.8
            ):
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

    return chunks

def translate_batch(chunks, batch_size=8):
    results = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        inputs = tokenizer_en2vi(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        outputs = model_en2vi.generate(
            **inputs,
            decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
            num_beams=3  # ↓ giảm beam
        )

        vi_texts = tokenizer_en2vi.batch_decode(
            outputs, skip_special_tokens=True
        )

        results.extend(vi_texts)

    return results