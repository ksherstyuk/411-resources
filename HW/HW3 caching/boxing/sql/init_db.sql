DROP TABLE IF EXISTS boxers;
CREATE TABLE boxers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    weight FLOAT NOT NULL CHECK(weight >= 125),
    height FLOAT NOT NULL CHECK(height > 0),
    reach FLOAT NOT NULL CHECK(reach > 0),
    age INTEGER NOT NULL CHECK(age >= 18 AND age <= 40),
    fights INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    UNIQUE(name)
);

/*BELOW INDEXES ARE WRONG!!!!!*/
CREATE INDEX idx_songs_artist_title ON songs(artist, title);
CREATE INDEX idx_songs_year ON songs(year);
CREATE INDEX idx_songs_play_count ON songs(play_count);