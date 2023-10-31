import sqlparse
from sqlparse import sql
import spacy
import spacy.cli


nlp = spacy.load("xx_sent_ud_sm")


def tokenize_text(text):
    return [str(token) for token in nlp(text)]


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


def tokenize_sql_statement(root, tokens=None):
    if tokens is None:
        tokens = []

    # Create tokens from elements which we can't divide
    if not hasattr(root, "tokens"):
        token = str(root).strip()
        if token == "":
            pass
        elif str(root.ttype).startswith("Token.Literal.String"):
            tokens.extend(tokenize_text(str(root)))
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
    elif isinstance(root, sql.Identifier) and "." in str(root) and str(root).strip("'\"") == str(root):
        tokens.append(str(root))

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
    return tokenize_text(question)
