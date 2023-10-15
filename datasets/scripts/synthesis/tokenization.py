import sqlparse
from sqlparse import sql
import spacy
import spacy.cli


# download spacy model
spacy_model = "pl_core_news_sm"
try:
    nlp_pl = spacy.load(spacy_model)
except Exception:
    spacy.cli.download(spacy_model)
    nlp_pl = spacy.load(spacy_model)


def tokenize_query_no_value(query):
    statement = sqlparse.parse(query)[0]

    value_tokens = [
        token
        for token in statement.flatten()
        if str(token.ttype).startswith("Token.Literal")
    ]
    for token in value_tokens:
        token.value = "value"

    coarse_tokens = [
        str(token).lower() for token in statement.flatten() if str(token).strip() != ""
    ]

    fine_tokens = []
    for token in coarse_tokens:
        if len(token.split(" ")) > 1:
            fine_tokens.extend(token.split(" "))
        elif token == "!=":
            fine_tokens.extend(["!", "="])
        elif token == ">=":
            fine_tokens.extend([">", "="])
        elif token == "<=":
            fine_tokens.extend(["<", "="])
        elif token == ";":
            continue
        else:
            fine_tokens.append(token)
    return fine_tokens


def tokenize_polish_text(text):
    return [str(token) for token in nlp_pl(text)]


def tokenize_sql_statement(root, tokens=None):
    if tokens is None:
        tokens = []

    # Create tokens from elements which we can't divide
    if not hasattr(root, "tokens"):
        token = str(root).strip()
        if token == "" or token == ";":
            pass
        elif len(token.split(" ")) > 1:
            tokens.extend(token.split(" "))
        elif token == "!=":
            tokens.extend(["!", "="])
        elif token == ">=":
            tokens.extend([">", "="])
        elif token == "<=":
            tokens.extend(["<", "="])
        else:
            tokens.append(str(root))

    # Not split identifiers like "T1.name" into separate tokens
    elif isinstance(root, sql.Identifier) and "." in str(root):
        tokens.append(str(root))

    # Tokenize strings using polish tokenizer
    elif (
        isinstance(root, sql.Identifier)
        and len(root.tokens) == 1
        and str(root.tokens[0].ttype) == "Token.Literal.String.Symbol"
    ):
        tokens.extend(tokenize_polish_text(str(root)))

    # Tokenize other compound elements recursively
    else:
        for token in root.tokens:
            tokenize_sql_statement(token, tokens)

    return tokens


def tokenize_query(query):
    statement = sqlparse.parse(query)[0]
    tokens = tokenize_sql_statement(statement)
    return tokens


def tokenize_question(question):
    return tokenize_polish_text(question)
