import os
from sqlmodel import SQLModel, create_engine, Session, select, or_, col
from . import models # Required by SQLModel.metadata.create_all(engine)
from .models import Hero, Team, HeroCityLink


# Write to the database
SQLALCHEMY_DATABASE_URL = os.environ['FAST_API_SQLALCHEMY_DATABASE_URL']  # postgresql://fastapi_app:fastapi_app_password@postgres-docker:5432/fastapi_db
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={}) # echo=True for debugging

# create the database and all the tables registered in this MetaData object.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# INSERT
def create_heroes():
    with Session(engine) as session:
        city_1 = models.City(name="New York", state="NY")
        city_2 = models.City(name="Los Angeles", state="CA")
        city_3 = models.City(name="Chicago", state="IL")
        city_4 = models.City(name="Houston", state="TX")
        session.add(city_1)
        session.add(city_2)
        session.add(city_3)
        session.add(city_4)
        session.commit()
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret’s Bar")
        session.add(team_preventers)
        session.add(team_z_force)
        session.commit()
        hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson", team_id=team_z_force.id)
        hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
        hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48, team_id=team_preventers.id)
        hero_4 = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32, team_id=team_preventers.id)
        hero_5 = Hero(name="Black Lion", secret_name="Trevor Challa", age=35, team_id=team_preventers.id)
        hero_6 = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
        hero_7 = Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93)
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.add(hero_4)
        session.add(hero_5)
        session.add(hero_6)
        session.add(hero_7)
        session.commit()
        hero_1_city_1_link = HeroCityLink(hero=hero_1, city=city_1, )
        hero_1_city_2_link = HeroCityLink(hero=hero_1, city=city_2, is_training=True)
        hero_2_city_1_link = HeroCityLink(hero=hero_2, city=city_1)
        hero_3_city_3_link = HeroCityLink(hero=hero_3, city=city_3)
        hero_4_city_2_link = HeroCityLink(hero=hero_4, city=city_2)
        hero_4_city_4_link = HeroCityLink(hero=hero_4, city=city_4)
        session.add(hero_1_city_1_link)
        session.add(hero_1_city_2_link)
        session.add(hero_2_city_1_link)
        session.add(hero_3_city_3_link)
        session.add(hero_4_city_2_link)
        session.add(hero_4_city_4_link)
        session.commit()

# SELECT
def select_heroes():
    with Session(engine) as session:
        # statement = select(Hero).where((Hero.name == "Deadpond"))
        # statement = select(Hero).where(Hero.age >= 35, Hero.age < 40)
        # statement = select(Hero).where(or_(Hero.age <= 35, Hero.age > 90))
        statement = select(Hero).where(col(Hero.age) >= 35) # col() only applies for the values that are not NULL in the database,
        heroes = session.exec(statement).all()
        for hero in heroes:
            print(hero)
        return heroes

def select_heroes_and_teams():
    with Session(engine) as session:
        statement = select(Hero, Team).where(Hero.team_id == Team.id)
        results = session.exec(statement).all()
        for hero, team in results:
            print("Hero:", hero, "Team:", team)
        return results

def select_heroes_with_teams():
    with Session(engine) as session:
        statement = select(Hero).join(Team, Hero.team_id == Team.id)
        results = session.exec(statement).all()
        res = []
        for hero in results:
            if hero.team:
                res.append({"hero": hero, "team": hero.team})
        return res

# UPDATE
def update_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        results = session.exec(statement)
        hero_1 = results.one()
        print("Hero 1:", hero_1)
        statement = select(Hero).where(Hero.name == "Captain North America")
        results = session.exec(statement)
        hero_2 = results.one()
        print("Hero 2:", hero_2)
        hero_1.age = 16
        hero_1.name = "Spider-Youngster"
        session.add(hero_1)
        hero_2.name = "Captain North America Except Canada"
        hero_2.age = 110
        session.add(hero_2)
        session.commit()
        session.refresh(hero_1)
        session.refresh(hero_2)
        print("Updated hero 1:", hero_1)
        print("Updated hero 2:", hero_2)

# DELETE
def delete_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Youngster")
        results = session.exec(statement)
        hero = results.one()
        print("Hero: ", hero)
        for city_link in hero.city_links:
            session.delete(city_link)
        session.commit()
        session.delete(hero)
        session.commit()
        print("Deleted hero:", hero)
        statement = select(Hero).where(Hero.name == "Spider-Youngster")
        results = session.exec(statement)
        hero = results.first()
        if hero is None:
            print("There's no hero named Spider-Youngster")

def main():
    create_db_and_tables()
    create_heroes()
    update_heroes()
    delete_heroes()

# Only called in command line 'python db.py'
if __name__ == "__main__":
    main()
