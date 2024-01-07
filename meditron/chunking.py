from model import get_token_len
from token_counting import *


class ECDoc:
    inc: list[str]
    exc: list[str]
    template = """Inclusion Criteria
{inclusion}

Exclusion Criteria
{exclusion}
"""

    def __init__(self, inc: list[str], exc: list[str]):
        self.inc = inc
        self.exc = exc

    @property
    def size(self) -> int:
        return get_token_len(str(self))

    def __str__(self) -> list[str]:
        return self.template.format(inclusion=''.join(self.inc).rstrip(),
                                    exclusion=''.join(self.exc).rstrip())

    def split(self):
        inc_len = len(self.inc)
        exc_len = len(self.exc)
        inc_midpoint = inc_len // 2
        exc_midpoint = exc_len // 2
        # Prevent Inclusion section from splitting too small
        if inc_len <= 5:
            inc_chunk_1 = self.inc
            inc_chunk_2 = self.inc
        else:
            inc_chunk_1 = self.inc[:inc_midpoint]
            inc_chunk_2 = self.inc[inc_midpoint:]
        # Prevent Exclusion section from splitting too small
        if exc_len <= 5:
            exc_chunk_1 = self.exc
            exc_chunk_2 = self.exc
        else:
            exc_chunk_1 = self.exc[:exc_midpoint]
            exc_chunk_2 = self.exc[exc_midpoint:]
        doc_chunk_1 = ECDoc(inc=inc_chunk_1, exc=exc_chunk_1)
        doc_chunk_2 = ECDoc(inc=inc_chunk_2, exc=exc_chunk_2)
        return doc_chunk_1, doc_chunk_2


def parse_file(filename: str) -> ECDoc:
    inc = []
    exc = []
    inclusion = True
    with open(filename) as filein:
        for line in filein.readlines():
            if line.strip().startswith('Inclusion Criteria'):
                continue
            elif line.strip().startswith('Exclusion Criteria'):
                inclusion = False
                continue
            elif line == '\n':
                continue
            if inclusion:
                inc.append(line)
            else:
                exc.append(line)
    return ECDoc(inc=inc, exc=exc)


def chunk_ec(doc: ECDoc) -> list[ECDoc]:
    # Not too large
    can_fit = doc.size + AVG_PROMPT_LEN < MAX_W_SIZE - AVG_RES_LEN
    if can_fit:
        return [doc]

    last_pass_chunks = [doc]
    while not can_fit:
        new_chunks = []
        for chunk in last_pass_chunks:
            new_chunks.extend(chunk.split())
        new_chunk_size = max([new_chunk.size for new_chunk in new_chunks])
        can_fit = new_chunk_size + AVG_PROMPT_LEN < MAX_W_SIZE - AVG_RES_LEN
        last_pass_chunks = new_chunks
    return new_chunks