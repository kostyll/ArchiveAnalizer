BEGIN TRANSACTION;
CREATE TABLE archiv (
                    id INTEGER PRIMARY KEY,
                    file TEXT,
                    disk TEXT,
                    date TEXT,
                    hour INTEGER,
                    rec INTEGER,
                    cam INTEGER,
                    size INTEGER,
                    date_in_file TEXT,
                    time_in_file TEXT
                    );
COMMIT;
