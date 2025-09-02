from database import SessionLocal, Base, engine
from models import Item

Base.metadata.create_all(bind=engine)

def wipe_and_seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        items = [
            Item(abbreviation="RS", name="Rare Sword", value=1000),
            Item(abbreviation="EH", name="Epic Hat", value=500),
            Item(abbreviation="LS", name="Legendary Shield", value=2500)
        ]

        db.add_all(items)
        db.commit()

        print("Database wiped and seeded successfully")
    finally:
        db.close()
