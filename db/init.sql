-- postgres 컨테이너의 데이터 폴더가 "비어 있을 때만" 한 번 실행된다.
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    user_name   TEXT        NOT NULL,
    page        TEXT        NOT NULL,
    device      TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
