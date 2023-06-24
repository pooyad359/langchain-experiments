import re
import sys
from pathlib import Path

import openai
import tiktoken
from dotenv import load_dotenv
from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.chains.mapreduce import MapReduceChain
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from openai.api_resources import engine
from pqdm.threads import pqdm
from rich.console import Console

load_dotenv()
MODEL_NAME = "gpt-3.5-turbo-16k"
console = Console()
llm = OpenAI(model=MODEL_NAME, temperature=0)
console.print("Using model", llm.model_name, style="bold green")
text_splitter = CharacterTextSplitter()
CHUNK_SIZE = 15800
OVERLAP = 100


def get_document_length(file: Path):
    content = file.read_text()
    # texts = text_splitter.split_text(content)
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    tokens = encoding.encode(content)
    return len(tokens)
    # print("Tokens:", len(tokens))


def split_document(file: Path):
    content = file.read_text()
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    tokens = encoding.encode(content)
    chunks = split_list(tokens, CHUNK_SIZE, OVERLAP)
    texts = [encoding.decode(c) for c in chunks]
    return texts


def split_list(lst, chunk_size, overlap):
    chunks = []
    end_pos = 0
    while end_pos < len(lst):
        start_pos = max(end_pos - overlap, 0)
        end_pos = min(start_pos + chunk_size, len(lst))
        chunk = lst[start_pos:end_pos]
        chunks.append(chunk)
    return chunks


def summarize_text(text: str):
    prompt = (
        "Summarize the following text and give me "
        + "(1) Why is this important, (2) How did they achieve this?,"
        + " (3) What is the novelty of this, (4) What are the key findings."
        + "\nProvide a few bullet points for each."
        + f": \n\n{text}"
    )
    # prompt = "Summarize the following text into four paragraphs (as markdown format)" + f": \n\n{text}"
    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return response


def text_cleaner(text: str):
    # Remove multiple newlines
    return re.sub(r"\n+", "\n", text)


def summarize(file: Path):
    name = file.stem
    output_file = Path(f"{name}_summary2.md")
    texts = split_document(file)
    length = get_document_length(file)
    console.print(f"Document Length: {length}", style="bold green")
    console.print(f"Number of Splits: {len(texts)}", style="bold green")
    responses = pqdm(texts, summarize_text, n_jobs=8)
    summaries = [r["choices"][0]["message"]["content"] for r in responses]
    output_file.write_text("\n\n".join(summaries))


if __name__ == "__main__":
    summarize(Path(sys.argv[1]))
    # print(split_list(list(range(50)), 10, 2))
