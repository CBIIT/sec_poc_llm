import subprocess
import time
from pathlib import Path

import pandas as pd
import requests


def load_ncit(version="Thesaurus.FLAT.zip"):
    thesaurusf = Path("ncit_output/Thesaurus.txt")

    if not thesaurusf.exists():
        print(f"Downloading {version} and moving to {thesaurusf}")
        subprocess.run(
            ["curl", "-O", f"https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/{version}"]
        )
        subprocess.run(["unzip", version])
        subprocess.run(["mv", "Thesaurus.txt", thesaurusf])
        subprocess.run(["rm", version])

    ncit = pd.read_csv(thesaurusf, sep="\t", header=None, encoding="utf-8")
    ncit.columns = [
        "code",
        "concept IRI",
        "parents",
        "synonyms",
        "definition",
        "display name",
        "concept status",
        "semantic type",
        "concept in subset",
    ]
    print(ncit.head())
    print(ncit.shape)
    return ncit


def evs_explore(code: str):
    return f"https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/{code}"


class EVSConceptsApi:
    max_codes_per_call = 575
    concepts_syns_endpoint = "https://api-evsrest.nci.nih.gov/api/v1/concept/ncit?list={codes}&include=synonyms"
    concepts_props_endpoint = "https://api-evsrest.nci.nih.gov/api/v1/concept/ncit?list={codes}&include=properties"
    retry_limit = 3

    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    @classmethod
    def get_concepts_list(cls, concept_codes: list[str], endpoint: str):
        chunk_count = 0
        record_count = 0
        print("Fetching from EVS Api")
        for c_codes in cls.chunks(concept_codes, cls.max_codes_per_call):
            record_count += len(c_codes)
            c_codes_string = ",".join(c_codes)
            concept_url_string = endpoint.format(codes=c_codes_string)
            retry_count = 0

            while retry_count < cls.retry_limit:
                try:
                    r = requests.get(concept_url_string, timeout=(1.0, 15.0))
                except requests.exceptions.RequestException as e:
                    print("exception -- ", e)
                    print("sleeping")
                    retry_count += 1
                    if retry_count == cls.retry_limit:
                        print("retry max limit hit -- bailing out ")
                        raise e
                    time.sleep(15)
                else:
                    concept_set = r.json()
                    for newc in concept_set:
                        yield newc

                    chunk_count = chunk_count + 1
                    print(
                        "processed chunk ",
                        chunk_count,
                        " record count = ",
                        record_count,
                    )
                    break

    @classmethod
    def _load_all(
        cls,
        concept_codes: list[str],
        filename: str,
        include_all_syn: bool = False,
    ):
        file = Path(filename)
        if file.exists():
            print(f"Using saved {file}")
            evs_concepts_df = pd.read_csv(file, encoding="utf-8")
        else:
            rows_of_df = []
            desired_sources = ["NCI", "CTRP"]
            desired_types = ["Display_Name", "Preferred_Name"]
            for concept in cls.get_concepts_list(
                concept_codes, endpoint=cls.concepts_syns_endpoint
            ):
                synonyms_df = pd.json_normalize(concept, record_path="synonyms").loc[
                    :, ["name", "source", "type"]
                ]
                if not include_all_syn:
                    # Filter out synonyms that don't meet the desired conditions
                    synonyms_df = synonyms_df[
                        (synonyms_df["source"].isin(desired_sources))
                        | (synonyms_df["type"].isin(desired_types))
                    ]
                synonyms_df = synonyms_df.rename(columns={"name": "synonym"})
                synonyms_df["code"] = concept["code"]
                synonyms_df["name"] = concept["name"]  # Preferred name
                synonyms_df = synonyms_df.drop_duplicates(subset=["synonym"])
                rows_of_df.append(synonyms_df)
            evs_concepts_df = pd.concat(rows_of_df).reset_index(drop=True)
            evs_concepts_df.to_csv(file, index=False, encoding="utf-8")
        return evs_concepts_df

    @classmethod
    def load_pref_terms(cls, concept_codes: list[str], filename: str):
        evs_concepts_df = cls._load_all(concept_codes, filename)
        pref_names_df = (
            evs_concepts_df.loc[:, ["code", "name"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )
        print(pref_names_df.head())
        return pref_names_df

    @classmethod
    def load_terms_w_synonyms(
        cls,
        concept_codes: list[str],
        filename: str,
        include_all_syn: bool = False,
    ):
        evs_concepts_df = cls._load_all(
            concept_codes, filename, include_all_syn=include_all_syn
        )
        print(evs_concepts_df.head())
        return evs_concepts_df

    @classmethod
    def load_props(cls, concept_codes: list[str], filename: str):
        file = Path(filename)
        if file.exists():
            print(f"Using saved {file}")
            props_df = pd.read_csv(file, encoding="utf-8")
        else:
            rows_of_df = []
            # desired_types = ["Legacy Concept Name", "Legacy_Concept_Name"]
            for concept in cls.get_concepts_list(
                concept_codes, endpoint=cls.concepts_props_endpoint
            ):
                props_df = pd.json_normalize(concept, record_path="properties").loc[
                    :, ["type", "value"]
                ]
                props_df["code"] = concept["code"]
                ## Filter out undesired types
                # props_df = props_df[props_df["type"].isin(desired_types)]
                rows_of_df.append(props_df)
            props_df = pd.concat(rows_of_df).reset_index(drop=True)
            props_df.to_csv(file, index=False, encoding="utf-8")
        print(props_df.head())
        return props_df
