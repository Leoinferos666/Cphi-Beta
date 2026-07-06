-- Plastic Limit Test Tables

CREATE TABLE plastic_limit_trials (
    id SERIAL PRIMARY KEY,
    trial_no INT NOT NULL,
    container_no INT NOT NULL,
    W1 FLOAT NOT NULL,
    W2 FLOAT NOT NULL,
    W3 FLOAT NOT NULL,
    water_weight FLOAT,
    dry_soil_weight FLOAT,
    moisture_content FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plastic_limit_reviews (
    id SERIAL PRIMARY KEY,
    trial_id INT REFERENCES plastic_limit_trials(id),
    average_moisture_content FLOAT,
    comments TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
