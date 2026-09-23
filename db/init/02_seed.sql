INSERT INTO INIMESED (eesnimi, perenimi) VALUES
    ('Mari',    'Tamm'),
    ('Jaan',    'Kask'),
    ('Kadri',   'Saar'),
    ('Toomas',  'Kuusk'),
    ('Liis',    'Rebane'),
    ('Andres',  'Parn'),
    ('Kristi',  'Lepik'),
    ('Margus',  'Ilves'),
    ('Piret',   'Magi'),
    ('Rein',    'Karu'),
    ('Triin',   'Oja')
ON DUPLICATE KEY UPDATE eesnimi = VALUES(eesnimi);
