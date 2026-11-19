"""Recreate the Kenyan storefront data (Kenya KES channel + 10 Kenyan products).

Run inside the running API container, after `docker compose up` and after the
demo data has been populated (``docker compose exec api python manage.py
populatedb``), e.g.:

    docker cp scripts/seed-kenya.py saleor-platform-api-1:/tmp/seed-kenya.py
    docker exec saleor-platform-api-1 python manage.py shell \\
        -c "exec(open('/tmp/seed-kenya.py').read())"

The script is idempotent: re-running it updates the existing channel,
products, listings and stock instead of duplicating them.

What it creates (exact data from the live Kenyan store, Nov 2026):
  * Channel ``kenya-kes`` ("Kenya (KES)", currency KES, default country KE).
  * Category ``kenyan-goods`` ("Kenyan Goods").
  * Product type ``simple`` ("Simple", no variants) if it does not exist yet.
  * 10 products, each with one variant (SKUs KE-001..KE-010), a KES channel
    listing and 50 units of stock in the ``africa`` warehouse.
  * Collections ``featured-products`` and ``summer-picks`` if they do not
    exist yet. Note: in the live store the Kenyan products are NOT assigned
    to any collection, so this script does not attach them either.

It does NOT touch shipping zones, taxes or payment settings: the live store
reuses the demo shipping zones, and checkout is out of scope here.
"""

import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from prices import Money

from saleor.channel.models import Channel
from saleor.product.models import (
    Category,
    Collection,
    Product,
    ProductChannelListing,
    ProductType,
    ProductVariant,
    ProductVariantChannelListing,
)
from saleor.warehouse.models import Stock, Warehouse

# (name, slug, description, sku, price in KES)
PRODUCTS = [
    (
        "Kenyan AA Coffee Beans 500g",
        "kenyan-aa-coffee-beans-500g",
        "Single-origin Kenyan AA arabica coffee beans, 500g bag, roasted in Nairobi.",
        "KE-001",
        "1850",
    ),
    (
        "Kericho Gold Tea 250g",
        "kericho-gold-tea-250g",
        "Black tea from the Kericho highlands, 250g pack.",
        "KE-002",
        "650",
    ),
    (
        "Maasai Shuka Blanket",
        "maasai-shuka-blanket",
        "Traditional red-checked Maasai shuka blanket, woven cotton.",
        "KE-003",
        "1500",
    ),
    (
        "Kiondo Sisal Basket",
        "kiondo-sisal-basket",
        "Handwoven sisal kiondo basket with leather handles, made in Kenya.",
        "KE-004",
        "2200",
    ),
    (
        "Handmade Leather Sandals",
        "handmade-leather-sandals",
        "Handmade leather sandals, crafted by Kenyan artisans.",
        "KE-005",
        "2800",
    ),
    (
        "Nairobi Leather Tote Bag",
        "nairobi-leather-tote-bag",
        "Full-grain leather tote bag, made in Nairobi.",
        "KE-006",
        "4500",
    ),
    (
        "Solar Lantern",
        "solar-lantern",
        "Rechargeable solar lantern for home and outdoor use.",
        "KE-007",
        "2400",
    ),
    (
        "Kenyan Honey 500ml",
        "kenyan-honey-500ml",
        "Pure raw Kenyan honey, 500ml jar.",
        "KE-008",
        "1100",
    ),
    (
        "Shea Butter Body Cream",
        "shea-butter-body-cream",
        "Whipped shea butter body cream, natural ingredients.",
        "KE-009",
        "900",
    ),
    (
        "Boda Boda Helmet",
        "boda-boda-helmet",
        "Safety helmet for boda boda riders, certified.",
        "KE-010",
        "3800",
    ),
]

STOCK_QUANTITY = 50


def editorjs_description(text):
    """Saleor stores rich-text descriptions as EditorJS JSON."""
    return {
        "time": int(time.time() * 1000),
        "blocks": [
            {"id": "kenya00001", "data": {"text": text}, "type": "paragraph"}
        ],
        "version": "2.22.2",
    }


def main():
    channel, _ = Channel.objects.update_or_create(
        slug="kenya-kes",
        defaults={
            "name": "Kenya (KES)",
            "currency_code": "KES",
            "default_country": "KE",
            "is_active": True,
        },
    )
    print(f"Channel: {channel.slug} ({channel.currency_code})")

    category, _ = Category.objects.get_or_create(
        slug="kenyan-goods", defaults={"name": "Kenyan Goods"}
    )
    print(f"Category: {category.slug}")

    product_type, _ = ProductType.objects.get_or_create(
        slug="simple", defaults={"name": "Simple", "has_variants": False}
    )
    print(f"Product type: {product_type.slug}")

    warehouse, _ = Warehouse.objects.get_or_create(
        slug="africa",
        defaults={"name": "Africa"},
    )
    warehouse.channels.add(channel)
    print(f"Warehouse: {warehouse.slug} (linked to {channel.slug})")

    for name, slug, description, sku, price in PRODUCTS:
        product, _ = Product.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": editorjs_description(description),
                "product_type": product_type,
                "category": category,
            },
        )
        ProductChannelListing.objects.update_or_create(
            product=product,
            channel=channel,
            defaults={"is_published": True, "visible_in_listings": True},
        )
        variant, _ = ProductVariant.objects.update_or_create(
            product=product,
            sku=sku,
            defaults={"name": ""},
        )
        ProductVariantChannelListing.objects.update_or_create(
            variant=variant,
            channel=channel,
            defaults={
                # NOTE: do NOT pass cost_price here. Both price and
                # cost_price share the single `currency` column, and
                # assigning cost_price=None would clear currency.
                "price": Money(Decimal(price), "KES"),
                "currency": "KES",
            },
        )
        Stock.objects.update_or_create(
            warehouse=warehouse,
            product_variant=variant,
            defaults={"quantity": STOCK_QUANTITY},
        )
        print(f"  {sku} {name}: KES {price} (stock {STOCK_QUANTITY})")

    for slug, name in [
        ("featured-products", "Featured Products"),
        ("summer-picks", "Summer Picks"),
    ]:
        collection, created = Collection.objects.get_or_create(
            slug=slug, defaults={"name": name}
        )
        print(f"Collection: {collection.slug} ({'created' if created else 'exists'})")

    print("Done: kenya-kes channel with 10 Kenyan products.")


main()
