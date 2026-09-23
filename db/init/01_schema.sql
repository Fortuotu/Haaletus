-- Hääletussüsteemi andmebaasi skeem
SET NAMES utf8mb4;

-- Eelnevalt kantud hääletajad (11 inimest)
CREATE TABLE IF NOT EXISTS INIMESED (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    eesnimi     VARCHAR(50)  NOT NULL,
    perenimi    VARCHAR(50)  NOT NULL,
    UNIQUE KEY uq_inimene (eesnimi, perenimi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Üks hääletusvoor (kestab 5 minutit, algab kõigile samal ajal)
CREATE TABLE IF NOT EXISTS TULEMUSED (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    h_alguse_aeg     DATETIME     NOT NULL,
    haaletanute_arv  INT          NOT NULL DEFAULT 0,
    poolt_haali      INT          NOT NULL DEFAULT 0,
    vastu_haali      INT          NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hääletaja viimane kehtiv otsus
CREATE TABLE IF NOT EXISTS HAALETUS (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    tulemus_id     INT          NOT NULL,
    inimene_id     INT          NOT NULL,
    eesnimi        VARCHAR(50)  NOT NULL,
    perenimi       VARCHAR(50)  NOT NULL,
    haaletuse_aeg  DATETIME     NOT NULL,
    otsus          ENUM('poolt','vastu') NOT NULL,
    UNIQUE KEY uq_haal (tulemus_id, inimene_id),
    CONSTRAINT fk_haaletus_tulemus FOREIGN KEY (tulemus_id) REFERENCES TULEMUSED(id) ON DELETE CASCADE,
    CONSTRAINT fk_haaletus_inimene FOREIGN KEY (inimene_id) REFERENCES INIMESED(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kõik muutused hääletamisel, kellaajaliselt (tõestusmaterjal)
CREATE TABLE IF NOT EXISTS LOGI (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    aeg         DATETIME(3)  NOT NULL,
    tulemus_id  INT          NULL,
    inimene_id  INT          NULL,
    eesnimi     VARCHAR(50)  NULL,
    perenimi    VARCHAR(50)  NULL,
    tegevus     VARCHAR(30)  NOT NULL,
    vana_otsus  ENUM('poolt','vastu') NULL,
    uus_otsus   ENUM('poolt','vastu') NULL,
    markus      VARCHAR(255) NULL,
    KEY idx_logi_aeg (aeg)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
