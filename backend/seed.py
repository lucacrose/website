from database import SessionLocal, Base, engine
from models import Item, TimeSeriesPoint
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

ITEM_DATA_FILE_PATH = os.getenv("ITEM_DATA_FILE_PATH")

Base.metadata.create_all(bind=engine)

def wipe_and_seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        with open(ITEM_DATA_FILE_PATH, "r") as f:
            data = json.loads(f.read())

        items = []

        for i, item in enumerate(data, start=1):
            points = []

            item_obj = Item(id=item["item_id"], name=item["item_details_data"]["item_name"])

            for j in range(item["history_data"]["num_points"]):
                timestamp = item["history_data"]["timestamp"][j]
                favorited = item["history_data"]["favorited"][j]
                rap = item["history_data"]["rap"][j]
                best_price = item["history_data"]["best_price"][j]
                num_sellers = item["history_data"]["num_sellers"][j]

                point = TimeSeriesPoint(timestamp=datetime.utcfromtimestamp(timestamp), favorited=favorited, rap=rap, best_price=best_price, num_sellers=num_sellers)

                points.append(point)

            item_obj.time_series = points

            items.append(item_obj)

            print(f"Built item {i}/{len(data)}")

            db.add(item_obj)

            if i % 16 == 0:
                db.commit()
                db.expunge_all()

        db.commit()

        print("Database wiped and seeded successfully")
    finally:
        db.close()
