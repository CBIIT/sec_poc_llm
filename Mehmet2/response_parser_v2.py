import re
from itertools import zip_longest

from Mehmet2.logging import logger


class Response:
    raw: str
    source_text: str
    answer: str
    entities: list[str]
    conditions: list[str]
    entities_by_name: dict[str, list[str]]
    _linestart = re.compile(
        r"^(SOURCE-TEXT|ANSWER|PRIMARY-ORGANS):?", flags=re.I
    )  # Will match a line that starts with "SOURCE-TEXT:" or "ANSWER:"
    _entities = re.compile(
        r"\[\[([\s\S]+?)]]", flags=re.M
    )  # Will match groups of "[[...]]"
    _conditions = re.compile(
        r"(\(\[\[)|(]][\s\S]+?\[\[)|(\]\]\))", flags=re.M
    )  # Will match text between "]]...[[" including leading "(" and trailing ")"
    _expected_entity_fmt = re.compile(
        r"^(SOURCE-TEXT|ANSWER|PRIMARY-ORGANS):?\s*\(?\[\[", flags=re.I
    )  # Inputs with entities should look like: "UPPERCASE: [[<entity>]]"

    def __init__(self, text: str) -> None:
        self.raw = text
        self.source_text = ""
        self.answer = ""
        self.conditions = []
        self.entities = []
        self.entities_by_name = {}
        self._parse(text)
        if not self.answer:
            logger.warning(f"No answer found: {text}")

    def _parse(self, text: str):
        lines = [line.lstrip() for line in text.split("\n")]
        line = self._get_line(lines)
        start_of_seq = self._linestart.match(line or "")
        seq = []
        seq_name = None
        while line is not None:
            if seq and start_of_seq:
                self._capture_sequence(seq_name, seq)
                seq = []
                seq_name = None

            if start_of_seq:
                seq_name = start_of_seq.groups()[0]
                seq.append(line)
            elif seq:
                seq.append(line)
            line = self._get_line(lines)
            start_of_seq = self._linestart.match(line or "")

        if seq:
            self._capture_sequence(seq_name, seq)

    @staticmethod
    def _get_line(lines: list[str]):
        return lines.pop(0) if lines else None

    @staticmethod
    def _extract_from_seq(seq_name: str, seq_text: str):
        if not Response._expected_entity_fmt.match(seq_text):
            logger.warning(f"Input doesn't match expected format: {seq_text}")
            entities, condition_matches = [], []
        else:
            entities = Response._entities.findall(seq_text)
            condition_matches = Response._conditions.findall(seq_text)
        cleaned_conditions = []
        for match in condition_matches:
            for cond in match:
                cond = re.sub(r"[\]\[\s\n]", " ", cond).strip()
                if "(" in cond or ")" in cond:
                    logger.warning(f"Response contains parentheses: {seq_text}")
                if cond:
                    cleaned_conditions.append(cond)
        answer = Response._reconstruct_answer(entities, cleaned_conditions)
        if not answer:
            answer = re.sub(f"^{seq_name}:?\s*", "", seq_text)
        return entities, cleaned_conditions, answer

    @staticmethod
    def _reconstruct_answer(entities: list[str], conditions: list[str]):
        answer = ""
        conditions = conditions.copy()
        if conditions and conditions[0] == "(":
            answer = conditions.pop(0)

        for entity, condition in zip_longest(entities, conditions):
            answer += entity
            if condition:
                answer += f" {condition.upper()} "
        answer = answer.strip()
        return answer

    def _capture_sequence(self, seq_name: str, seq: list[str]):
        entities, conditions, answer = self._extract_from_seq(seq_name, "\n".join(seq))
        if entities:
            if seq_name in self.entities_by_name:
                self.entities_by_name[seq_name].extend(entities)
            else:
                self.entities_by_name[seq_name] = entities.copy()
        if seq_name.lower() == "answer":
            if self.answer:
                # If answer was provided more than once, join them as conjunctive
                self.entities.extend(entities)
                self.conditions.append("AND")
                self.conditions.extend(conditions)
                self.answer = self._reconstruct_answer(self.entities, self.conditions)
            else:
                self.entities = entities.copy()
                self.conditions = conditions.copy()
                self.answer = answer
        elif seq_name.lower() == "source-text":
            # Response may contain more than one source text
            if self.source_text:
                self.source_text += f"\n\n{answer}"
            else:
                self.source_text = answer

    def _get_root_conditions(self):
        if any(("(" in cond for cond in self.conditions)):
            root_conditions = []
            skip_until = None
            for cond in self.conditions:
                if skip_until:
                    if skip_until(cond):
                        skip_until = None
                    else:
                        continue
                if cond == "(":

                    def skip_until(x):
                        return x.startswith(")") or x == ")"

                    continue
                if cond.endswith("("):
                    root_conditions.append(
                        cond.replace("(", "").replace(")", "").strip(" ")
                    )

                    def skip_until(x):
                        return x.startswith(")") or x == ")"

                    continue
                if cond.startswith(")") and cond != ")":
                    root_conditions.append(
                        cond.replace("(", "").replace(")", "").strip(" ")
                    )
                    continue
                if "(" not in cond and ")" not in cond:
                    root_conditions.append(cond)
        else:
            root_conditions = self.conditions
        logger.debug(f"Conditions: {','.join(self.conditions)}")
        logger.debug(f"Root conditions: {','.join(root_conditions)}")
        return root_conditions

    def is_conjunctive(self):
        if not self.conditions:
            return False
        root_conditions = self._get_root_conditions()
        return all((cond.upper() == "AND" for cond in root_conditions))

    def is_disjunctive(self):
        if not self.conditions:
            return False
        root_conditions = self._get_root_conditions()
        return all((cond.upper() == "OR" for cond in root_conditions))

    def split_as_disjunctive(self):
        if not self.answer:
            return []
        entities = self.answer.split(" OR ")
        for idx, e in enumerate(entities):
            entities[idx] = e.removeprefix("(").removesuffix(")").strip(" ")
        return entities

    def is_falsy(self):
        return (
            not self.answer
            or self.answer.lower() == "no"
            or self.answer.lower() == "none"
            or self.answer.lower() == "not specified"
        )


if __name__ == "__main__":
    r = Response("""SOURCE-TEXT:[[lorem ipsum dolor
sepet dumit.]]
PRIMARY-ORG:[[Breast]]
ANSWER: ([[One | cond]] AND [[two]]) OR [[three]]""")
    print(r)
