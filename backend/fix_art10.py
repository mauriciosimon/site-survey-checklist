import sys
sys.path.insert(0, '/root/clawd-dev/projects/westpark-surveys/backend')

from database import SessionLocal
from models import RateCardItem

db = SessionLocal()

# Fix ART10
art10 = db.query(RateCardItem).filter(RateCardItem.art_code == "ART10").first()
if art10:
    art10.description = "Lockset / latch / lock mechanism issues"
    art10.rate_card_code = "B05"
    art10.rate_card_description = "Replace lever handles / latch set — supply & fit, CE-marked ironmongery"
    art10.unit_price = "£95.00"
    db.commit()
    print(f"✓ Updated ART10: {art10.description} -> {art10.rate_card_code}")
else:
    print("✗ ART10 not found")

db.close()
