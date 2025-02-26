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

CREATE SEQUENCE estatisticas_visitantes_id_seq;
ALTER TABLE estatisticas_visitantes ALTER COLUMN id SET DEFAULT nextval('estatisticas_visitantes_id_seq');
SELECT setval('estatisticas_visitantes_id_seq', COALESCE(MAX(id), 1)) FROM estatisticas_visitantes;
ALTER TABLE estatisticas_visitantes ADD PRIMARY KEY (id);

CREATE SEQUENCE estatisticas_mandantes_id_seq;
ALTER TABLE estatisticas_mandantes ALTER COLUMN id SET DEFAULT nextval('estatisticas_mandantes_id_seq');
SELECT setval('estatisticas_mandantes_id_seq', COALESCE(MAX(id), 1)) FROM estatisticas_mandantes;
ALTER TABLE estatisticas_mandantes ADD PRIMARY KEY (id);

ALTER TABLE cartoes ADD CONSTRAINT fk_cartoes_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);

ALTER TABLE gols ADD CONSTRAINT fk_gols_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);

ALTER TABLE estatisticas_visitantes ADD CONSTRAINT fk_estatisticas_visitantes_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);

ALTER TABLE estatisticas_mandantes ADD CONSTRAINT fk_estatisticas_mandantes_partida_id FOREIGN KEY (partida_id) REFERENCES partidas(id);


-- Quero que faça a conversão de todos os campos para inteiros
ALTER TABLE estatisticas_visitantes ALTER COLUMN rodada TYPE INTEGER USING rodada::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN chutes TYPE INTEGER USING chutes::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN chutes_no_alvo TYPE INTEGER USING chutes_no_alvo::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN passes TYPE INTEGER USING passes::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN faltas TYPE INTEGER USING faltas::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN cartao_amarelo TYPE INTEGER USING cartao_amarelo::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN cartao_vermelho TYPE INTEGER USING cartao_vermelho::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN impedimentos TYPE INTEGER USING impedimentos::integer;
ALTER TABLE estatisticas_visitantes ALTER COLUMN escanteios TYPE INTEGER USING escanteios::integer;

ALTER TABLE estatisticas_mandantes ALTER COLUMN rodada TYPE INTEGER USING rodada::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN chutes TYPE INTEGER USING chutes::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN chutes_no_alvo TYPE INTEGER USING chutes_no_alvo::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN passes TYPE INTEGER USING passes::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN faltas TYPE INTEGER USING faltas::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN cartao_amarelo TYPE INTEGER USING cartao_amarelo::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN cartao_vermelho TYPE INTEGER USING cartao_vermelho::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN impedimentos TYPE INTEGER USING impedimentos::integer;
ALTER TABLE estatisticas_mandantes ALTER COLUMN escanteios TYPE INTEGER USING escanteios::integer;

ALTER TABLE cartoes ALTER COLUMN rodada TYPE INTEGER USING rodada::integer;
ALTER TABLE cartoes ALTER COLUMN num_camisa TYPE INTEGER USING num_camisa::integer;

ALTER TABLE gols ALTER COLUMN rodada TYPE INTEGER USING rodada::integer;

ALTER TABLE partidas ALTER COLUMN rodada TYPE INTEGER USING rodada::integer;
ALTER TABLE partidas ALTER COLUMN mandante_placar TYPE INTEGER USING  mandante_placar::integer;
ALTER TABLE partidas ALTER COLUMN visitante_placar TYPE INTEGER USING  visitante_placar::integer;