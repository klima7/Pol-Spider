import click

from common import SAMPLES_PATH
from synthesis import synthesize_dataset


@click.command()
@click.argument("dataset_name", type=click.STRING)
@click.argument("output_name", type=click.STRING)
@click.option('-t', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-q', '--question-lang', type=str, default='pl', help='Question language to use')
@click.option('-s', '--query-lang', type=str, default='pl', help='SQL language to use')
@click.option('--with-db', is_flag=True, help='Translate databases')
def synthesize(dataset_name, output_name, schema_translation, question_lang, query_lang, with_db):
    """Synthesize dataset"""
    synthesize_dataset(
        output_name=output_name,
        dataset_name=dataset_name,
        schema_trans_name=schema_translation,
        with_db=with_db,
        query_lang=query_lang,
        question_lang=question_lang
    )


if __name__ == "__main__":
    synthesize()
