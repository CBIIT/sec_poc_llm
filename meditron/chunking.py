from model import get_token_len
from token_counting import *

DOC_TEMPLATE = """Inclusion Criteria
{inclusion}

Exclusion Criteria
{exclusion}
"""


class ECDoc:
    inc: list[str]
    exc: list[str]
    template = DOC_TEMPLATE

    def __init__(self, inc: list[str], exc: list[str]):
        self.inc = inc
        self.exc = exc

    @property
    def size(self) -> int:
        return get_token_len(str(self))

    def __str__(self) -> list[str]:
        return self.template.format(inclusion=''.join(self.inc).rstrip(),
                                    exclusion=''.join(self.exc).rstrip())

    def split(self, min_criterions_per_section: int = 5):
        """Split a document into 2 new documents halfway between each Inclusion/Exclusion section.

        Keyword arguments:
        min_criterions_per_section -- The minimum number of individual criterions allowed per Inclusion/Exclusion section (default 5).
        """
        inc_len = len(self.inc)
        exc_len = len(self.exc)
        inc_midpoint = inc_len // 2
        exc_midpoint = exc_len // 2
        # Prevent Inclusion section from splitting too small
        if inc_len <= min_criterions_per_section:
            inc_chunk_1 = self.inc
            inc_chunk_2 = self.inc
        else:
            inc_chunk_1 = self.inc[:inc_midpoint]
            inc_chunk_2 = self.inc[inc_midpoint:]
        # Prevent Exclusion section from splitting too small
        if exc_len <= min_criterions_per_section:
            exc_chunk_1 = self.exc
            exc_chunk_2 = self.exc
        else:
            exc_chunk_1 = self.exc[:exc_midpoint]
            exc_chunk_2 = self.exc[exc_midpoint:]
        doc_chunk_1 = ECDoc(inc=inc_chunk_1, exc=exc_chunk_1)
        doc_chunk_2 = ECDoc(inc=inc_chunk_2, exc=exc_chunk_2)
        return doc_chunk_1, doc_chunk_2

    def can_fit(self, target_input_size: float = 0.0):
        if target_input_size > 0:
            # If Input + Example 1-shot < A percentage of the maximum output defined by target_input_size
            return self.size + AVG_PROMPT_LEN <= MAX_W_SIZE * target_input_size
        # If Input + Example 1-shot < Total - Expected Output
        return self.size + AVG_PROMPT_LEN < MAX_W_SIZE - AVG_RES_LEN

    def __eq__(self, other):
        return self.inc == other.inc and self.exc == other.exc


def parse_file(filename: str) -> ECDoc:
    inc = []
    exc = []
    inclusion = True
    with open(filename) as filein:
        for line in filein:
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

def parse_file_with_pipes(filename: str) -> list[str]:
    criterions = []
    with open(filename) as filein:
        contents = filein.read()
    splits = contents.split('|')
    for split in splits:
        split = split.replace('(inclusion--- t)', '')
        split = split.replace('(inclusion--- f)', '')
        split = split.strip()
        criterions.append(split)
    return criterions


def chunk_ec(doc: ECDoc, min_criterions_per_section: int = 5, target_input_size: float = 0.0) -> list[ECDoc]:
    """Chunk an eligibility criteria document until it fits within max_input_size or a size determined by the
    average example lengths.

    Keyword arguments:
    doc -- The EC document.
    min_criterions_per_section -- The minimum number of individual criterions allowed per Inclusion/Exclusion section (default 5).
    target_input_size -- The desired input size as a percentage of the context length (default 0.0). When 0, the value is ignored and instead the average example size is used.
    """
    if doc.can_fit(target_input_size):
        return [doc]

    can_fit = False
    last_pass_chunks = [doc]
    num_splits = 1
    while not can_fit:
        if num_splits > 10:
            raise ValueError('Document attempted to split more than 10 times. Exiting from indefinite loop.')
        new_chunks = []
        for chunk in last_pass_chunks:
            chunk1, chunk2 = chunk.split(min_criterions_per_section)
            # The chunks will only be the same if their parent document could not be split any further.
            # This is influenced by the min_criterions_per_section param.
            if chunk1 == chunk2:
                # import ipdb; ipdb.set_trace()
                raise ValueError('Document has reached smallest possible chunk size. Perhaps you need to adjust the min_criterions_per_section to allow smaller documents.')
            new_chunks.append(chunk1)
            new_chunks.append(chunk2)
        max_chunk = max(new_chunks, key=lambda c: c.size)
        can_fit = max_chunk.can_fit(target_input_size)
        last_pass_chunks = new_chunks
        num_splits += 1
    return new_chunks
