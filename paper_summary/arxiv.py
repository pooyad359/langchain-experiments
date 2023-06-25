from __future__ import annotations
from urllib.parse import urlparse, ParseResult
import requests
from pypdf import PdfReader
from io import BytesIO
from paper_summary.exceptions import ArxivPaperNotFound, ArxivPaperNotDownloaded, MetadataNotFound
from pathlib import Path
from bs4 import BeautifulSoup


class ArxivPaper:
    def __init__(self, id) -> None:
        self._id: str = id
        self._bytes: bytes | None = None
        self._manuscript: str | None = None
        self._metadata: BeautifulSoup | None = None

    @classmethod
    def from_url(cls, url) -> "ArxivPaper":
        _url: ParseResult = urlparse(url)
        _id: str = _url.path.split("/")[-1]
        return cls(_id)

    @property
    def url(self) -> str:
        return f"https://arxiv.org/abs/{self._id}"

    @property
    def export_url(self) -> str:
        return f"https://export.arxiv.org/pdf/{self._id}"

    def __repr__(self) -> str:
        return f"Arxive(id={repr(self._id)})"

    def _is_valid_url(self) -> bool:
        try:
            response = requests.head(self.url, timeout=20)
        except requests.exceptions.ConnectionError:
            return False
        return response.ok

    def download(self) -> None:
        if not self._is_valid_url():
            raise ArxivPaperNotFound(f"Could not connect to {self.url}")
        response = requests.get(self.export_url, timeout=20)
        if not response.ok:
            raise ArxivPaperNotDownloaded(f"An error occured when downloading.\n{response.text}")
        self._bytes = response.content

    def _get_manuscript(self) -> str:
        if not self._bytes:
            self.download()
        bytes_buffer = BytesIO(self._bytes)  # type: ignore
        reader = PdfReader(bytes_buffer)
        texts = [p.extract_text() for p in reader.pages]
        return "\n".join(texts)

    def get_manuscript(self) -> str:
        if not self._manuscript:
            self._manuscript = self._get_manuscript()
        return self._manuscript

    def _get_metadata(self) -> BeautifulSoup:
        try:
            response = requests.get(self.url, timeout=20)
            if not response.ok:
                raise Exception()
        except Exception:
            raise MetadataNotFound(f"Could not connect to {self.url}")
        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    def get_metadata(self) -> BeautifulSoup:
        if not self._metadata:
            self._metadata = self._get_metadata()
        return self._metadata

    def save_manuscript(self, path: str | Path | None = None) -> None:
        if path is None:
            title = self.get_title()
            path = Path(title).with_suffix(".txt")
        else:
            path = Path(path)
        path.write_text(self.get_manuscript(), encoding="utf-8")

    def get_header(self) -> str:
        try:
            manuscript = self.get_manuscript()
            i = manuscript.lower().index("abstract")
            if i > 500:
                i = manuscript.lower().index("\n")
            header = manuscript[:i]
        except ValueError:
            return ""
        return header

    def get_title(self) -> str:
        metadata = self.get_metadata()
        element = metadata.find("h1", {"class": "title"})
        if not element:
            return self._approx_title()
        title = list(element.children)[-1]
        return title.text.strip()

    def _approx_title(self) -> str:
        return self.get_manuscript().splitlines()[0]

    def get_abstract(self) -> str:
        metadata = self.get_metadata()
        element = metadata.find(class_="abstract")
        if not element:
            return ""
        abstract = list(element.children)[-1]
        return abstract.text.strip()

    def main_body(self) -> str:
        manuscript = self.get_manuscript()
        start = manuscript.lower().find("abstract")
        start = min(0, start)
        end = manuscript.lower().rfind("references", start)
        return manuscript[start:end]
