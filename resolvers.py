from ariadne import QueryType, MutationType, ObjectType
from database import get_db_connection
import sqlite3

query = QueryType()
mutation = MutationType()
character_type = ObjectType("Character")
planet_type = ObjectType("Planet")
starship_type = ObjectType("Starship")

# --- Query Resolvers ---
@query.field("allCharacters")
def resolve_all_characters(_, info):
    conn = get_db_connection()
    try:
        characters = conn.execute("SELECT id, name, species, home_planet_id, affiliation_id, rank_id FROM characters").fetchall()
        return [dict(char) for char in characters]
    finally:
        conn.close()

@query.field("character")
def resolve_character(_, info, id):
    conn = get_db_connection()
    try:
        character = conn.execute("SELECT id, name, species, home_planet_id, affiliation_id, rank_id FROM characters WHERE id = ?", (id,)).fetchone()

        if not character:
            raise Exception(f"Karakter dengan ID {id} tidak ditemukan.")   
        
        return dict(character)
    finally:
        conn.close()

@query.field("allPlanets")
def resolve_all_planets(_, info):
    conn = get_db_connection()
    try:
        planets = conn.execute("SELECT id, name, climate, terrain FROM planets").fetchall()
        return [dict(p) for p in planets]
    finally:
        conn.close()

@query.field("planet")
def resolve_planet(_, info, id):
    conn = get_db_connection()
    try:
        planet = conn.execute("SELECT id, name, climate, terrain FROM planets WHERE id = ?", (id,)).fetchone()
        return dict(planet) if planet else None
    finally:
        conn.close()

@query.field("allStarships")
def resolve_all_starships(_, info):
    conn = get_db_connection()
    try:
        starships = conn.execute("SELECT id, name, model, manufacturer FROM starships").fetchall()
        return [dict(s) for s in starships]
    finally:
        conn.close()

@query.field("starship")
def resolve_starship(_, info, id):
    conn = get_db_connection()
    try:
        starship = conn.execute("SELECT id, name, model, manufacturer FROM starships WHERE id = ?", (id,)).fetchone()

        if not starship:
            raise Exception(f"Starship dengan ID {id} tidak ditemukan.")
        
        return dict(starship)
    finally:
        conn.close()

@query.field("allAffiliations")
def resolve_all_affiliations(_, info):
    conn = get_db_connection()
    try:
        affiliations = conn.execute("SELECT id, name FROM affiliations").fetchall()
        return [dict(a) for a in affiliations]
    finally:
        conn.close()

@query.field("allRanks")
def resolve_all_ranks(_, info):
    conn = get_db_connection()
    try:
        ranks = conn.execute("SELECT id, name FROM ranks").fetchall()
        return [dict(r) for r in ranks]
    finally:
        conn.close()


# --- Nested Resolvers ---
@character_type.field("homePlanet")
def resolve_character_home_planet(character_obj, info):
    home_planet_id = character_obj.get("home_planet_id")
    if not home_planet_id:
        return None
    conn = get_db_connection()
    try:
        planet = conn.execute("SELECT id, name, climate, terrain FROM planets WHERE id = ?", (home_planet_id,)).fetchone()
        return dict(planet) if planet else None
    finally:
        conn.close()

@character_type.field("pilotedStarships")
def resolve_character_piloted_starships(character_obj, info):
    character_id = character_obj.get("id")
    conn = get_db_connection()
    try:
        starships = conn.execute(
            """
            SELECT s.id, s.name, s.model, s.manufacturer
            FROM starships s
            JOIN character_starships cs ON s.id = cs.starship_id
            WHERE cs.character_id = ?
            """,
            (character_id,),
        ).fetchall()
        return [dict(s) for s in starships]
    finally:
        conn.close()

@planet_type.field("residents")
def resolve_planet_residents(planet_obj, info):
    planet_id = planet_obj.get("id")
    conn = get_db_connection()
    try:
        characters = conn.execute(
            "SELECT id, name, species, home_planet_id FROM characters WHERE home_planet_id = ?",
            (planet_id,),
        ).fetchall()
        return [dict(char) for char in characters]
    finally:
        conn.close()

@starship_type.field("pilots")
def resolve_starship_pilots(starship_obj, info):
    starship_id = starship_obj.get("id")
    conn = get_db_connection()
    try:
        characters = conn.execute(
            """
            SELECT c.id, c.name, c.species, c.home_planet_id
            FROM characters c
            JOIN character_starships cs ON c.id = cs.character_id
            WHERE cs.starship_id = ?
            """,
            (starship_id,),
        ).fetchall()
        return [dict(char) for char in characters]
    finally:
        conn.close()

@character_type.field("affiliation")
def resolve_character_affiliation(character_obj, info):
    aff_id = character_obj.get("affiliation_id")
    if not aff_id:
        return None
    conn = get_db_connection()
    try:
        aff = conn.execute("SELECT id, name FROM affiliations WHERE id = ?", (aff_id,)).fetchone()
        return dict(aff) if aff else None
    finally:
        conn.close()

@character_type.field("rank")
def resolve_character_rank(character_obj, info):
    rank_id = character_obj.get("rank_id")
    if not rank_id:
        return None
    conn = get_db_connection()
    try:
        rank = conn.execute("SELECT id, name FROM ranks WHERE id = ?", (rank_id,)).fetchone()
        return dict(rank) if rank else None
    finally:
        conn.close()

# --- Mutation Resolvers ---
@mutation.field("createPlanet")
def resolve_create_planet(_, info, input):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO planets (name, climate, terrain) VALUES (?, ?, ?)",
            (input["name"], input.get("climate"), input.get("terrain")),
        )
        conn.commit()
        planet_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        planet = conn.execute("SELECT id, name, climate, terrain FROM planets WHERE id = ?", (planet_id,)).fetchone()
        return dict(planet)
    except sqlite3.IntegrityError:
        conn.rollback()
        raise Exception(f"Planet '{input['name']}' sudah ada.")
    finally:
        conn.close()

@mutation.field("updatePlanet")
def resolve_update_planet(_, info, input):
    conn = get_db_connection()
    try:
        planet = conn.execute("SELECT id, name, climate, terrain FROM planets WHERE id = ?", (input["id"],)).fetchone()
        if not planet:
            raise Exception(f"Planet dengan ID {input['id']} tidak ditemukan.")
        conn.execute(
            "UPDATE planets SET name = ?, climate = ?, terrain = ? WHERE id = ?",
            (
                input.get("name", planet["name"]),
                input.get("climate", planet["climate"]),
                input.get("terrain", planet["terrain"]),
                input["id"],
            ),
        )
        conn.commit()
        updated_planet = conn.execute("SELECT id, name, climate, terrain FROM planets WHERE id = ?", (input["id"],)).fetchone()
        return dict(updated_planet)
    except sqlite3.IntegrityError:
        conn.rollback()
        raise Exception("Nama planet sudah digunakan.")
    finally:
        conn.close()

@mutation.field("deletePlanet")
def resolve_delete_planet(_, info, id):
    conn = get_db_connection()
    try:
        planet = conn.execute("SELECT id FROM planets WHERE id = ?", (id,)).fetchone()
        if not planet:
            raise Exception(f"Planet dengan ID {id} tidak ditemukan.")
        residents = conn.execute("SELECT COUNT(*) FROM characters WHERE home_planet_id = ?", (id,)).fetchone()[0]
        if residents > 0:
            raise Exception(f"Tidak dapat menghapus planet dengan {residents} penduduk.")
        conn.execute("DELETE FROM planets WHERE id = ?", (id,))
        conn.commit()
        return True
    finally:
        conn.close()

@mutation.field("createCharacter")
def resolve_create_character(_, info, input):
    conn = get_db_connection()
    try:
        if input.get("homePlanetId"):
            planet = conn.execute("SELECT id FROM planets WHERE id = ?", (input["homePlanetId"],)).fetchone()
            if not planet:
                raise Exception(f"Planet dengan ID {input['homePlanetId']} tidak ditemukan.")
        if input.get("affiliationId"):
            affiliation = conn.execute("SELECT id FROM affiliations WHERE id = ?", (input["affiliationId"],)).fetchone()
            if not affiliation:
                raise Exception(f"Afiliatif dengan ID {input['affiliationId']} tidak ditemukan.")
        if input.get("rankId"):
            rank = conn.execute("SELECT id FROM ranks WHERE id = ?", (input["rankId"],)).fetchone()
            if not rank:
                raise Exception(f"Jabatan dengan ID {input['rankId']} tidak ditemukan.")
        conn.execute(
            """
            INSERT INTO characters (name, species, home_planet_id, affiliation_id, rank_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                input["name"],
                input.get("species"),
                input.get("homePlanetId"),
                input.get("affiliationId"),
                input.get("rankId"),
            ),
        )
        conn.commit()
        char_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        character = conn.execute(
            "SELECT * FROM characters WHERE id = ?", (char_id,)
        ).fetchone()
        return dict(character)
    finally:
        conn.close()

@mutation.field("assignStarship")
def resolve_assign_starship(_, info, input):
    conn = get_db_connection()
    try:
        character = conn.execute("SELECT id FROM characters WHERE id = ?", (input["characterId"],)).fetchone()
        starship = conn.execute("SELECT id FROM starships WHERE id = ?", (input["starshipId"],)).fetchone()
        if not character:
            raise Exception(f"Karakter dengan ID {input['characterId']} tidak ditemukan.")
        if not starship:
            raise Exception(f"Kapal dengan ID {input['starshipId']} tidak ditemukan.")
        conn.execute(
            "INSERT OR IGNORE INTO character_starships (character_id, starship_id) VALUES (?, ?)",
            (input["characterId"], input["starshipId"]),
        )
        conn.commit()
        character = conn.execute(
            "SELECT id, name, species, home_planet_id FROM characters WHERE id = ?",
            (input["characterId"],),
        ).fetchone()
        return dict(character)
    finally:
        conn.close()

@mutation.field("updateCharacter")
def resolve_update_character(_, info, input):
    conn = get_db_connection()
    try:
        character = conn.execute("SELECT * FROM characters WHERE id = ?", (input["id"],)).fetchone()
        if not character:
            raise Exception(f"Karakter dengan ID {input['id']} tidak ditemukan.")

        if input.get("homePlanetId"):
            planet = conn.execute("SELECT id FROM planets WHERE id = ?", (input["homePlanetId"],)).fetchone()
            if not planet:
                raise Exception(f"Planet dengan ID {input['homePlanetId']} tidak ditemukan.")
        if input.get("affiliationId"):
            affiliation = conn.execute("SELECT id FROM affiliations WHERE id = ?", (input["affiliationId"],)).fetchone()
            if not affiliation:
                raise Exception(f"Afiliatif dengan ID {input['affiliationId']} tidak ditemukan.")
        if input.get("rankId"):
            rank = conn.execute("SELECT id FROM ranks WHERE id = ?", (input["rankId"],)).fetchone()
            if not rank:
                raise Exception(f"Jabatan dengan ID {input['rankId']} tidak ditemukan.")
        conn.execute(
            """
            UPDATE characters 
            SET name = ?, species = ?, home_planet_id = ?, affiliation_id = ?, rank_id = ?
            WHERE id = ?
            """,
            (
                input.get("name", character["name"]),
                input.get("species", character["species"]),
                input.get("homePlanetId", character["home_planet_id"]),
                input.get("affiliationId", character["affiliation_id"]),
                input.get("rankId", character["rank_id"]),
                input["id"],
            ),
        )
        conn.commit()
        updated_char = conn.execute(
            "SELECT id, name, species, home_planet_id,affiliation_id, rank_id FROM characters WHERE id = ?", (input["id"],)
        ).fetchone()
        return dict(updated_char)
    finally:
        conn.close()

@mutation.field("deleteCharacter")
def resolve_delete_character(_, info, id):
    conn = get_db_connection()
    try:
        character = conn.execute("SELECT id FROM characters WHERE id = ?", (id,)).fetchone()
        if not character:
            raise Exception(f"Karakter dengan ID {id} tidak ditemukan.")
        conn.execute("DELETE FROM characters WHERE id = ?", (id,))
        conn.commit()
        return True
    finally:
        conn.close()

@mutation.field("updateStarship")
def resolve_update_starship(_, info, input):
    conn = get_db_connection()
    try:
        starship = conn.execute("SELECT * FROM starships WHERE id = ?", (input["id"],)).fetchone()
        if not starship:
            raise Exception(f"Kapal dengan ID {input['id']} tidak ditemukan.")
        conn.execute(
            "UPDATE starships SET name = ?, model = ?, manufacturer = ? WHERE id = ?",
            (
                input.get("name", starship["name"]),
                input.get("model", starship["model"]),
                input.get("manufacturer", starship["manufacturer"]),
                input["id"],
            ),
        )
        conn.commit()
        updated_starship = conn.execute(
            "SELECT id, name, model, manufacturer FROM starships WHERE id = ?", (input["id"],)
        ).fetchone()
        return dict(updated_starship)
    finally:
        conn.close()

@mutation.field("deleteStarship")
def resolve_delete_starship(_, info, id):
    conn = get_db_connection()
    try:
        starship = conn.execute("SELECT id FROM starships WHERE id = ?", (id,)).fetchone()
        if not starship:
            raise Exception(f"Kapal dengan ID {id} tidak ditemukan.")
        conn.execute("DELETE FROM starships WHERE id = ?", (id,))
        conn.commit()
        return True
    finally:
        conn.close()

@mutation.field("assignAffiliation")
def resolve_assign_affiliation(_, info, input):
    conn = get_db_connection()
    try:
        character = conn.execute("SELECT id FROM characters WHERE id = ?", (input["characterId"],)).fetchone()
        affiliation = conn.execute("SELECT id FROM affiliations WHERE id = ?", (input["affiliationId"],)).fetchone()
        if not character:
            raise Exception(f"Karakter dengan ID {input['characterId']} tidak ditemukan.")
        if not affiliation:
            raise Exception(f"Afiliatif dengan ID {input['affiliationId']} tidak ditemukan.")
        conn.execute(
            "UPDATE characters SET affiliation_id = ? WHERE id = ?",
            (input["affiliationId"], input["characterId"]),
        )
        conn.commit()
        updated_character = conn.execute(
            "SELECT id, name, species, home_planet_id, affiliation_id, rank_id FROM characters WHERE id = ?",
            (input["characterId"],),
        ).fetchone()
        return dict(updated_character)
    finally:
        conn.close()

@mutation.field("assignRank")
def resolve_assign_rank(_, info, input):
    conn = get_db_connection()
    try:
        character = conn.execute("SELECT id FROM characters WHERE id = ?", (input["characterId"],)).fetchone()
        rank = conn.execute("SELECT id FROM ranks WHERE id = ?", (input["rankId"],)).fetchone()
        if not character:
            raise Exception(f"Karakter dengan ID {input['characterId']} tidak ditemukan.")
        if not rank:
            raise Exception(f"Jabatan dengan ID {input['rankId']} tidak ditemukan.")
        conn.execute(
            "UPDATE characters SET rank_id = ? WHERE id = ?",
            (input["rankId"], input["characterId"]),
        )
        conn.commit()
        updated_character = conn.execute(
            "SELECT id, name, species, home_planet_id, affiliation_id, rank_id FROM characters WHERE id = ?",
            (input["characterId"],),
        ).fetchone()
        return dict(updated_character)
    finally:
        conn.close()

resolvers = [query, mutation, character_type, planet_type, starship_type]