"""Console script for bulk_note."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for bulk_note."""
    click.echo("Replace this message by putting your code into "
               "bulk_note.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
