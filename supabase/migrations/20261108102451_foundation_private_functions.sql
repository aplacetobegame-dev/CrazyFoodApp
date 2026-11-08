-- Service-role entry points. Queue functions stay unreachable to anon and authenticated.

create or replace function private.enqueue_echo(p_user_id uuid, p_idempotency_key text)
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  existing_id bigint;
  new_id bigint;
  payload jsonb;
begin
  if p_user_id is null
    or p_idempotency_key is null
    or char_length(p_idempotency_key) < 8
    or char_length(p_idempotency_key) > 128 then
    raise exception 'invalid enqueue request' using errcode = '22023';
  end if;

  select keys.message_id
  into existing_id
  from infra.api_idempotency_keys as keys
  where keys.user_id = p_user_id
    and keys.idempotency_key = p_idempotency_key;

  if existing_id is not null then
    return existing_id;
  end if;

  payload := pg_catalog.jsonb_build_object(
    'type', 'echo',
    'idempotencyKey', p_idempotency_key,
    'payload', pg_catalog.jsonb_build_object(
      'idempotencyKey', p_idempotency_key,
      'requestedBy', p_user_id
    )
  );

  select pgmq.send('jobs', payload) into new_id;

  insert into infra.api_idempotency_keys (user_id, idempotency_key, message_id)
  values (p_user_id, p_idempotency_key, new_id);

  return new_id;
exception
  when unique_violation then
    select keys.message_id
    into existing_id
    from infra.api_idempotency_keys as keys
    where keys.user_id = p_user_id
      and keys.idempotency_key = p_idempotency_key;
    return existing_id;
end;
$$;

create or replace function private.delete_account(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_user_id is null then
    raise exception 'user id is required' using errcode = '22023';
  end if;

  delete from auth.users
  where id = p_user_id;
end;
$$;

revoke all on function private.enqueue_echo(uuid, text) from public, anon, authenticated;
revoke all on function private.delete_account(uuid) from public, anon, authenticated;
grant execute on function private.enqueue_echo(uuid, text) to service_role;
grant execute on function private.delete_account(uuid) to service_role;
