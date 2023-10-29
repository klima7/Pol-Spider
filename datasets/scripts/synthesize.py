import click

from common import SAMPLES_PATH
from synthesis import synthesize_everything


@click.group()
def cli():
    pass


@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-t', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-q', '--question-lang', type=str, default='pl', help='Question language to use')
@click.option('-s', '--query-lang', type=str, default='pl', help='SQL language to use')
@click.option('--with-db', is_flag=True, help='Translate databases')
def spider(output_name, schema_translation, question_lang, query_lang, with_db):
    """Synthesize spider dataset"""
    samples_path = SAMPLES_PATH / 'spider'
    synthesize_everything(
        output_name=output_name,
        samples_paths=[
            samples_path / 'dev.json',
            samples_path / 'train_others.json',
            samples_path / 'train_spider.json',
        ],
        gold_mapping={
            'dev_gold.sql': ['dev.json'],
            'train_gold.sql': ['train_spider.json', 'train_others.json'],
        },
        schema_translation_name=schema_translation,
        with_db=with_db,
        query_lang=query_lang,
        question_lang=question_lang
    )
    
    
@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-t', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-q', '--question-lang', type=str, default='pl', help='Question language to use')
@click.option('-s', '--query-lang', type=str, default='pl', help='SQL language to use')
@click.option('--with-db', is_flag=True, help='Translate databases')
def spider_dk(output_name, schema_translation, question_lang, query_lang, with_db):
    """Synthesize spider_dk dataset"""
    samples_path = SAMPLES_PATH / 'spider_dk'
    synthesize_everything(
        output_name=output_name,
        samples_paths=[
            samples_path / 'dev.json',
        ],
        gold_mapping={
            'dev_gold.sql': ['dev.json'],
        },
        schema_translation_name=schema_translation,
        with_db=with_db,
        query_lang=query_lang,
        question_lang=question_lang
    )
    

@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-t', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-q', '--question-lang', type=str, default='pl', help='Question language to use')
@click.option('-s', '--query-lang', type=str, default='pl', help='SQL language to use')
@click.option('--with-db', is_flag=True, help='Translate databases')
def spider_syn(output_name, schema_translation, question_lang, query_lang, with_db):
    """Synthesize spider_syn dataset"""
    samples_path = SAMPLES_PATH / 'spider_syn'
    synthesize_everything(
        output_name=output_name,
        samples_paths=[
            samples_path / 'dev.json',
            samples_path / 'train_spider.json',
        ],
        gold_mapping={
            'dev_gold.sql': ['dev.json'],
            'train_gold.sql': ['train_spider.json'],
        },
        schema_translation_name=schema_translation,
        with_db=with_db,
        query_lang=query_lang,
        question_lang=question_lang
    )
    
    
@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-t', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-q', '--question-lang', type=str, default='pl', help='Question language to use')
@click.option('-s', '--query-lang', type=str, default='pl', help='SQL language to use')
@click.option('--with-db', is_flag=True, help='Translate databases')
def sparc_wc(output_name, schema_translation, question_lang, query_lang, with_db):
    """Synthesize sparc_wc dataset"""
    samples_path = SAMPLES_PATH / 'sparc_wc'
    synthesize_everything(
        output_name=output_name,
        samples_paths=[
            samples_path / 'dev.json',
            samples_path / 'train_spider.json',
        ],
        gold_mapping={
            'dev_gold.sql': ['dev.json'],
            'train_gold.sql': ['train_spider.json'],
        },
        schema_translation_name=schema_translation,
        with_db=with_db,
        query_lang=query_lang,
        question_lang=question_lang
    )
    
    
@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-t', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-q', '--question-lang', type=str, default='pl', help='Question language to use')
@click.option('-s', '--query-lang', type=str, default='pl', help='SQL language to use')
@click.option('--with-db', is_flag=True, help='Translate databases')
def cosql_wc(output_name, schema_translation, question_lang, query_lang, with_db):
    """Synthesize cosql_wc dataset"""
    samples_path = SAMPLES_PATH / 'cosql_wc'
    synthesize_everything(
        output_name=output_name,
        samples_paths=[
            samples_path / 'dev.json',
            samples_path / 'train_spider.json',
        ],
        gold_mapping={
            'dev_gold.sql': ['dev.json'],
            'train_gold.sql': ['train_spider.json'],
        },
        schema_translation_name=schema_translation,
        with_db=with_db,
        query_lang=query_lang,
        question_lang=question_lang
    )


if __name__ == "__main__":
    cli()
