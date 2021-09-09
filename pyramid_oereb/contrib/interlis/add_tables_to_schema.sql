/* TABLE datenintegration*/

CREATE TABLE IF NOT EXISTS :schema.datenintegration
(
    t_id bigint NOT NULL,
    datum timestamp without time zone NOT NULL,
    amt bigint NOT NULL,
    checksum character varying COLLATE pg_catalog."default",
    CONSTRAINT datenintegration_pkey PRIMARY KEY (t_id),
    CONSTRAINT datenintegration_amt_fkey FOREIGN KEY (amt)
        REFERENCES :schema.amt (t_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE :schema.datenintegration
    OWNER to :usr;


/* TABLE verfuegbarkeit */

CREATE TABLE IF NOT EXISTS :schema.verfuegbarkeit
(
    bfsnr int NOT NULL,
    verfuegbar boolean NOT NULL,
    CONSTRAINT verfuegbarkeit_pkey PRIMARY KEY (bfsnr)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE :schema.verfuegbarkeit
    OWNER to :usr;