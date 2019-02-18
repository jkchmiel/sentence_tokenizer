from typing import List

from sentence_tokenizer import SentenceTokenizer


def read_examples(filename) -> List[str]:
    return [split_sign.replace('\n', '') for split_sign in open(filename).readlines()]


def print_examples_sentences(filename: str = "example.txt", output_filename: str = "output.txt"):
    examples = read_examples(filename)

    with open(output_filename, 'w') as f:
        for example in examples:
            sentences = SentenceTokenizer().tokenize(example)

            for sentence in sentences:
                f.write(sentence + "\n")

        f.close()


if __name__ == "__main__":
    print_examples_sentences()
