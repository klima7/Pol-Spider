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
    print('Done')


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
    print('Done')


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
    print('Done')


if __name__ == "__main__":
    cli()
