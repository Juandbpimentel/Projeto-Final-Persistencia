CREATE SEQUENCE gols_id_seq;
ALTER TABLE gols ALTER COLUMN id SET DEFAULT nextval('gols_id_seq');
SELECT setval('gols_id_seq', COALESCE(MAX(id), 1)) FROM gols;
ALTER TABLE gols ADD PRIMARY KEY (id);

CREATE SEQUENCE cartoes_id_seq;
ALTER TABLE cartoes ALTER COLUMN id SET DEFAULT nextval('cartoes_id_seq');
SELECT setval('cartoes_id_seq', COALESCE(MAX(id), 1)) FROM cartoes;
ALTER TABLE cartoes ADD PRIMARY KEY (id);

CREATE SEQUENCE partidas_id_seq;
ALTER TABLE partidas ALTER COLUMN id SET DEFAULT nextval('partidas_id_seq');
SELECT setval('partidas_id_seq', COALESCE(MAX(id), 1)) FROM partidas;
ALTER TABLE partidas ADD PRIMARY KEY (id);

CREATE SEQUENCE estatisticas_visitante_id_seq;
ALTER TABLE estatisticas_visitante ALTER COLUMN id SET DEFAULT nextval('estatisticas_visitante_id_seq');
SELECT setval('estatisticas_visitante_id_seq', COALESCE(MAX(id), 1)) FROM estatisticas_visitante;
ALTER TABLE estatisticas_visitante ADD PRIMARY KEY (id);

CREATE SEQUENCE estatisticas_mandante_id_seq;
ALTER TABLE estatisticas_mandante ALTER COLUMN id SET DEFAULT nextval('estatisticas_mandante_id_seq');
SELECT setval('estatisticas_mandante_id_seq', COALESCE(MAX(id), 1)) FROM estatisticas_mandante;
ALTER TABLE estatisticas_mandante ADD PRIMARY KEY (id);

ALTER TABLE cartoes ADD CONSTRAINT fk_cartoes_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);

ALTER TABLE gols ADD CONSTRAINT fk_gols_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);

ALTER TABLE estatisticas_visitante ADD CONSTRAINT fk_estatisticas_visitante_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);

ALTER TABLE estatisticas_mandante ADD CONSTRAINT fk_estatisticas_mandante_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);