-- Trigger functions run as the user who issued the update. Authenticated
-- profile edits need to execute this function, and the private schema is
-- otherwise closed. The body only stamps updated_at.

create or replace function private.set_updated_at()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  new.updated_at = pg_catalog.now();
  return new;
end;
$$;

grant usage on schema private to authenticated;
grant execute on function private.set_updated_at() to authenticated;

revoke all on function private.handle_new_user() from public, anon, authenticated;
revoke all on function private.enqueue_echo(uuid, text) from public, anon, authenticated;
revoke all on function private.delete_account(uuid) from public, anon, authenticated;
