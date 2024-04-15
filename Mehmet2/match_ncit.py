###############################################################################
# Designed by Mehmet Kayaalp (c)
# Converted from Perl to Python by Cameron Crouch (c)
# The algorithm takes a clinical cancer term and identifies its corresponding
# NCI Thesarus terms. The NCI Thesaurus term code mapping is found in file
# disease-code.txt. The code to preferred term map is found in code2term.tsv
###############################################################################
import re
# import hashlib

workdir = "/usr/src/app"
infile = workdir + "/disease-code.tsv"
code2preferred_f = workdir + "/code2term.tsv"
testcases_f = workdir + "/test-2024-04-11.txt"

code2term: dict[str, str] = {}
word2code: dict[str, dict[str, int]] = {}
bigram2code: dict[str, dict[str, int]] = {}
trigram2code: dict[str, dict[str, int]] = {}


def test():
    cases = []

    read_cases(cases, testcases_f)
    for term in cases:
        print(term)
        term = re.sub(
            r"\(\w+\)", "", term
        )  # abbreviations in parentheses may be misleading
        words = []
        bigrams = []
        trigrams = []
        get_ngrams(term, words, bigrams, trigrams)
        get_codes_v2(
            words,
            bigrams,
            trigrams,
            word2code,
            bigram2code,
            trigram2code,
        )


def get_codes_v2(
    words_aref: list,
    bigrams_aref: list,
    trigrams_aref: list,
    word2code_href: dict,
    bigram2code_href: dict,
    trigram2code_href: dict,
):
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

    code2score = {}

    for n in range(1, 4):
        if len(words_aref) <= 2 and n != 2:
            continue  # special treatment for two word terms

        aref = arefs[n - 1]
        href = hrefs[n - 1]
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
                word_count = len(re.split(r"[^\w\']+", code2term[code]))
                word_count = max(n, word_count)
                max_ngram_count = word_count - n + 1
                # Coverage shows which code appears most often with respect to the ngram size
                coverage = count / max_ngram_count
                score = coverage * (n * 2) ** count
                if code not in code2score:
                    code2score[code] = 0
                code2score[code] += score
            increment *= 1.5

    code_scores = []
    for code, score in code2score.items():
        code_scores.append((code, score))

    code_scores.sort(key=lambda cs: cs[1], reverse=True)

    scoremax = 0
    for cs in code_scores:
        code, score = cs

        scoremax = scoremax or score
        if score < scoremax:
            break
        print(f"\tC{code}\t", end="")

        # print(f"{score:.2f}\t", end="")  # uncomment to debug scoring algorithm
        print(code2term[code])
    print()

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


def get_ngrams(
    term: str,
    words_aref: list[str],
    bigrams_aref: list[list[str]],
    trigrams_aref: list[list[str]],
):
    term = term.lower()

    term = re.sub(r"\bcancer\b", "carcinoma", term)
    words = re.split(r"[^\w\']+", term)
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
            bigrams_aref.append(tuple(bigram))
        if len(trigram) == 3:
            trigrams_aref.append(tuple(trigram))


def read_cases(aref: list[str], infile: str):
    ifh = open(infile)
    while line := ifh.readline():
        line = line.strip()

        terms = re.split(r"\,\s*", line)
        for term in terms:
            if term:
                aref.append(term)
    ifh.close()


def write_data():
    word_outfile = workdir + "/word2codes_py.tsv"
    bigram_outfile = workdir + "/bigram2codes_py.tsv"
    trigram_outfile = workdir + "/trigram2codes_py.tsv"
    files = [word_outfile, bigram_outfile, trigram_outfile]
    hashes = [word2code, bigram2code, trigram2code]

    while files:
        file = files.pop(0)
        href = hashes.pop(0)
        print(f"Writing into {file}...")
        printout(file, href)


def printout(outfile: str, href0: dict[str, dict[str, int]]):
    ofh = open(outfile, mode="w")
    for term, href in href0.items():
        ofh.write(term if isinstance(term, str) else " ".join(term))
        codes = [int(key) for key in href.keys()]
        codes.sort()
        for code in codes:
            ofh.write(f"\t{code}")
        ofh.write("\n")
    ofh.close()


def read_input():
    print("Reading input...")
    terms = {}
    ifh = open(infile)
    _ = ifh.readline()
    while line := ifh.readline():
        line = line.strip()
        term, code = re.split(r"\t", line)
        code = re.sub(r"^C", "", code)
        term = term.lower()
        if term in terms:
            continue
        terms[term] = 1
        words = re.split(r"[^\w\']+", term)
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
                bigram_t = tuple(bigram)
                if bigram_t not in bigram2code:
                    bigram2code[bigram_t] = {}
                bigram2code[bigram_t][code] = 1
            if len(trigram) == 3:
                trigram_t = tuple(trigram)
                if trigram_t not in trigram2code:
                    trigram2code[trigram_t] = {}
                trigram2code[trigram_t][code] = 1
    ifh.close()

    ifh = open(code2preferred_f)
    _ = ifh.readline()
    while line := ifh.readline():
        line = line.strip()
        line = re.sub(r"^C", "", line)
        code, term = re.split(r"\t", line)
        code2term[code] = term
    ifh.close()


read_input()
write_data()  # uncomment if keeping a record of data is needed
test()
