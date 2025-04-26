DROP TABLE IF EXISTS movies;
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_year INTEGER NOT NULL CHECK(release_year >= 1900),
    popularity FLOAT NOT NULL,
    runtime INTEGER NOT NULL CHECK(runtime > 0),
    average_vote FLOAT NOT NULL CHECK(0 < average_vote < 10),
    UNIQUE(title, release_year)
);

CREATE INDEX idx_movies_release_year_title ON movies(release_year, title);
CREATE INDEX idx_movies_popularity ON movies(popularity);
CREATE INDEX idx_movies_average_vote ON movies(average_vote);