from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _value(
    item: Any,
    attribute: str,
    default=None,
):
    if isinstance(item, dict):
        return item.get(
            attribute,
            default,
        )

    return getattr(
        item,
        attribute,
        default,
    )


def official_candidate_rank(
    item: Any,
) -> int:
    """
    Read an existing official recruitment rank.

    No rank is calculated or modified here.
    """

    for attribute in (
        "mission_rank",
        "official_rank",
        "rank",
    ):
        value = _value(
            item,
            attribute,
        )

        try:
            rank = int(value or 0)
        except (TypeError, ValueError):
            rank = 0

        if rank > 0:
            return rank

    return 9999


def official_candidate_score(
    item: Any,
) -> float:
    """
    Read an existing official matching score.

    Used only as a deterministic display fallback.
    """

    for attribute in (
        "official_match_score",
        "mission_fit_score",
        "match_score",
        "fit_score",
    ):
        value = _value(
            item,
            attribute,
        )

        if value is None:
            continue

        try:
            return float(value)
        except (TypeError, ValueError):
            continue

    return 0.0


def candidate_display_name(
    item: Any,
) -> str:
    for attribute in (
        "candidate_name",
        "name",
    ):
        value = str(
            _value(
                item,
                attribute,
                "",
            )
            or ""
        ).strip()

        if value:
            return value

    return ""


def candidate_identity(
    item: Any,
) -> str:
    value = str(
        _value(
            item,
            "candidate_id",
            "",
        )
        or ""
    ).strip()

    return (
        value
        or candidate_display_name(item)
    )


def official_candidate_sort_key(
    item: Any,
):
    return (
        official_candidate_rank(item),
        -official_candidate_score(item),
        candidate_display_name(
            item
        ).casefold(),
        candidate_identity(item),
    )


def sort_by_official_rank(
    candidates: Iterable[Any] | None,
) -> list[Any]:
    """
    Sort presentation objects using existing
    official ranks and scores.

    Candidate objects are never modified.
    """

    return sorted(
        list(candidates or []),
        key=official_candidate_sort_key,
    )


def order_candidate_ids(
    candidate_ids: Iterable[str] | None,
    available_ids: Iterable[str] | None,
) -> list[str]:
    """
    Order selected candidate IDs according to
    the canonical available candidate order.
    """

    selected = {
        str(candidate_id or "")
        for candidate_id
        in candidate_ids or []
        if str(candidate_id or "")
    }

    return [
        str(candidate_id)
        for candidate_id
        in available_ids or []
        if str(candidate_id) in selected
    ]
