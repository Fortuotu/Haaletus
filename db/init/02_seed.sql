-- 11 eelnevalt andmebaasi kantud hääletajat
INSERT INTO INIMESED (eesnimi, perenimi) VALUES
    ('Mari',    'Tamm'),
    ('Jaan',    'Kask'),
    ('Kadri',   'Saar'),
    ('Toomas',  'Kuusk'),
    ('Liis',    'Rebane'),
    ('Andres',  'Pärn'),
    ('Kristi',  'Lepik'),
    ('Margus',  'Ilves'),
    ('Piret',   'Mägi'),
    ('Rein',    'Karu'),
    ('Triin',   'Oja')
ON DUPLICATE KEY UPDATE eesnimi = VALUES(eesnimi);
