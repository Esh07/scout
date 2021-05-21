"""CLI for adding a new evalution term to the database."""
import json
import logging

import click
from flask.cli import with_appcontext

from scout.load import load_evaluation_term
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

VALID_CATEGORIES = ("dismissal_term", "manual_rank")
REQUIRED_FIELDS = ["name", "term_category", "analysis_type", "institute"]


def get_next_rank(term_category):
    """Get next rank value."""
    query = store.evaluation_terms_collection.find({"term_category": term_category})
    latest_term = max(query, key=lambda term: term["rank"])
    return latest_term["rank"] + 1


@click.command("evaluation-term", help="Load a variant evaluation term")
@click.option("-i", "--internal-id", help="Unique id of a term")
@click.option("-n", "--name", required=True, help="Displayed name of a term")
@click.option("-l", "--label", help="Displayed shorthand name of a term [default: same as name]")
@click.option("-d", "--description", help="Verbose description of a term [default: same as name]")
@click.option(
    "-r", "--rank", type=int, help="Rank used for determening the order entries are displayed"
)
@click.option("-e", "--evidence", multiple=True, help="Type of evidence supporting a term")
@click.option(
    "-s", "--institute", default="all", help="Make a term exclusive for a institute [default: all]"
)
@click.option(
    "-c",
    "--term_category",
    type=click.Choice(VALID_CATEGORIES),
    required=True,
    help="Type of evaluation term",
)
@click.option(
    "-a",
    "--analysis_type",
    default="all",
    help="Make a term exclusive for a analysis type [default: all]",
)
@with_appcontext
def evaluation_term(
    internal_id, name, label, description, rank, evidence, institute, term_category, analysis_type
):
    """Create a new evalution term and add it to the database."""
    adapter = store

    # assign users default values to options
    if not internal_id:
        internal_id = name.lower().replace(" ", "-")

    if not label:
        label = name

    if not description:
        description = name

    if not rank:
        rank = get_next_rank(term_category)

    try:
        LOG.info(
            f'adding a new term: "{label}" with category "{term_category}" to institute "{institute}"'
        )
        load_evaluation_term(
            adapter=adapter,
            internal_id=internal_id,
            name=name,
            label=label,
            description=description,
            rank=rank,
            evidence=evidence,
            institute=institute,
            term_category=term_category,
            analysis_type=analysis_type,
        )
    except ValueError as e:
        message = f"{e}, please try to specify another value"
        raise click.UsageError(message)
    except Exception as e:
        LOG.warning(e)
        raise click.Abort()
    else:
        click.secho("✓ Added new term", fg="green")


@click.command("batch-evaluation-term", help="Load a variant evaluation term")
@click.option(
    "-f",
    "--file",
    type=click.File(),
    required=True,
    help="Load a json file with multiple evaluation terms",
)
@with_appcontext
def batch_evaluation_terms(file):
    """Load several evaluation terms from a file into the database.

    The tool expects an json array as input.
    """
    adapter = store
    try:
        LOG.info(f"adding terms from {file}")
        entries = json.load(file)
        # validate terms
        LOG.info("Validate evaluation terms")
        for entry in entries:
            # validate content
            if not all(f in entry for f in REQUIRED_FIELDS):
                raise ValueError(
                    f'Some entries does not contain all required fields; required fields: {", ".join(REQUIRED_FIELDS)}'
                )
            # validate term_category
            if not entry["term_category"] in VALID_CATEGORIES:
                raise ValueError(
                    f'Invalida term_category "{entry["term_category"]}"; valid terms: {", ".join(VALID_CATEGORIES)}'
                )
        # store terms in database
        LOG.info("Store evaluation terms in database")
        for entry in entries:
            # assign default values
            if "internal_id" not in entry:
                entry["internal_id"] = entry["name"].lower().replace(" ", "-")

            if "label" not in entry:
                entry["label"] = entry["name"]

            if "description" not in entry:
                entry["description"] = entry["name"]

            if "rank" not in entry:
                entry["rank"] = get_next_rank(entry["term_category"])
            # load terms
            load_evaluation_term(adapter, **entry)
    except ValueError as e:
        raise click.UsageError(e)
    except Exception as e:
        LOG.warning(e)
        raise click.Abort()
    else:
        click.secho("✓ Added new terms", fg="green")
