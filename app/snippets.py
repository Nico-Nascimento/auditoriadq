"""Snippets no formato do VS Code: leitura, gravação e interpretação dos campos.

Este módulo não depende do Qt, para poder ser testado isoladamente.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------
@dataclass(eq=False)
class Snippet:
    name: str
    prefixes: list[str]
    body: str
    description: str = ""
    extra: dict = field(default_factory=dict)  # chaves desconhecidas (ex.: "scope"), preservadas

    @property
    def prefix_text(self) -> str:
        return ", ".join(self.prefixes)


@dataclass
class Field:
    index: int
    start: int  # posição no texto expandido (caracteres Python)
    end: int
    choices: list[str] | None = None  # ${1|a,b,c|}: opções para escolher na lista


@dataclass
class ParsedBody:
    text: str
    tabstops: list[Field]  # ordem de navegação: $1, $2, ... (o $0 fica de fora)
    final: int | None  # posição do $0, se existir
    all_fields: list[Field]


# ---------------------------------------------------------------------------
# Interpretação do corpo (sintaxe de snippets do VS Code)
# ---------------------------------------------------------------------------
_RE_SIMPLE = re.compile(r"\$(\d+)")
_RE_OPEN = re.compile(r"\$\{(\d+)")


class _Parser:
    def __init__(self, src: str):
        self.s = src
        self.i = 0
        self.out: list[str] = []
        self.length = 0
        self.fields: list[Field] = []

    def emit(self, text: str) -> None:
        self.out.append(text)
        self.length += len(text)

    def parse(self, nested: bool = False) -> bool:
        """Lê até o fim (ou até '}' quando aninhado). Retorna True se achou o '}'."""
        s = self.s
        n = len(s)
        while self.i < n:
            c = s[self.i]
            if c == "\\" and self.i + 1 < n and s[self.i + 1] in "$}\\":
                self.emit(s[self.i + 1])
                self.i += 2
                continue
            if nested and c == "}":
                return True
            if c == "$":
                m = _RE_SIMPLE.match(s, self.i)
                if m:
                    self.fields.append(Field(int(m.group(1)), self.length, self.length))
                    self.i = m.end()
                    continue
                m = _RE_OPEN.match(s, self.i)
                if m:
                    idx = int(m.group(1))
                    j = m.end()
                    nxt = s[j] if j < n else ""
                    if nxt == "}":  # ${1}
                        self.fields.append(Field(idx, self.length, self.length))
                        self.i = j + 1
                        continue
                    if nxt == ":":  # ${1:texto}
                        self.i = j + 1
                        start = self.length
                        if self.parse(nested=True):
                            self.i += 1
                        self.fields.append(Field(idx, start, self.length))
                        continue
                    if nxt == "|":  # ${1|a,b,c|}
                        end = s.find("|}", j + 1)
                        if end != -1:
                            raw = s[j + 1:end]
                            choices = [x.replace("\\,", ",").strip() for x in re.split(r"(?<!\\),", raw)]
                            start = self.length
                            self.emit(choices[0] if choices else "")
                            self.fields.append(Field(idx, start, self.length, choices or None))
                            self.i = end + 2
                            continue
            self.emit(c)
            self.i += 1
        return False


def parse_body(body: str) -> ParsedBody:
    p = _Parser(body)
    p.parse()
    text = "".join(p.out)

    first: dict[int, Field] = {}
    for f in sorted(p.fields, key=lambda f: (f.start, -(f.end - f.start))):
        first.setdefault(f.index, f)

    tabstops = [first[i] for i in sorted(first) if i != 0]
    final = first[0].start if 0 in first else None
    return ParsedBody(text=text, tabstops=tabstops, final=final, all_fields=p.fields)


# ---------------------------------------------------------------------------
# Leitura / gravação de arquivos .json / .code-snippets
# ---------------------------------------------------------------------------
def strip_jsonc(text: str) -> str:
    """Remove comentários // e /* */ e vírgulas finais (o VS Code aceita ambos)."""
    out: list[str] = []
    i = 0
    n = len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if c == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":
                i += 1
                continue
        out.append(c)
        i += 1
    return "".join(out)


def snippets_from_text(text: str) -> list[Snippet]:
    data = json.loads(strip_jsonc(text.lstrip("﻿")))
    if not isinstance(data, dict):
        raise ValueError("O arquivo não está no formato de snippets do VS Code.")
    result: list[Snippet] = []
    for name, entry in data.items():
        if not isinstance(entry, dict) or "body" not in entry:
            continue
        prefix = entry.get("prefix", "")
        if isinstance(prefix, list):
            prefixes = [str(p) for p in prefix]
        else:
            prefixes = [str(prefix)] if prefix != "" else []
        body = entry.get("body", "")
        if isinstance(body, list):
            body = "\n".join(str(b) for b in body)
        description = entry.get("description", "")
        extra = {k: v for k, v in entry.items() if k not in ("prefix", "body", "description")}
        result.append(Snippet(str(name), prefixes, str(body), str(description or ""), extra))
    return result


def load_snippets_file(path: str | Path) -> list[Snippet]:
    return snippets_from_text(Path(path).read_text(encoding="utf-8"))


def snippets_to_text(snippets: list[Snippet]) -> str:
    data: dict[str, dict] = {}
    for s in snippets:
        base = s.name.strip() or (s.prefixes[0] if s.prefixes else "") or "Snippet"
        name = base
        k = 2
        while name in data:
            name = f"{base} ({k})"
            k += 1
        entry: dict = {}
        prefixes = [p for p in s.prefixes if p]
        entry["prefix"] = prefixes[0] if len(prefixes) == 1 else (prefixes or "")
        entry["body"] = s.body.split("\n")
        if s.description:
            entry["description"] = s.description
        for k2, v in s.extra.items():
            entry.setdefault(k2, v)
        data[name] = entry
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def save_snippets_file(path: str | Path, snippets: list[Snippet]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(snippets_to_text(snippets), encoding="utf-8")
    tmp.replace(path)


def parse_prefix_text(text: str) -> list[str]:
    return [p.strip() for p in text.split(",") if p.strip()]


# ---------------------------------------------------------------------------
# Busca por prefixo
# ---------------------------------------------------------------------------
def is_word_char(ch: str) -> bool:
    return bool(ch) and (ch.isalnum() or ch == "_")


def find_matches(snippets: list[Snippet], word: str) -> list[tuple[str, Snippet]]:
    """Snippets cujo prefixo começa com `word` (sem diferenciar maiúsculas)."""
    w = word.casefold()
    if not w:
        return []
    found = [(p, s) for s in snippets for p in s.prefixes if p and p.casefold().startswith(w)]
    found.sort(key=lambda t: (t[0].casefold() != w, t[0].casefold(), t[1].name.casefold()))
    return found


def same_prefix_conflicts(snippets: list[Snippet], target: Snippet) -> dict[str, list[Snippet]]:
    """Para cada prefixo do `target`, outros snippets que usam o mesmo prefixo."""
    result: dict[str, list[Snippet]] = {}
    for p in target.prefixes:
        if not p:
            continue
        others = [s for s in snippets if s is not target and any(q.casefold() == p.casefold() for q in s.prefixes)]
        if others:
            result[p] = others
    return result
