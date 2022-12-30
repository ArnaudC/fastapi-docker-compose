from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Session, select
from .models import Hero, HeroRead, HeroCreate, HeroUpdate, Team, TeamRead, TeamCreate, TeamUpdate, HeroReadWithTeam, TeamReadWithHeroes
from .db import engine, create_db_and_tables, create_heroes, select_heroes, update_heroes, select_heroes_and_teams, select_heroes_with_teams # Use SQLModel from db.py to ensure models are registered in the same MetaData object.

app_name = "app_sql_model"
app = FastAPI(docs_url="/docs")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # create the database and tables once at startup

def get_session():
    with Session(engine) as session:
        yield session

class Tags:
    heroes = "heroes"
    teams = "teams"

# Heroes
@app.get("/create_db_and_tables", tags=[Tags.heroes])
def api_create_db_and_tables():
    create_db_and_tables()
    return {"message": "Db and tables initialized"}

@app.get("/create_heroes", tags=[Tags.heroes])
def api_create_heroes():
    create_heroes()
    return {"message": "Heroes created"}

@app.get("/select_heroes", tags=[Tags.heroes])
def api_select_heroes():
    return select_heroes()

@app.get("/update_heroes", tags=[Tags.heroes])
def api_update_heroes():
    update_heroes()
    return {"message": "Heroes updated"}

@app.get("/select_heroes_and_teams", tags=[Tags.heroes])
def api_select_heroes_and_teams():
    return select_heroes_and_teams()

@app.get("/select_heroes_with_teams", tags=[Tags.heroes])
def api_select_heroes_with_teams():
    return select_heroes_with_teams()

@app.post("/heroes/", response_model=HeroRead, tags=[Tags.heroes])
def create_hero(*, session: Session = Depends(get_session), hero: HeroCreate): # * means that all the parameters after it must be named
    db_hero = Hero.from_orm(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=list[HeroRead], tags=[Tags.heroes])
def read_heroes(*, session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, lte=100)):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroReadWithTeam, tags=[Tags.heroes])
def read_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroRead, tags=[Tags.heroes])
def update_hero(*, session: Session = Depends(get_session), hero_id: int, hero: HeroUpdate):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.dict(exclude_unset=True) # Can remove the age with PATCH {"age": null}
    for key, value in hero_data.items():
        setattr(db_hero, key, value)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.delete("/heroes/{hero_id}", tags=[Tags.heroes])
def delete_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    for city_link in hero.city_links:
        session.delete(city_link)
    session.commit()
    session.delete(hero)
    session.commit()
    return {"ok": True}

# Teams
@app.post("/teams/", response_model=TeamRead, tags=[Tags.teams])
def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
    db_team = Team.from_orm(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@app.get("/teams/", response_model=list[TeamRead], tags=[Tags.teams])
def read_teams(*, session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, lte=100)):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams

@app.get("/teams/{team_id}", response_model=TeamReadWithHeroes, tags=[Tags.teams])
def read_team(*, team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.patch("/teams/{team_id}", response_model=TeamRead, tags=[Tags.teams])
def update_team(*, session: Session = Depends(get_session), team_id: int, team: TeamUpdate):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.dict(exclude_unset=True)
    for key, value in team_data.items():
        setattr(db_team, key, value)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@app.delete("/teams/{team_id}", tags=[Tags.teams])
def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}
