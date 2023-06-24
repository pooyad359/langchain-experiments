import sys
from pathlib import Path

import tiktoken
from dotenv import load_dotenv
from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.chains.mapreduce import MapReduceChain
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from pqdm.threads import pqdm
from rich.console import Console

load_dotenv()
MODEL_NAME = "gpt-3.5-turbo-16k"
console = Console()
llm = OpenAI(model=MODEL_NAME, temperature=0)
console.print("Using model", llm.model_name, style="bold green")
text_splitter = CharacterTextSplitter()


def test_splitter(file: Path):
    content = file.read_text()
    texts = text_splitter.split_text(content)
    print(len(texts))


def main(file: Path):
    content = file.read_text()
    texts = text_splitter.split_text(content)
    docs = [Document(page_content=t) for t in texts]
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    response = chain.run(docs)
    console.print(response, style="bold green")


def summary(file: Path):
    content = file.read_text()
    texts = text_splitter.split_text(content)
    texts = [content]
    template = PromptTemplate(
        input_variables=["text"],
        template="Summarize the following text and give me key points: \n{text}",
    )
    chain = LLMChain(llm=llm, prompt=template)
    responses = pqdm(texts, lambda t: chain.run(text=t), n_jobs=8)
    for response in responses:
        console.print(response, style="blue")
    Path("summary2c.md").write_text("\n".join(responses))
    # docs = [Document(page_content=t) for t in texts]

    # chain = load_summarize_chain(llm, chain_type="map_reduce")
    # response = chain.run(docs)


def get_document_length(file: Path):
    content = file.read_text()
    # texts = text_splitter.split_text(content)
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    tokens = encoding.encode(content)
    print("Tokens:", len(tokens))


if __name__ == "__main__":
    # main(Path(sys.argv[1]))
    # test_splitter(Path(sys.argv[1]))
    get_document_length(Path(sys.argv[1]))
    summary(Path(sys.argv[1]))
