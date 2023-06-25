from pathlib import Path

from rich.console import Console

from paper_summary import ArxivPaper, Summarizer

console = Console()
ID = "2306.07967"


def get_paper(_id) -> ArxivPaper:
    paper = ArxivPaper(_id)
    console.print(f"Processing {paper} ...")
    paper.get_manuscript()
    return paper


def main():
    paper = get_paper(ID)
    paper.save_manuscript()
    console.print(f"Number of characters: {len(paper.main_body())}")
    summarizer = Summarizer(text=paper.main_body())
    summarizer.check_length()
    console.print(f"Number of tokens: {summarizer.tokens_count}")
    console.print(paper.get_header(), style="bold green")
    console.print(summarizer.get_key_points(), style="bold cyan")
    console.print("\nSUMMARY", style="bold reverse blue")
    console.print(summarizer.get_summary(), style="bold blue")


def test_stuff():
    paper = get_paper(ID)
    title = paper.get_title()
    console.print(title, style="bold blue reverse")
    abstract = paper.get_abstract()
    console.print(abstract, style="bold green")
    body = paper.main_body()
    console.print(Summarizer(body).tokens_count, style="bold red")


if __name__ == "__main__":
    main()
