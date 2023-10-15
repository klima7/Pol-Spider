import click
import json
from pathlib import Path

import synthesis
from synthesis import (
    load_table_translations,
    load_column_translations,
    add_calculated_attributes,
    translate_samples,
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
    tables = _load_json(
        str(Path(__file__).parent / "../components/schema/base/tables.json")
    )
    trans_tables = synthesis.translate_tables(tables, table_trans, column_trans)
    _save_json(output_path, trans_tables)


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
    tables = _load_json(tables_path)
    samples = _load_json(samples_path)
    samples = translate_samples(samples, table_trans, column_trans)
    samples = add_calculated_attributes(samples, tables)
    _save_json(output_path, samples)


@cli.command()
def create_gold():
    """create gold.sql from samples"""
    click.echo("Dropped the database")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, json_obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    cli()
