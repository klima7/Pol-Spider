import os
from pathlib import Path

import click

import synthesis
from synthesis import (
    add_calculated_attributes,
    translate_samples,
    create_gold_sql
)
from common import (
    load_table_translations,
    load_column_translations,
    load_json,
    save_json
)


COMPONENTS_DIR_PATH = Path(__file__).parent.parent / 'components'
COMPLETE_DIR_PATH = Path(__file__).parent.parent / 'complete'


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "column_trans_path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "table_trans_path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "output_path",
    type=click.Path(exists=False, dir_okay=False, writable=True),
)
def translate_tables(column_trans_path, table_trans_path, output_path):
    """Translate tables.json according to given mapping"""
    table_trans = load_table_translations(table_trans_path)
    column_trans = load_column_translations(column_trans_path)
    tables = load_json(
        str(Path(__file__).parent / "../components/schema/base/tables.json")
    )
    trans_tables = synthesis.translate_tables(tables, table_trans, column_trans)
    save_json(output_path, trans_tables)


@cli.command()
@click.argument(
    "column_trans_path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "table_trans_path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "tables_path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "samples_path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "output_path",
    type=click.Path(exists=False, dir_okay=False, writable=True),
)
def synthesize_samples(
    column_trans_path, table_trans_path, tables_path, samples_path, output_path
):
    """Add redundant attributes and translate sql schema"""
    table_trans = load_table_translations(table_trans_path)
    column_trans = load_column_translations(column_trans_path)
    tables = load_json(tables_path)
    samples = load_json(samples_path)
    samples = translate_samples(samples, table_trans, column_trans)
    samples = add_calculated_attributes(samples, tables)
    save_json(output_path, samples)


@cli.command()
@click.argument(
    "output_path",
    type=click.Path(exists=False, dir_okay=False, writable=True),
)
@click.argument(
    "samples_paths",
    type=click.Path(exists=True, dir_okay=False),
    nargs=-1
)
def create_gold(output_path, samples_paths):
    """create gold.sql from samples"""
    samples_list = [load_json(path) for path in samples_paths]
    create_gold_sql(samples_list, output_path)
    
    
@cli.group()
def complete():
    """Synthesize complete dataset"""
    pass


@complete.command()
@click.argument( "output_name", type=click.STRING)
@click.pass_context
def spider(ctx, output_name):
    """Synthesize spider dataset"""
    complete_dir_path = COMPLETE_DIR_PATH / output_name
    complete_dir_path.mkdir(exist_ok=False)
    samples_path = COMPONENTS_DIR_PATH / 'samples' / 'spider'
    translations_path = COMPONENTS_DIR_PATH / 'schema' / 'translations'
    
    ctx.invoke(
        translate_tables,
        column_trans_path=str(translations_path / 'columns_pl.json'),
        table_trans_path=str(translations_path / 'tables_pl.json'),
        output_path=str(complete_dir_path / 'tables.json'),
    )
    
    for filename in ['dev.json', 'train_others.json', 'train_spider.json']:
        ctx.invoke(
            synthesize_samples,
            column_trans_path=str(translations_path / 'columns_pl.json'),
            table_trans_path=str(translations_path / 'tables_pl.json'),
            tables_path=str(complete_dir_path / 'tables.json'),
            samples_path=str(samples_path / filename),
            output_path=str(complete_dir_path / filename),
        )
        
    ctx.invoke(
        create_gold,
        output_path=str(complete_dir_path / 'train_gold.sql'),
        samples_paths=[
            str(samples_path / 'train_spider.json'),
            str(samples_path / 'train_others.json'),
        ]
    )
    
    ctx.invoke(
        create_gold,
        output_path=str(complete_dir_path / 'dev_gold.sql'),
        samples_paths=[
            str(samples_path / 'dev.json'),
        ]
    )


if __name__ == "__main__":
    cli()


