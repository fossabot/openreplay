DO
$$
    DECLARE
        previous_version CONSTANT text := 'v1.12.0';
        next_version     CONSTANT text := 'v1.13.0';
    BEGIN
        IF (SELECT openreplay_version()) = previous_version THEN
            raise notice 'valid previous DB version';
        ELSEIF (SELECT openreplay_version()) = next_version THEN
            raise notice 'new version detected, nothing to do';
        ELSE
            RAISE EXCEPTION 'upgrade to % failed, invalid previous version, expected %, got %', next_version,previous_version,(SELECT openreplay_version());
        END IF;
    END ;
$$
LANGUAGE plpgsql;

BEGIN;
CREATE OR REPLACE FUNCTION openreplay_version()
    RETURNS text AS
$$
SELECT 'v1.13.0'
$$ LANGUAGE sql IMMUTABLE;

CREATE TABLE IF NOT EXISTS public.feature_flags
(
    feature_flag_id     integer generated BY DEFAULT AS IDENTITY,
    project_id          integer         NOT NULL,
    name                text            NOT NULL,
    flag_key            text            NOT NULL,
    description         text            NOT NULL,
    flag_type           text            NOT NULL,
    is_persist          boolean         NOT NULL DEFAULT FALSE,
    is_active           boolean         NOT NULL DEFAULT FALSE,
    created_by          integer         NOT NULL,
    updated_by          integer NULL    DEFAULT NULL,
    created_at          timestamp       default (now() AT TIME ZONE 'utc'::text),
    updated_at          timestamp NULL  default (now() AT TIME ZONE 'utc'::text),
    deleted_at          timestamp NULL  DEFAULT NULL,
    primary key (feature_flag_id, created_at),
    unique (project_id, flag_key)
);

CREATE INDEX idx_feature_flags_project_id ON public.feature_flags (project_id);


CREATE TABLE IF NOT EXISTS public.feature_flags
(
    feature_flag_id     integer     NOT NULL,
    name                text        NOT NULL,
    rollout_percentage  integer     NOT NULL,
    conditions          jsonb       NOT NULL,
);

COMMIT;