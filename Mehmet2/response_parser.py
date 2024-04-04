from itertools import zip_longest

from Mehmet2.logging import logger


class Response:
    raw: str
    source_text: str
    entities: list[str]
    conditions: list[str]
    answer: str

    def __init__(self, text: str) -> None:
        self._parse(text)

    def _parse(self, text: str):
        is_source_text, is_answer = False, False
        source_text = ""
        answers = []
        conditions = []
        is_new_sequence = False
        for line in text.split("\n"):
            line = line.strip(" \t")
            if line.upper().startswith("SOURCE-TEXT"):
                is_source_text, is_answer = True, False
                is_new_sequence = True
                line = (
                    line.removeprefix("SOURCE-TEXT")
                    .removeprefix("source-text")
                    .removeprefix(": ")
                )
            elif line.upper().startswith("ANSWER"):
                is_source_text, is_answer = False, True
                is_new_sequence = True
                line = (
                    line.removeprefix("ANSWER")
                    .removeprefix("answer")
                    .removeprefix(":")
                    .removesuffix(".")
                    .strip(" ")
                )
                if answers:
                    conditions.append("AND")
            else:
                is_new_sequence = False

            if is_source_text:
                # IF source text already exists and this line is a new sequence
                if source_text and is_new_sequence:
                    source_text += "\n" + line
                else:
                    source_text += line + "\n"
            elif is_answer:
                line_len = len(line)
                answer = ""
                condition = ""
                inside_answer = False
                for idx, char in enumerate(line):
                    # Beginning of an answer line
                    if idx == 0:
                        assert (
                            char == "[" or char == "("
                        ), "Answer should start with [[ or ("
                        if char == "(":
                            conditions.append("(")
                    # End of an answer line
                    elif idx == line_len - 1:
                        assert (
                            char == "]" or char == ")"
                        ), "Answer should end with ]] or )"
                        if char == ")":
                            conditions.append(")")
                    # Check if the token is beginning of answer sequence
                    elif char == "[" and line[idx - 1] == "[":
                        inside_answer = True
                        # If a condition exists from the last answer, save it
                        if condition:
                            conditions.append(condition.strip())
                            condition = ""
                    # Check if the token is end of an answer sequence
                    elif char == "]" and line[idx + 1] == "]":
                        inside_answer = False
                        # If it is, save the completed answer
                        answers.append(answer)
                        answer = ""
                    elif inside_answer:
                        answer += char
                    elif char != "[" and char != "]":
                        # If it's not a bos or eos token and it's not an answer, then it must be a condition between answers
                        if char == "(" or char == ")":
                            logger.warning(f"response contains parentheses: {line}")
                        condition += char
        self.raw = text
        self.source_text = source_text.strip()
        self.entities = answers
        self.conditions = conditions
        self.answer = self._rebuild_answer_for_parsing()

    def _rebuild_answer_for_parsing(self):
        answer = ""
        conditions = self.conditions.copy()
        if conditions and conditions[0] == "(":
            answer = conditions.pop(0)

        for entity, condition in zip_longest(self.entities, conditions):
            answer += entity
            if condition:
                answer += " " + condition.upper() + " "
        answer = answer.strip()
        return answer

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
        logger.debug(f"conditions: {','.join(self.conditions)}")
        logger.debug(f"root conditions: {','.join(root_conditions)}")
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
