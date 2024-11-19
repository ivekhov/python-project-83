DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO urls (name) VALUES 
('https://www.google.com'),
('https://www.yandex.ru'),
('https://www.bing.com'),
('https://www.yahoo.com'),
('https://www.duckduckgo.com'),
('https://www.ask.com'),
('https://www.baidu.com'),
('https://www.aol.com'),
('https://www.wolframalpha.com');


DROP TABLE IF EXISTS url_checks;

CREATE TABLE url_checks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id BIGINT NOT NULL,
    status_code VARCHAR(100),
    h1 TEXT,
    title TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);