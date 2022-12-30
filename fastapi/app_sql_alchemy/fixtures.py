from sqlalchemy.orm import Session
from .crud import create_user, create_user_item, get_items, get_users, delete_user, delete_item
from .database import SessionLocal
from .schemas import UserCreate, ItemCreate

email_1 = "user_1@users.com"
item_title_1 = "item_1"

# INSERT
def insert_fixtures(db):
    user_1 = UserCreate(email=email_1, password="user_1_password")
    user_1 = create_user(db=db, user=user_1)
    item_1 = ItemCreate(title=item_title_1, description="item 1 description")
    item_1 = create_user_item(db=db, item=item_1, user_id=user_1.id)

# SELECT
def select_fixtures(db):
    all_items = get_items(db)
    for item in all_items:
        print(item.title, item.description)
    for user in get_users(db):
        print(user.email, user.items)
    return all_items

# UPDATE
def update_fixtures(db):
    pass

# DELETE
def delete_fixtures(db):
    delete_item(db=db, title=item_title_1)
    delete_user(db=db, email=email_1)

def main():
    with SessionLocal() as db:
        delete_fixtures(db)
        insert_fixtures(db)
        select_fixtures(db)

# Only called in command line 'python fixtures.py'
if __name__ == "__main__":
    main()
