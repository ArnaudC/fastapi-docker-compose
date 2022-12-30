from sqlmodel import Field, SQLModel, Relationship


# API models
class HeroBase(SQLModel): # Only inherit from data models
    name: str = Field(index=True) # An index on the field name
    team_id: int|None = Field(default=None, foreign_key="team.id")
    secret_name: str
    age: int|None = Field(default=None, index=True) # The default value of age will continue to be None, so we set default=None.

class HeroCreate(HeroBase):
    pass

class HeroRead(HeroBase):
    id: int

class HeroUpdate(SQLModel):
    name: str|None = None
    secret_name: str|None = None
    age: int|None = None
    team_id: int|None = None

class TeamBase(SQLModel):
    name: str = Field(index=True)
    headquarters: str

class TeamCreate(TeamBase):
    pass

class TeamRead(TeamBase):
    id: int

class TeamUpdate(SQLModel):
    name: str|None = None
    headquarters: str|None = None

class HeroReadWithTeam(HeroRead):
    team: TeamRead|None = None

class TeamReadWithHeroes(TeamRead):
    heroes: list[HeroRead] = []

# Database models
## ManyToMany between Hero and City
class HeroCityLink(SQLModel, table=True):
    hero_id: int|None = Field(default=None, foreign_key="hero.id", primary_key=True)
    city_id: int|None = Field(default=None, foreign_key="city.id", primary_key=True)
    hero: "Hero" = Relationship(back_populates="city_links")
    city: "City" = Relationship(back_populates="hero_links")
    is_training: bool = False

class City(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    hero_links: list[HeroCityLink] = Relationship(back_populates="city")
    name: str = Field(index=True)
    state: str|None = None

class Team(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")
    name: str = Field(index=True)
    headquarters: str

class Hero(HeroBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    team: Team|None = Relationship(back_populates="heroes")
    city_links: list[HeroCityLink] = Relationship(back_populates="hero")
    team_id: int|None = Field(default=None, foreign_key="team.id")
