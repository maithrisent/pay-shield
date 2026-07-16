import json
from db.database import get_db_connection
from auth.phone_hash import hash_phone

# Balances are in paise: 500000 paise = ₹5000
DEMO_USERS = [
    {"phone": "9900000001", "label": "Diya (payer)", "starting_balance_paise": 500000},
    {"phone": "9900000002", "label": "Auto driver Ramesh (receiver)", "starting_balance_paise": 100000},
    {"phone": "9900000003", "label": "Cafe owner Priya (receiver)", "starting_balance_paise": 100000},
]


def seed():
    demo_map = {}

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for u in DEMO_USERS:
                phone_hash = hash_phone(u["phone"])

                # Safe to re-run: skip creating a user that already exists
                cur.execute(
                    """
                    INSERT INTO users (phone_hash, kyc_status)
                    VALUES (%s, 'verified')
                    ON CONFLICT (phone_hash) DO NOTHING
                    RETURNING id
                    """,
                    (phone_hash,),
                )
                row = cur.fetchone()
                if row is None:
                    cur.execute(
                        "SELECT id FROM users WHERE phone_hash = %s",
                        (phone_hash,),
                    )
                    row = cur.fetchone()
                user_id = row[0]

                # Also safe to re-run: only create a wallet if this user
                # doesn't already have one, so re-running seed.py never
                # gives someone a second wallet or resets their balance
                cur.execute(
                    "SELECT id FROM wallets WHERE user_id = %s", (user_id,)
                )
                if cur.fetchone() is None:
                    cur.execute(
                        "INSERT INTO wallets (user_id, balance) VALUES (%s, %s)",
                        (user_id, u["starting_balance_paise"]),
                    )

                demo_map[u["phone"]] = {
                    "user_id": str(user_id),
                    "label": u["label"],
                }

    # Dumped to a file so the frontend/demo can hardcode quick-login
    # buttons instead of typing phone numbers live during a demo
    with open("demo-users.json", "w") as f:
        json.dump(demo_map, f, indent=2)

    print("Seeded demo users:")
    for phone, info in demo_map.items():
        print(f"  {phone} -> {info['label']} (user_id: {info['user_id']})")


if __name__ == "__main__":
    seed()