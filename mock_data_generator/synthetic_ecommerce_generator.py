import argparse
import csv
import os
import random
import string
import uuid
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd

# Initialize faker
faker = Faker()
Faker.seed(42)

SOURCES = ["CRM", "ECommerce_Web", "Mobile_App", "Marketing_Platform", "Payment_System"]
CATEGORIES = ["Electronics", "Fashion", "Home & Kitchen", "Books", "Health", "Beauty", "Sports", "Toys"]

def random_case_variation(text):
    """Randomly change casing to simulate inconsistency."""
    styles = [str.upper, str.lower, str.title]
    return random.choice(styles)(text) if text else text

def add_typo(text):
    """Add small typos for fuzzy match simulation."""
    if not text or len(text) < 3 or random.random() > 0.3:
        return text
    pos = random.randint(0, len(text)-1)
    return text[:pos] + random.choice(string.ascii_lowercase) + text[pos+1:]

def random_date(start_years_ago=5):
    """Return a random date in the last N years."""
    start_date = datetime.now() - timedelta(days=start_years_ago*365)
    end_date = datetime.now()
    date = faker.date_between(start_date=start_date, end_date=end_date)
    # Mix formats
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]
    return date.strftime(random.choice(formats))

def generate_customer(source, canonical_id=None):
    """Generate one customer record."""
    first = faker.first_name()
    last = faker.last_name()
    full = f"{first} {last}"
    email_base = f"{first.lower()}.{last.lower()}@{faker.free_email_domain()}"

    reg_date = random_date()
    last_purchase = reg_date if random.random() < 0.8 else ""
    if last_purchase:
        last_purchase = random_date()

    record = {
        "customer_id": f"{source}_{uuid.uuid4().hex[:8]}",
        "first_name": first,
        "last_name": last,
        "full_name": full,
        "email": email_base,
        "phone_number": faker.phone_number() if random.random() > 0.15 else "",
        "address_line1": faker.street_address(),
        "address_line2": faker.secondary_address() if random.random() > 0.3 else "",
        "city": faker.city(),
        "state": faker.state(),
        "postal_code": faker.postcode(),
        "country": faker.country(),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=80).strftime(random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"])) if random.random() > 0.05 else "",
        "registration_date": reg_date,
        "last_purchase_date": last_purchase,
        "total_orders": random.randint(0, 200),
        "total_spent": round(random.uniform(0, 20000), 2),
        "preferred_category": random.choice(CATEGORIES),
        "source_system": source,
        "canonical_id": canonical_id or uuid.uuid4().hex[:12],
    }
    return record

def add_variation(record):
    """Create a fuzzy duplicate of a record."""
    dup = record.copy()
    variations = [
        lambda r: r.update({"first_name": add_typo(r["first_name"])}),
        lambda r: r.update({"last_name": random_case_variation(r["last_name"])}),
        lambda r: r.update({"email": add_typo(r["email"].replace("@", str(random.randint(1,9)) + "@"))}),
        lambda r: r.update({"address_line1": r["address_line1"].replace("Street", "St.") if "Street" in r["address_line1"] else r["address_line1"]}),
        lambda r: r.update({"city": add_typo(r["city"])}),
        lambda r: r.update({"postal_code": add_typo(r["postal_code"])}),
    ]
    random.choice(variations)(dup)
    dup["customer_id"] = f"{dup['source_system']}_{uuid.uuid4().hex[:8]}"
    dup["email"] = dup["email"].lower().strip()
    return dup

def generate_dataset(n_rows, overlap_pct=0.15, seed=42, incremental=False, existing_file=None, output="synthetic_customers.csv"):
    random.seed(seed)
    Faker.seed(seed)

    all_records = []

    if incremental and existing_file and os.path.exists(existing_file):
        existing_df = pd.read_csv(existing_file)
        print(f"Loaded {len(existing_df)} existing records.")
        canonical_ids = existing_df["canonical_id"].unique().tolist()
    else:
        existing_df = pd.DataFrame()
        canonical_ids = []

    # Determine overlap count (how many to re-use)
    overlap_count = int(n_rows * overlap_pct) if len(canonical_ids) > 0 else 0
    new_count = n_rows - overlap_count

    # Reuse existing canonical_ids for duplicates
    reused_ids = random.sample(canonical_ids, k=min(overlap_count, len(canonical_ids))) if canonical_ids else []

    # Generate new unique records
    for _ in range(new_count):
        src = random.choice(SOURCES)
        rec = generate_customer(src)
        all_records.append(rec)

    # Add variants for reused identities
    for cid in reused_ids:
        src = random.choice(SOURCES)
        base_rec = existing_df[existing_df["canonical_id"] == cid].sample(1).iloc[0].to_dict()
        variant = add_variation(base_rec)
        variant["source_system"] = src
        all_records.append(variant)

    df = pd.DataFrame(all_records)
    df.to_csv(output, index=False)
    print(f"✅ Generated {len(df)} records → {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic e-commerce dataset")
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--output", type=str, default="synthetic_customers.csv")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument("--existing_file", type=str, default="synthetic_customers.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate_dataset(
        n_rows=args.rows,
        incremental=args.incremental,
        existing_file=args.existing_file,
        seed=args.seed,
        output=args.output
    )
