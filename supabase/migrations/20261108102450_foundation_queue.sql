-- Private PGMQ queue. Do not expose pgmq or pgmq_public through the Data API.
-- The worker connects with DATABASE_URL, a server credential, and is not a client role.

create extension if not exists pgmq;

select pgmq.create('jobs');

revoke all on schema pgmq from anon, authenticated;
alter table pgmq.q_jobs enable row level security;
alter table pgmq.a_jobs enable row level security;
revoke all on table pgmq.q_jobs from anon, authenticated;
revoke all on table pgmq.a_jobs from anon, authenticated;

create schema if not exists infra;

revoke all on schema infra from public, anon, authenticated;

create table infra.api_idempotency_keys (
  user_id uuid not null references auth.users (id) on delete cascade,
  idempotency_key text not null,
  message_id bigint not null,
  created_at timestamptz not null default pg_catalog.now(),
  primary key (user_id, idempotency_key),
  constraint api_idempotency_keys_key_length check (char_length(idempotency_key) between 8 and 128)
);

create table infra.job_receipts (
  message_id bigint primary key,
  idempotency_key text not null,
  job_type text not null,
  processed_at timestamptz not null default pg_catalog.now(),
  constraint job_receipts_key_length check (char_length(idempotency_key) between 8 and 128),
  constraint job_receipts_type_length check (char_length(job_type) between 1 and 64)
);

alter table infra.api_idempotency_keys enable row level security;
alter table infra.job_receipts enable row level security;

revoke all on table infra.api_idempotency_keys from public, anon, authenticated, service_role;
revoke all on table infra.job_receipts from public, anon, authenticated, service_role;
