import click
import json

import synthesis
from synthesis import (
    load_table_translations,
    load_column_translations,
    translate_tables,
)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--column",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to column translations path",
)
@click.option(
    "--table",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to tables translations path",
)
@click.option(
    "--output",
    type=click.Path(exists=False, dir_okay=False, writable=True),
    help="Path where save output",
)
def translate_tables(column, table, output):
    """Translate tables.json according to given mapping"""
    table_trans = load_table_translations(table)
    column_trans = load_column_translations(column)
    tables = _load_json("../../components/schema/base/tables.json")
    trans_tables = synthesis.translate_tables(tables, table_trans, column_trans)
    _save_json(output, trans_tables)


@cli.command()
def synthesize_samples():
    """Add redundant attributes and translate sql schema"""
    pass


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
