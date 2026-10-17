#!/usr/bin/env python3
"""Validate a tea-drink campaign brief and build a structured image prompt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_MODES = {"publish-ready", "concept", "style-spec", "series-template", "channel-adaptation"}
VALID_ROLES = {"STYLE_REF", "PRODUCT_ASSET", "BRAND_ASSET", "INGREDIENT_REF", "COPY_SHEET"}


def load_brief(source: str) -> dict[str, Any]:
    if source == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(source).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("brief root must be a JSON object")
    return data


def text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be an array of strings")
        return []
    return [item.strip() for item in value if item.strip()]


def asset_roles(brief: dict[str, Any], errors: list[str]) -> list[dict[str, Any]]:
    assets = brief.get("assets", [])
    if not isinstance(assets, list):
        errors.append("assets must be an array")
        return []
    normalized: list[dict[str, Any]] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"assets[{index}] must be an object")
            continue
        label = text(asset.get("label"))
        raw_roles = asset.get("roles", asset.get("role", []))
        if isinstance(raw_roles, str):
            roles = [raw_roles.strip().upper()] if raw_roles.strip() else []
        elif isinstance(raw_roles, list) and all(isinstance(role, str) for role in raw_roles):
            roles = [role.strip().upper() for role in raw_roles if role.strip()]
        else:
            roles = []
            errors.append(f"assets[{index}].roles must be an array of strings")
        if not label:
            errors.append(f"assets[{index}].label is required")
        invalid_roles = [role for role in roles if role not in VALID_ROLES]
        if not roles:
            errors.append(f"assets[{index}].roles must include at least one role")
        if invalid_roles:
            errors.append(f"assets[{index}].roles contains invalid roles: {invalid_roles}")
        valid_roles = list(dict.fromkeys(role for role in roles if role in VALID_ROLES))
        if label and valid_roles:
            normalized.append({"label": label, "roles": valid_roles, "notes": text(asset.get("notes"))})
    labels = [item["label"] for item in normalized]
    if len(labels) != len(set(labels)):
        errors.append("asset labels must be unique")
    return normalized


def validate(brief: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    mode = text(brief.get("mode")) or "publish-ready"
    if mode not in VALID_MODES:
        errors.append(f"mode must be one of {sorted(VALID_MODES)}")

    assets = asset_roles(brief, errors)
    roles = {role for item in assets for role in item["roles"]}
    product_name = text(brief.get("product_name"))
    product_description = text(brief.get("product_description"))
    exact_copy = string_list(brief.get("exact_copy"), "exact_copy", errors)
    confirmed_ingredients = string_list(brief.get("confirmed_ingredients"), "confirmed_ingredients", errors)
    confirmed_claims = string_list(brief.get("confirmed_claims"), "confirmed_claims", errors)
    visible_layers = string_list(brief.get("visible_layers"), "visible_layers", errors)
    must_preserve = string_list(brief.get("must_preserve"), "must_preserve", errors)
    forbidden = string_list(brief.get("forbidden"), "forbidden", errors)

    if mode in {"publish-ready", "channel-adaptation"}:
        if "PRODUCT_ASSET" not in roles:
            errors.append(f"{mode} mode requires a PRODUCT_ASSET")
        if not product_name:
            errors.append(f"{mode} mode requires product_name")
        if not product_description:
            errors.append(f"{mode} mode requires product_description")
    if mode == "style-spec" and "STYLE_REF" not in roles:
        errors.append("style-spec mode requires a STYLE_REF")
    if mode == "concept" and "PRODUCT_ASSET" not in roles:
        warnings.append("concept mode has no PRODUCT_ASSET; label the result as a concept visual")

    if len(exact_copy) != len(set(exact_copy)):
        errors.append("exact_copy contains duplicates; each literal string should appear once")
    price = text(brief.get("price"))
    promotion_terms = text(brief.get("promotion_terms"))
    if promotion_terms and not price:
        warnings.append("promotion_terms is present without price; verify the offer is complete")
    if price and not promotion_terms:
        warnings.append("price is present without promotion_terms; confirm whether conditions apply")
    if not text(brief.get("channel")):
        warnings.append("channel is empty; defaulting to social-portrait")
    if not text(brief.get("aspect_ratio")):
        warnings.append("aspect_ratio is empty; use the selected channel preset")

    normalized = dict(brief)
    normalized.update(
        {
            "mode": mode,
            "assets": assets,
            "product_name": product_name,
            "product_description": product_description,
            "exact_copy": exact_copy,
            "confirmed_ingredients": confirmed_ingredients,
            "confirmed_claims": confirmed_claims,
            "visible_layers": visible_layers,
            "must_preserve": must_preserve,
            "forbidden": forbidden,
        }
    )
    return errors, warnings, normalized


def joined(items: list[str], empty: str = "未提供；不得猜测") -> str:
    return "、".join(items) if items else empty


def build_prompt(brief: dict[str, Any]) -> str:
    assets = brief["assets"]
    asset_lines = [
        f'- {item["label"]}: {", ".join(item["roles"])}'
        + (f' ({item["notes"]})' if item.get("notes") else "")
        for item in assets
    ]
    roles = {role for item in assets for role in item["roles"]}
    exact_copy = list(brief["exact_copy"])
    product_name = brief["product_name"]
    if product_name and product_name not in exact_copy:
        exact_copy.insert(0, product_name)
    price = text(brief.get("price"))
    promotion_terms = text(brief.get("promotion_terms"))
    for literal in (price, promotion_terms):
        if literal and literal not in exact_copy:
            exact_copy.append(literal)

    concept_note = (
        "This is a concept visual without a PRODUCT_ASSET. Do not imply that the generated packaging is a real product."
        if brief["mode"] == "concept" and "PRODUCT_ASSET" not in roles
        else ""
    )
    style_note = (
        "Use STYLE_REF only for layout, typography behavior, color relationships, hero scale, graphic language, and finish. Replace its products, logos, wording, people, characters, and proprietary content."
        if "STYLE_REF" in roles
        else "Create an original commercial composition from the brief and brand assets."
    )
    product_note = (
        "Treat PRODUCT_ASSET as the destination product truth. Preserve count, silhouette, vessel/packaging, label and logo placement, colors, visible layers, toppings, proportions, and orientation. Improve integration and lighting without redesigning the product."
        if "PRODUCT_ASSET" in roles
        else concept_note
    )
    preset_note = ""
    if "STYLE_REF" not in roles and not text(brief.get("style_direction")):
        preset_path = Path(__file__).resolve().parent.parent / "references" / "warm-paper-preset.md"
        if preset_path.exists():
            preset_note = "\nDefault user-approved style preset (style only; keep the current product):\n" + preset_path.read_text(encoding="utf-8")

    preservation = list(brief["must_preserve"])
    if "PRODUCT_ASSET" in roles:
        preservation.extend(
            [
                "product count and silhouette",
                "cup or package structure",
                "label and logo placement",
                "visible liquid layers and toppings",
                "product proportions and orientation",
            ]
        )
    forbidden = list(brief["forbidden"])
    forbidden.extend(
        [
            "extra or invented ingredients",
            "unconfirmed price, origin, certification, nutrition, or health claims",
            "random text, pseudo-English, QR codes, signatures, or watermarks",
            "copied reference branding, packaging, characters, or exact composition",
        ]
    )

    mode = brief["mode"]
    output_intents = {
        "publish-ready": "Create a publishable tea-drink campaign visual",
        "concept": "Create a clearly labeled tea-drink concept visual",
        "style-spec": "Analyze the supplied style reference and return a reusable tea-drink poster system; do not generate an image",
        "series-template": "Build a reusable tea-drink campaign series template with invariants, controlled variables, asset slots, and a copy-ready prompt",
        "channel-adaptation": "Adapt the confirmed tea-drink campaign visual to the target channel without stretching or redesigning the product",
    }
    production_directions = {
        "style-spec": (
            "Describe observable layout, typography, product mechanism, color relationships, graphic language, and finish. "
            "Return Hard lock, Soft lock, Must replace from style reference, and recommended destination asset slots."
        ),
        "series-template": (
            "Separate series invariants from controlled variables. Allow only two to four controlled changes per variant, "
            "and include the reusable brief fields, asset roles, exact-copy policy, and acceptance gates."
        ),
        "channel-adaptation": (
            "Recompose for the target canvas while preserving product scale logic, packaging direction, brand assets, exact copy, "
            "and offer terms. Do not mechanically crop the source or stretch the product."
        ),
        "concept": (
            "Build an original visual from confirmed facts. If no PRODUCT_ASSET exists, keep the packaging generic and clearly treat it as conceptual. "
            "Reserve clean text zones for deterministic typesetting."
        ),
        "publish-ready": (
            "Prioritize product fidelity. Build or extend the background around the product, match perspective, light direction, contact shadow, "
            "reflections, depth of field, and grain. For dense Chinese copy, price, offer terms, or disclaimers, reserve clean text zones and add them "
            "with deterministic SVG/HTML/layout tools after image generation."
        ),
    }
    acceptance = (
        "The specification must be based on visible evidence and must separate reusable style mechanisms from reference content."
        if mode == "style-spec"
        else "The product must be immediately recognizable and physically plausible. Exact copy and verified facts must be correct. The reference visual system may be recognizable, but none of its semantic or proprietary content may survive. Do not call the result publish-ready if product fidelity or copy accuracy fails."
    )

    return f"""Output intent: {output_intents[mode]} for {text(brief.get('channel')) or 'social-portrait'}, aspect ratio {text(brief.get('aspect_ratio')) or 'use channel preset'}.
Mode: {mode}

Input roles:
{chr(10).join(asset_lines) if asset_lines else '- No image assets supplied'}

Role policy:
{style_note}
{product_note}
{preset_note}

Product facts:
- Product name: {product_name or '未提供'}
- Copy status: {text(brief.get('copy_status')) or 'Not specified; do not present proposed copy as an existing official name or slogan'}
- Visible product description: {brief['product_description'] or '未提供'}
- Category: {text(brief.get('category')) or 'tea-drink'}
- Temperature: {text(brief.get('temperature')) or '未提供；不得猜测'}
- Visible layers: {joined(brief['visible_layers'])}
- Confirmed ingredients: {joined(brief['confirmed_ingredients'])}
- Confirmed claims allowed in copy: {joined(brief['confirmed_claims'])}
- Origin: {text(brief.get('origin')) or '未提供；不得猜测'}

Campaign:
- Goal: {text(brief.get('campaign_goal')) or 'product communication'}
- Audience: {text(brief.get('audience')) or '未指定'}
- Style direction: {text(brief.get('style_direction')) or 'derive an original commercial direction from the supplied assets'}
- Reading path: brand or series → product → product name → confirmed benefit/flavor → verified offer or action.
- Copy layout: {text(brief.get('copy_layout')) or 'Map reference text slots by position, visible type height, occupied width, line count, spacing, and capacity. Draft missing names, slogans, and microcopy to fit those slots before producing the final exact-copy list; do not invent factual claims.'}
- Product title rule: preserve the complete product name and follow the user or reference title layout, including multiple lines, vertical text, or staggered alignment when appropriate. Match visible glyph scale, footprint, and margins; fit proposed copy length to the slot rather than shrinking the headline. Never abbreviate a supplied official name without authorization. Glyphs may overlap decorative art, but never use a rectangular backing patch, color strip, or blur to clear the title.
- Title layout details: {text(brief.get('title_layout')) or 'derive from the reference and user instructions'}
- Title content role: the main central headline contains the complete product name only. If it spans multiple lines, all lines together form that one name. Never combine one name line with one slogan line as the main title; place slogans in separate subordinate copy slots unless the user explicitly requests otherwise.

Must preserve from destination assets:
{joined(list(dict.fromkeys(preservation)), 'Only confirmed destination assets and facts')}

Exact text, verbatim, exactly once each; no other text:
{joined([f'“{item}”' for item in exact_copy], 'No in-image text unless added later with deterministic typesetting')}

Production direction:
{production_directions[mode]}

Forbidden:
{joined(list(dict.fromkeys(forbidden)))}

Acceptance:
{acceptance}"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a tea-drink brief and build a structured campaign prompt.")
    parser.add_argument("--brief", required=True, help="JSON file path or '-' for stdin")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--json-report", action="store_true", help="Print validation as JSON")
    args = parser.parse_args()

    try:
        brief = load_brief(args.brief)
        errors, warnings, normalized = validate(brief)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = {"ok": not errors, "errors": errors, "warnings": warnings}
    if errors:
        if args.json_report or args.validate_only:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.validate_only:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    prompt = build_prompt(normalized)
    if args.json_report:
        print(json.dumps({**report, "prompt": prompt}, ensure_ascii=False, indent=2))
        return 0

    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
