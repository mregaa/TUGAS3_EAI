from database import get_db_connection, init_db

def seed_data():
    """Mengisi database dengan data awal Star Wars."""
    conn = get_db_connection()
    c = conn.cursor()

    # Bersihkan data lama
    c.execute("DELETE FROM character_starships")
    c.execute("DELETE FROM characters")
    c.execute("DELETE FROM starships")
    c.execute("DELETE FROM planets")
    c.execute("DELETE FROM affiliations")
    c.execute("DELETE FROM ranks")
    conn.commit()

    # Data planet
    planets = [
        ("Tatooine", "Arid", "Desert"),
        ("Alderaan", "Temperate", "Grasslands, Mountains"),
        ("Yavin IV", "Temperate, Humid", "Jungle, Rainforests"),
        ("Naboo", "Temperate", "Grassy Hills, Swamps"),
        ("Coruscant", "Temperate", "Cityscape"),
    ]
    c.executemany("INSERT INTO planets (name, climate, terrain) VALUES (?, ?, ?)", planets)
    planet_ids = {row["name"]: row["id"] for row in c.execute("SELECT id, name FROM planets").fetchall()}

    # Data affiliation
    affiliations = [
        ("Rebel Alliance",),
        ("Galactic Empire",),
        ("Jedi Order",),
        ("Independent",),
    ]
    c.executemany("INSERT INTO affiliations (name) VALUES (?)", affiliations)
    affiliation_ids = {row["name"]: row["id"] for row in c.execute("SELECT id, name FROM affiliations").fetchall()}

    # Data rank
    ranks = [
        ("General",),
        ("Captain",),
        ("Jedi Master",),
        ("Droid",),
        ("Smuggler",),
    ]
    c.executemany("INSERT INTO ranks (name) VALUES (?)", ranks)
    rank_ids = {row["name"]: row["id"] for row in c.execute("SELECT id, name FROM ranks").fetchall()}

    # Data karakter (dengan kolom affiliation dan rank)
    characters = [
        ("Luke Skywalker", "Human", planet_ids["Tatooine"], affiliation_ids["Jedi Order"], rank_ids["Jedi Master"]),
        ("Leia Organa", "Human", planet_ids["Alderaan"], affiliation_ids["Rebel Alliance"], rank_ids["General"]),
        ("Han Solo", "Human", None, affiliation_ids["Independent"], rank_ids["Smuggler"]),
        ("C-3PO", "Droid", None, None, rank_ids["Droid"]),
        ("Yoda", "Unknown", None, affiliation_ids["Jedi Order"], rank_ids["Jedi Master"]),
    ]
    c.executemany(
        "INSERT INTO characters (name, species, home_planet_id, affiliation_id, rank_id) VALUES (?, ?, ?, ?, ?)",
        characters
    )
    character_ids = {row["name"]: row["id"] for row in c.execute("SELECT id, name FROM characters").fetchall()}

    # Data kapal
    starships = [
        ("Millennium Falcon", "YT-1300 light freighter", "Corellian Engineering"),
        ("X-wing", "T-65 X-wing starfighter", "Incom Corporation"),
        ("TIE Fighter", "TIE/LN starfighter", "Sienar Fleet Systems"),
    ]
    c.executemany("INSERT INTO starships (name, model, manufacturer) VALUES (?, ?, ?)", starships)
    starship_ids = {row["name"]: row["id"] for row in c.execute("SELECT id, name FROM starships").fetchall()}

    # Relasi karakter-kapal
    character_starships = [
        (character_ids["Han Solo"], starship_ids["Millennium Falcon"]),
        (character_ids["Luke Skywalker"], starship_ids["X-wing"]),
    ]
    c.executemany("INSERT INTO character_starships (character_id, starship_id) VALUES (?, ?)", character_starships)

    conn.commit()
    conn.close()
    print("Database berhasil diisi dengan data Star Wars!")

if __name__ == "__main__":
    init_db()  # Pastikan tabel ada
    seed_data()
