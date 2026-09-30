SET NAMES utf8mb4;

CREATE OR REPLACE TRIGGER trg_haaletus_lisamine
AFTER INSERT ON HAALETUS
FOR EACH ROW
    INSERT INTO LOGI (aeg, tulemus_id, inimene_id, eesnimi, perenimi, tegevus, vana_otsus, uus_otsus)
    VALUES (UTC_TIMESTAMP(3), NEW.tulemus_id, NEW.inimene_id, NEW.eesnimi, NEW.perenimi,
            'HAAL_ANTUD', NULL, NEW.otsus);

CREATE OR REPLACE TRIGGER trg_haaletus_muutmine
AFTER UPDATE ON HAALETUS
FOR EACH ROW
    INSERT INTO LOGI (aeg, tulemus_id, inimene_id, eesnimi, perenimi, tegevus, vana_otsus, uus_otsus)
    VALUES (UTC_TIMESTAMP(3), NEW.tulemus_id, NEW.inimene_id, NEW.eesnimi, NEW.perenimi,
            'HAAL_MUUDETUD', OLD.otsus, NEW.otsus);
