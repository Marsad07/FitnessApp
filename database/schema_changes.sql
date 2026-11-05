USE fitnessapp_db;

CREATE TABLE food_cache (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    search_term VARCHAR(255) UNIQUE NOT NULL,
    results TEXT NOT NULL,
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE logged_entries DROP FOREIGN KEY fk_user;

ALTER TABLE logged_entries
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) REFERENCES user_accounts(id)
ON DELETE CASCADE;


