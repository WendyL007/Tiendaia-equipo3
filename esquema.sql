create table consultas (
    id bigserial primary key,
    creado timestamptz not null default now(),
    ciudad text not null,
    temperatura_c real,
    descripcion text,
    recomendacion text
);

alter table consultas enable row level security;
