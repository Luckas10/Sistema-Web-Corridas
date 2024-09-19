create database db_projeto;
USE db_projeto;

CREATE TABLE tb_eventos (
    eve_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    eve_nome VARCHAR(90),
    eve_data DATE,
    eve_premio TEXT
);

CREATE TABLE tb_usuarios (
    usr_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    usr_nome VARCHAR(90),
    usr_email TEXT,
    usr_senha TEXT,
    usr_idade INT
);

CREATE TABLE tb_corridas (
    cor_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    cor_data DATE,
    cor_tempo TIME,
    cor_distancia TEXT,
    cor_usr_id INT,
    cor_eve_id INT,
    FOREIGN KEY (cor_usr_id) REFERENCES tb_usuarios(usr_id),
    FOREIGN KEY (cor_eve_id) REFERENCES tb_eventos(eve_id)
);
