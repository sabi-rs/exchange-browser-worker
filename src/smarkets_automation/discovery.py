from dataclasses import dataclass
from html.parser import HTMLParser
import re


@dataclass(frozen=True)
class EventCandidate:
    label: str
    url: str


class _SearchResultsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._current_href: str | None = None
        self._current_label_parts: list[str] = []
        self.results: list[EventCandidate] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        attributes = dict(attrs)
        self._current_href = attributes.get("href")
        self._current_label_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href is None:
            return

        stripped = data.strip()
        if stripped:
            self._current_label_parts.append(stripped)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return

        label = " ".join(self._current_label_parts)
        if label and "-vs-" in self._current_href:
            self.results.append(EventCandidate(label=label, url=self._current_href))

        self._current_href = None
        self._current_label_parts = []


def parse_search_results(html: str) -> list[EventCandidate]:
    parser = _SearchResultsParser()
    parser.feed(html)
    return parser.results


def filter_event_candidates(
    candidates: list[EventCandidate],
    query: str,
) -> list[EventCandidate]:
    query_tokens = re.findall(r"[a-z0-9]+", query.lower())
    if not query_tokens:
        raise ValueError("query must contain at least one search token")

    filtered: list[EventCandidate] = []
    seen_urls: set[str] = set()
    for candidate in candidates:
        label_text = candidate.label.lower()
        if not all(token in label_text for token in query_tokens):
            continue
        if candidate.url in seen_urls:
            continue
        seen_urls.add(candidate.url)
        filtered.append(candidate)

    return filtered
