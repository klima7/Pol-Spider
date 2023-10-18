import os
from pathlib import Path

import click

from synthesis.other import synthesize_everything


COMPONENTS_DIR_PATH = Path(__file__).parent.parent / 'components'
COMPLETE_DIR_PATH = Path(__file__).parent.parent / 'complete'


@click.group()
def cli():
    pass


@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-s', '--schema-translation', type=str, default='english')
def spider(output_name, schema_translation):
    """Synthesize spider dataset"""
    samples_path = Path(__file__).parent.parent / 'components' / 'samples' / 'spider'
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
        schema_translation_name=schema_translation
    )
    
    
@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-s', '--schema-translation', type=str, default='english')
def spider_dk(output_name, schema_translation):
    """Synthesize spider dataset"""
    samples_path = Path(__file__).parent.parent / 'components' / 'samples' / 'spider_dk'
    synthesize_everything(
        output_name=output_name,
        samples_paths=[
            samples_path / 'samples.json',
        ],
        gold_mapping={
            'dev_gold.sql': ['samples.json'],
        },
        schema_translation_name=schema_translation
    )
    

@cli.command()
@click.argument("output_name", type=click.STRING)
@click.option('-s', '--schema-translation', type=str, default='english')
def spider_syn(output_name, schema_translation):
    """Synthesize spider dataset"""
    samples_path = Path(__file__).parent.parent / 'components' / 'samples' / 'spider_syn'
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
        schema_translation_name=schema_translation
    )


if __name__ == "__main__":
    cli()


