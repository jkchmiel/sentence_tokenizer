import re
from typing import List

PUNCT = "<punct>"
EOS = "<eos>"


class SentenceTokenizer:
    def __init__(self, lower_case_abbreviations: bool = True, acronym_level: int = 4):
        self.abbreviations = Abbreviations(lower_case_abbreviations)
        self._acronym_level = acronym_level

    def tokenize(self, text: str) -> List[str]:
        text = text.replace('\n', ' ')
        text = self.abbreviations.handle(text)
        text = self._handle_acronyms(text)
        text = self._prepare_eos_mapping(text)
        text = text.replace(f"{PUNCT}", ".")
        return self._split(text)

    def _prepare_eos_mapping(self, text: str) -> str:
        text = re.sub("([?!.])([\"'`])", f"\\1\\2{EOS}", text)
        return re.sub("([?!.])[ ]+([A-Z])", f"\\1{EOS}\\2", text)

    def _handle_acronyms(self, text: str) -> str:
        for n in range(2, self._acronym_level + 1):
            text = self._handle_n_acronym(text, n)
        return text

    def _handle_n_acronym(self, text: str, n: int) -> str:
        acronym_pattern = "[.]".join(["([A-Za-z])"] * n) + "[.]"
        acronym_replacement = PUNCT.join([f"\\{i}" for i in range(1, n + 1)]) + PUNCT

        # end of sentence acronyms
        text = re.sub(acronym_pattern + "( [A-Z])", acronym_replacement + f"{EOS}\\{n+1}", text)

        return re.sub(acronym_pattern, acronym_replacement, text)

    @classmethod
    def _split(cls, text) -> List[str]:
        return [sentence.strip() for sentence in text.split(EOS)]


class Abbreviations:
    _abbreviations_file = "abbreviations.txt"

    def __init__(self, lower_case_abbreviations: bool = True):
        self.prefixes = []
        self.suffixes = []
        self.complex = []
        self._read_abbreviations()
        if lower_case_abbreviations:
            self._to_lower()

    def _to_lower(self):
        self.prefixes += [prefix.lower() for prefix in self.prefixes]
        self.suffixes += [suffix.lower() for suffix in self.suffixes]
        self.complex += [c.lower() for c in self.complex]

    def _read_abbreviations(self):
        temp = []
        temp_name = ""
        for line in [line.replace('\n', '') for line in open(self._abbreviations_file).readlines()]:
            if line.startswith('#'):
                temp = []
                temp_name = line.replace('#', '').strip()
            elif line == "":
                setattr(self, temp_name, temp)
            else:
                temp.append(line)

    def _read_file(self, filename):
        return [split_sign.replace('\n', '') for split_sign in open(filename).readlines()]

    def _replace_prefixes(self, text: str) -> str:
        prefixes = f"({'|'.join(self.prefixes)})[.]"
        return re.sub(prefixes, f"\\1{PUNCT}", text)

    def _replace_suffixes(self, text: str) -> str:
        suffixes = f"({'|'.join(self.suffixes)})[.]"
        # end of sentence (assuming tha capital letter is beginning of the sentence
        text = re.sub(suffixes + "( [A-Z])", f"\\1{PUNCT}{EOS}", text)
        return re.sub(suffixes, f"\\1{PUNCT}", text)

    def _replace_complex(self, text: str) -> str:
        for c in self.complex:
            text = re.sub(f"{c} ([A-Z])", f"{c.replace('.', PUNCT)}{EOS}\\1", text)
            text = re.sub(c, c.replace('.', PUNCT), text)

        return text

    def handle(self, text: str) -> str:
        text = self._replace_prefixes(text)
        text = self._replace_suffixes(text)
        return self._replace_complex(text)

