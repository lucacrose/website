from database import SessionLocal, Base, engine
from models import Item
from dotenv import load_dotenv
import os
import json

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

        for item in data:
            items.append(Item(id=item["item_id"], name=item["item_details_data"]["item_name"]))

        db.add_all(items)
        db.commit()

        print("Database wiped and seeded successfully")
    finally:
        db.close()
