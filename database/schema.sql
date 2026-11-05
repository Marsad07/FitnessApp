-- Griot Fitness - creates every table the app needs on a fresh MySQL database
-- Generated from the SQLAlchemy models in app/models
-- Run it once in MySQL Workbench (or the mysql command line) before starting the app

CREATE DATABASE IF NOT EXISTS fitnessapp_db;
USE fitnessapp_db;

CREATE TABLE user_accounts (
    id INTEGER NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
);

CREATE TABLE logged_entries (
    id INTEGER NOT NULL AUTO_INCREMENT,
    fdc_id INTEGER,
    user_id INTEGER NOT NULL,
    food_name VARCHAR(255),
    food_weight DECIMAL(6, 2),
    calories DECIMAL(6, 2),
    protein DECIMAL(6, 2),
    carbs DECIMAL(6, 2),
    fats DECIMAL(6, 2),
    meal_category VARCHAR(255),
    logged_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES user_accounts (id) ON DELETE CASCADE
);

CREATE TABLE nutrition (
    id INTEGER NOT NULL AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    calories_goal DECIMAL(6, 2),
    protein_goal DECIMAL(6, 2),
    carbs_goal DECIMAL(6, 2),
    fats_goal DECIMAL(6, 2),
    PRIMARY KEY (id),
    UNIQUE (user_id),
    FOREIGN KEY(user_id) REFERENCES user_accounts (id) ON DELETE CASCADE
);

CREATE TABLE food_cache (
    id INTEGER NOT NULL AUTO_INCREMENT,
    search_term VARCHAR(255) NOT NULL,
    results TEXT NOT NULL,
    cached_at DATETIME,
    PRIMARY KEY (id),
    UNIQUE (search_term)
);
