import click

from common import SAMPLES_PATH
from synthesis import synthesize_everything


@click.group()
def cli():
    pass


@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-s', '--schema-translation', type=str, default='english', help='Schema translation to use')
@click.option('-d', '--with-db', is_flag=True, help='Translate databases')
def spider(output_name, schema_translation, with_db):
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
        with_db=with_db
    )
    
    
@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-s', '--schema-translation', type=str, default='english')
@click.option('-d', '--with-db', is_flag=True, help='Translate databases')
def spider_dk(output_name, schema_translation, with_db):
    """Synthesize spider dataset"""
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
        with_db=with_db
    )
    

@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-s', '--schema-translation', type=str, default='english')
@click.option('-d', '--with-db', is_flag=True, help='Translate databases')
def spider_syn(output_name, schema_translation, with_db):
    """Synthesize spider dataset"""
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
        with_db=with_db
    )


if __name__ == "__main__":
    cli()

