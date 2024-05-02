###############################################################################
# Designed by Mehmet Kayaalp (c)
# Converted from Perl to Python by Cameron Crouch (c)
# The algorithm takes a clinical cancer term and identifies its corresponding
# NCI Thesarus terms. The NCI Thesaurus term code mapping is found in file
# disease-code.txt. The code to preferred term map is found in code2term.tsv
###############################################################################
import json
import re
from pathlib import Path
from typing import Union

from Mehmet2.logging import logger

# import hashlib

# Files to tokenize
datadir = Path(__file__).parent / "data"
outdir = datadir / "output"
infile = datadir / "disease-code.tsv"
code2preferred_f = datadir / "code2term.tsv"
_testcases_f = datadir / "test-2024-04-11.txt"

# Output files
if not outdir.exists():
    outdir.mkdir()
code2term_outfile = outdir / "code2term.json"
word_outfile = outdir / "word2codes.json"
bigram_outfile = outdir / "bigram2codes.json"
trigram_outfile = outdir / "trigram2codes.json"

# Global mappings
code2term: dict[str, str] = {}
word2code: dict[str, dict[str, int]] = {}
bigram2code: dict[str, dict[str, int]] = {}
trigram2code: dict[str, dict[str, int]] = {}


def _word_split(term: str):
    return re.split(r"[^\w']+", term)


def _word_join(words: list[str]):
    return " ".join(words)


def test():
    cases = []
    _read_test_cases(cases, _testcases_f)
    for term in cases:
        logger.debug(term)
        get_match(term)


def _read_test_cases(aref: list[str], infile: str):
    ifh = open(infile)
    while line := ifh.readline():
        line = line.strip()

        terms = re.split(r"\,\s*", line)
        for term in terms:
            if term:
                aref.append(term)
    ifh.close()


def get_match(term: str):
    words = _word_split(term)
    if len(words) > 13:
        logger.warning("Input term is longer than 13 words. Truncating to 13.")
        logger.info(f"Term before truncation is: '{term}'")
        term = " ".join(words[:13])
        logger.info(f"Term after truncation is: '{term}'")
    assert word2code and bigram2code and trigram2code and code2term
    term = re.sub(
        r"\(\w+\)", "", term
    )  # abbreviations in parentheses may be misleading
    words = []
    bigrams = []
    trigrams = []
    _get_ngrams(term, words, bigrams, trigrams)
    return _get_codes_v2(
        words,
        bigrams,
        trigrams,
        word2code,
        bigram2code,
        trigram2code,
    )


def _get_codes_v2(
    words_aref: list,
    bigrams_aref: list,
    trigrams_aref: list,
    word2code_href: dict,
    bigram2code_href: dict,
    trigram2code_href: dict,
) -> Union[tuple[str, str], None]:
    hrefs: tuple[dict[str, dict[str, int]]] = (
        word2code_href,
        bigram2code_href,
        trigram2code_href,
    )
    arefs: tuple[list[str]] = (
        words_aref,
        bigrams_aref,
        trigrams_aref,
    )

    code2score: dict[str, float] = {}

    for n in range(1, 4):
        if len(words_aref) <= 2 and n != 2:
            continue  # special treatment for two word terms

        aref = arefs[n - 1]
        href = hrefs[n - 1]
        assert len(aref) <= 13, "Cannot calculate terms longer than ~13 words"
        code2count: dict[str, float] = {}

        increment = 1.0

        for ngram in aref:
            codes_href = href.get(ngram, {})
            for code in codes_href.keys():
                if code not in code2count:
                    code2count[code] = 0
                # Count how many times a certain code is seen
                code2count[code] += increment
            for code, count in code2count.items():
                word_count = len(_word_split(code2term[code]))
                word_count = max(n, word_count)
                max_ngram_count = word_count - n + 1
                # Coverage shows which code appears most often with respect to the ngram size
                coverage = count / max_ngram_count
                score = coverage * (n * 2) ** count
                if code not in code2score:
                    code2score[code] = 0
                code2score[code] += score
            increment *= 1.5

    code_scores: list[tuple[str, float]] = []
    for code, score in code2score.items():
        code_scores.append((code, score))

    code_scores.sort(key=lambda cs: cs[1], reverse=True)

    scoremax = 0
    matched_code, matched_term = None, None
    for cs in code_scores:
        code, score = cs

        scoremax = scoremax or score
        if score < scoremax:
            break
        # logger.debug(f"\tC{code}\t{score:.2f}\t{code2term[code]}") # uncomment to debug scoring algorithm
        logger.debug(f"\tC{code}\t{code2term[code]}")
        matched_code = code
        matched_term = code2term[code]
    return ("C" + matched_code, matched_term) if matched_code else None

    ## Uncomment the following to save the scores
    # Create a new SHA-1 hash object
    # hash_object = hashlib.sha1()
    # # Update the hash object with the bytes of the string
    # hash_object.update(" ".join(words_aref).encode())
    # # Get the hexadecimal digest of the hash
    # sha1_hash = hash_object.hexdigest()
    # # uncomment to write scores to file
    # ofh = open(f"scores_{sha1_hash[:5]}_py.tsv", mode="w")
    # ofh.write("Code\tScore\n")
    # for code, score in code_scores:
    #     ofh.write(str(code))
    #     ofh.write(f"\t{score:.2f}\n")
    # ofh.close()


def _get_ngrams(
    term: str,
    words_aref: list[str],
    bigrams_aref: list[list[str]],
    trigrams_aref: list[list[str]],
):
    term = term.lower()

    term = re.sub(r"\bcancer\b", "carcinoma", term)
    words = _word_split(term)
    for word in words:
        if not word:
            continue
        words_aref.append(word)
    bigram = []
    trigram = []
    for word in words_aref:
        # if already proper n-gram, remove the first word
        # so that a new proper n-gram is formed after pushing $word
        if len(bigram) == 2:
            bigram.pop(0)
        if len(trigram) == 3:
            trigram.pop(0)

        bigram.append(word)
        trigram.append(word)

        if len(bigram) == 2:
            bigrams_aref.append(_word_join(bigram))
        if len(trigram) == 3:
            trigrams_aref.append(_word_join(trigram))


def _write_thesaurus_mappings():
    logger.info("Saving parsed thesaurus inputs to JSON files...")
    files = [word_outfile, bigram_outfile, trigram_outfile, code2term_outfile]
    hashes = [word2code, bigram2code, trigram2code, code2term]

    while files:
        file = files.pop(0)
        href = hashes.pop(0)
        logger.info(f"Writing to {file.name}...")
        with open(file, "w") as ofh:
            json.dump(href, ofh, indent=1)


def _read_saved_thesaurus_mappings():
    global code2term, word2code, bigram2code, trigram2code
    if code2term_outfile.exists():
        with open(code2term_outfile) as ifh:
            code2term = json.load(ifh)
    if word_outfile.exists():
        with open(word_outfile) as ifh:
            word2code = json.load(ifh)
    if bigram_outfile.exists():
        with open(bigram_outfile) as ifh:
            bigram2code = json.load(ifh)
    if trigram_outfile.exists():
        with open(trigram_outfile) as ifh:
            trigram2code = json.load(ifh)
    return code2term and word2code and bigram2code and trigram2code


def _read_thesaurus_inputs():
    saved_success = _read_saved_thesaurus_mappings()
    if saved_success:
        logger.info("Using previously parsed thesaurus output files.")
        return

    logger.info(f"Reading NCIt inputs: {infile.name} and {code2preferred_f.name}")
    terms = {}
    ifh = open(infile)
    _ = ifh.readline()
    while line := ifh.readline():
        line = line.strip()
        term, code = line.split("\t")
        code = re.sub(r"^C", "", code)
        term = term.lower()
        if term in terms:
            continue
        terms[term] = 1
        words = _word_split(term)
        bigram = []
        trigram = []

        for word in words:
            if not word:
                continue
            if word not in word2code:
                word2code[word] = {}
            word2code[word][code] = 1

            if len(bigram) == 2:
                bigram.pop(0)
            if len(trigram) == 3:
                trigram.pop(0)

            bigram.append(word)
            trigram.append(word)

            if len(bigram) == 2:
                key = _word_join(bigram)
                if key not in bigram2code:
                    bigram2code[key] = {}
                bigram2code[key][code] = 1
            if len(trigram) == 3:
                key = _word_join(trigram)
                if key not in trigram2code:
                    trigram2code[key] = {}
                trigram2code[key][code] = 1
    ifh.close()

    ifh = open(code2preferred_f)
    _ = ifh.readline()
    while line := ifh.readline():
        line = line.strip()
        line = re.sub(r"^C", "", line)
        code, term = line.split("\t")
        code2term[code] = term
    ifh.close()

    _write_thesaurus_mappings()


_read_thesaurus_inputs()

if __name__ == "__main__":
    # test()
    match = get_match("Non-Small Cell Lung Cancer (NSCLC), stage IIA non-squamous")
    print(match)
