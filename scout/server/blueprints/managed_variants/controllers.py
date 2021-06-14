import logging
import os.path

from flask_login import current_user

from scout.build import build_managed_variant
from scout.parse.variant.managed_variant import parse_managed_variant_lines
from scout.server.extensions import store
from scout.server.utils import user_institutes

from .forms import (
    CATEGORY_CHOICES,
    SUBCATEGORY_CHOICES,
    ManagedVariantAddForm,
    ManagedVariantModifyForm,
    ManagedVariantsFilterForm,
)

LOG = logging.getLogger(__name__)

VARS_PER_PAGE = 50


def managed_variants(request):
    """Create and return managed variants' data

    Args:
        request(werkzeug.local.LocalProxy): request containing form data

    Returns
        data(dict): data to be displayed in template page
    """

    page = int(request.form.get("page", 1))
    skip_count = VARS_PER_PAGE * max(page - 1, 0)

    # Retrieve form data for the 3 types of form present on the managed variants page
    filters_form = ManagedVariantsFilterForm(request.form)
    add_form = ManagedVariantAddForm()
    modify_form = ManagedVariantModifyForm()

    # Retrieve form data to compose variants query
    categories = request.form.getlist("category") or [cat[0] for cat in CATEGORY_CHOICES]

    query_options = {"sub_category": []}
    for sub_cat in request.form.getlist("sub_category") or [
        subcat[0] for subcat in SUBCATEGORY_CHOICES
    ]:
        query_options["sub_category"].append(sub_cat)

    # Get all variants according to the selected fields in filter form
    managed_variants_query = store.managed_variants(
        category=categories, query_options=query_options
    )

    variant_count = store.count_managed_variants(category=categories, query_options=query_options)
    more_variants = True if variant_count > (skip_count + VARS_PER_PAGE) else False
    managed_variants_res = managed_variants_query.skip(skip_count).limit(VARS_PER_PAGE)

    managed_variants = [managed_variant for managed_variant in managed_variants_res]

    return {
        "page": page,
        "filters_form": filters_form,
        "add_form": add_form,
        "modify_form": modify_form,
        "managed_variants": managed_variants,
        "more_variants": more_variants,
    }


def add_managed_variant(request):
    """Add a managed variant.

    Args:
        request(werkzeug.local.LocalProxy): request containing form data
    """

    add_form = ManagedVariantAddForm(request.form)
    institutes = list(user_institutes(store, current_user))
    current_user_id = current_user._id

    managed_variant_obj = build_managed_variant(
        dict(
            chromosome=add_form["chromosome"].data,
            position=add_form["position"].data,
            end=add_form["end"].data,
            reference=add_form["reference"].data,
            alternative=add_form["alternative"].data,
            institutes=institutes,
            maintainer=[current_user_id],
            category=add_form["category"].data,
            sub_category=add_form["sub_category"].data,
            description=add_form["description"].data,
        )
    )

    return store.upsert_managed_variant(managed_variant_obj)


def upload_managed_variants(store, lines, institutes, current_user_id):
    """Add managed variants from a CSV file"""

    total_variant_lines = 0
    new_managed_variants = 0

    for managed_variant_info in parse_managed_variant_lines(lines):
        total_variant_lines += 1

        managed_variant_info.update({"maintainer": [current_user_id], "institutes": institutes})
        managed_variant_obj = build_managed_variant(managed_variant_info)

        if store.upsert_managed_variant(managed_variant_obj):
            new_managed_variants += 1

    return new_managed_variants, total_variant_lines


def modify_managed_variant(store, managed_variant_id, edit_form):
    """Modify a managed variant."""

    managed_variant = store.find_managed_variant(managed_variant_id)

    if managed_variant is None:
        return

    original_obj_id = managed_variant["_id"]

    managed_variant.update(
        {
            "chromosome": edit_form["chromosome"].data,
            "position": edit_form["position"].data,
            "end": edit_form["end"].data,
            "reference": edit_form["reference"].data,
            "alternative": edit_form["alternative"].data,
            "category": edit_form["category"].data,
            "sub_category": edit_form["sub_category"].data,
            "description": edit_form["description"].data,
        }
    )

    # new ids must be built upon update
    updated_variant = build_managed_variant(managed_variant)

    LOG.debug(
        "Updated variant has mvid %s and old id is %s.",
        updated_variant["managed_variant_id"],
        original_obj_id,
    )

    result = store.upsert_managed_variant(updated_variant, original_obj_id)

    return result


def remove_managed_variant(store, managed_variant_id):
    """Remove a managed variant."""

    removed_variant = store.delete_managed_variant(managed_variant_id)
    return removed_variant
