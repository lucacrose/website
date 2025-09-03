from database import SessionLocal, Base, engine
from models import Item, TimeSeriesPoint
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

ITEM_DATA_FILE_PATH = os.getenv("ITEM_DATA_FILE_PATH")

Base.metadata.create_all(bind=engine)

def wipe():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database wiped successfully")

def seed():
    db = SessionLocal()

    try:
        existing_count = db.query(Item).count()

        if existing_count > 0:
            print(f"Database already has {existing_count} items. Skipping seed.")
            return
        
        with open(ITEM_DATA_FILE_PATH, "r") as f:
            data = json.loads(f.read())

        items = []

        for i, item in enumerate(data, start=1):
            points = []

            item_obj = Item(id=item["item_id"], name=item["item_details_data"]["item_name"])

            for j in range(item["history_data"]["num_points"]):
                timestamp = item["history_data"]["timestamp"][j] / 3600
                favorited = item["history_data"]["favorited"][j]
                rap = item["history_data"]["rap"][j]
                best_price = item["history_data"]["best_price"][j] - 2 ** 63
                num_sellers = item["history_data"]["num_sellers"][j]

                point = TimeSeriesPoint(timestamp=timestamp, favorited=favorited, rap=rap, best_price=best_price, num_sellers=num_sellers)

                points.append(point)

            item_obj.time_series = points

            items.append(item_obj)

            print(f"Built item {i}/{len(data)}")

            db.add(item_obj)

            if i % 16 == 0:
                db.commit()
                db.expunge_all()

        db.commit()

        print("Database seeded successfully")
    finally:
        db.close()
