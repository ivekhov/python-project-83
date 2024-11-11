CREATE TABLE urls (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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