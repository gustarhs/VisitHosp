CREATE DATABASE IF NOT EXISTS db_visithosp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE db_visithosp;

-- ------------------------------------------------------------
-- Entidades independentes (sem FK de entrada)
-- ------------------------------------------------------------

CREATE TABLE visitante (
    id                  INT          PRIMARY KEY NOT NULL AUTO_INCREMENT,
    status              BOOL         NOT NULL,
    tipo                VARCHAR(20)  NOT NULL,
    nome                VARCHAR(150) NOT NULL,
    data_nascimento     DATETIME     NOT NULL,
    termo_consentimento BOOL         NOT NULL,
    cpf                 VARCHAR(20)  UNIQUE NOT NULL
);

CREATE TABLE hospital (
    id              INT          PRIMARY KEY NOT NULL AUTO_INCREMENT,
    horario_visita  DATETIME     NOT NULL,
    nome            VARCHAR(150) NOT NULL,
    -- endereço composto (rua, número, cidade, estado)
    rua             VARCHAR(150) NOT NULL,
    numero          VARCHAR(20)  NOT NULL,
    cidade          VARCHAR(100) NOT NULL,
    estado          VARCHAR(50)  NOT NULL
);

CREATE TABLE paciente (
    id              INT          PRIMARY KEY NOT NULL AUTO_INCREMENT,
    data_nascimento DATETIME     NOT NULL,
    tipo            VARCHAR(20)  NOT NULL,
    status          BOOL         NOT NULL,
    nome            VARCHAR(150) NOT NULL,
    cpf             VARCHAR(20)  UNIQUE NOT NULL
);

CREATE TABLE leito (
    id      INT         PRIMARY KEY NOT NULL AUTO_INCREMENT,
    status  BOOL        NOT NULL,
    ala     VARCHAR(20) NOT NULL,
    numero  INT         NOT NULL,
    andar   INT         NOT NULL,
    bloco   VARCHAR(20) NOT NULL
);

CREATE TABLE triagem (
    id          INT         PRIMARY KEY NOT NULL AUTO_INCREMENT,
    data_hora   DATETIME    NOT NULL,
    resultado   BOOL        NOT NULL,
    perguntas   LONGTEXT    NOT NULL,
    respostas   LONGTEXT    NOT NULL
);

-- ------------------------------------------------------------
-- Internação — depende de Paciente (1:N) e Leito (1:N)
-- ------------------------------------------------------------

CREATE TABLE internacao (
    id              INT         PRIMARY KEY NOT NULL AUTO_INCREMENT,
    data_entrada    DATETIME    NOT NULL,
    data_saida      DATETIME    NOT NULL,
    status          BOOL        NOT NULL,
    token_acesso    VARCHAR(20) NOT NULL,
    -- Paciente possui N internações  →  1:N 
    id_paciente     INT         NOT NULL,
    -- Internação ocupa 1 Leito  →  1:N  
    id_leito        INT         NOT NULL,
    CONSTRAINT fk_internacao_paciente
        FOREIGN KEY (id_paciente) REFERENCES paciente(id),
    CONSTRAINT fk_internacao_leito
        FOREIGN KEY (id_leito)    REFERENCES leito(id)
);

CREATE TABLE visita (
    id              INT         PRIMARY KEY NOT NULL AUTO_INCREMENT,
    data_hora       DATETIME    NOT NULL,
    status          BOOL        NOT NULL,
    qr_code         VARCHAR(100) UNIQUE NOT NULL,
    -- Visitante realiza N visitas  →  1:N  
    id_visitante    INT         NOT NULL,
    -- Hospital possui N visitas    →  1:N  
    id_hospital     INT         NOT NULL,
    -- Visita recebe 1 Internação   →  M:1  
    id_internacao   INT,
    -- Visita possui 1 Triagem      →  1:1  
    id_triagem      INT         UNIQUE,
    CONSTRAINT fk_visita_visitante
        FOREIGN KEY (id_visitante)  REFERENCES visitante(id),
    CONSTRAINT fk_visita_hospital
        FOREIGN KEY (id_hospital)   REFERENCES hospital(id),
    CONSTRAINT fk_visita_internacao
        FOREIGN KEY (id_internacao) REFERENCES internacao(id),
    CONSTRAINT fk_visita_triagem
        FOREIGN KEY (id_triagem)    REFERENCES triagem(id)
);
