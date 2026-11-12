-- Connected recipe flow: daily allowance, fixture jobs, publish, votes,
-- cooked proof, staff review, and clip jobs. Mutations stay in private.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'clips',
  'clips',
  false,
  20971520,
  array['video/mp4']::text[]
)
on conflict (id) do update
set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

create table public.recipes (
  id uuid primary key,
  owner_id uuid not null references auth.users (id) on delete cascade,
  slug text not null unique,
  visibility text not null default 'private' check (visibility in ('private', 'public')),
  title text not null,
  description text not null,
  request jsonb not null,
  document jsonb not null,
  ingredient_text text not null,
  sample_image_key text not null check (sample_image_key in ('rice', 'mac')),
  weirdness integer not null check (weirdness between 0 and 100),
  crime_level integer not null check (crime_level between 0 and 100),
  regret_potential integer not null check (regret_potential between 0 and 100),
  moderation_state text not null default 'approved' check (moderation_state in ('pending', 'approved', 'rejected')),
  published_at timestamptz,
  created_at timestamptz not null default pg_catalog.now(),
  updated_at timestamptz not null default pg_catalog.now(),
  constraint recipes_title_length check (char_length(title) between 1 and 120),
  constraint recipes_public_is_approved check (
    visibility <> 'public' or (published_at is not null and moderation_state = 'approved')
  )
);

create table public.generation_jobs (
  id uuid primary key default pg_catalog.gen_random_uuid(),
  owner_id uuid not null references auth.users (id) on delete cascade,
  idempotency_key text not null,
  status text not null check (status in ('queued', 'processing', 'complete', 'failed')),
  request jsonb not null,
  recipe_id uuid references public.recipes (id) on delete set null,
  error_category text,
  created_at timestamptz not null default pg_catalog.now(),
  updated_at timestamptz not null default pg_catalog.now(),
  unique (owner_id, idempotency_key),
  constraint generation_jobs_key_length check (char_length(idempotency_key) between 8 and 128)
);

create table private.credit_ledger (
  id uuid primary key default pg_catalog.gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  day date not null,
  entry_type text not null check (entry_type in ('reserve', 'consume', 'refund')),
  amount integer not null check (amount between -1 and 1),
  idempotency_key text not null,
  job_id uuid,
  created_at timestamptz not null default pg_catalog.now(),
  unique (user_id, idempotency_key, entry_type)
);

create table public.recipe_votes (
  recipe_id uuid not null references public.recipes (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  verdict text not null check (verdict in ('guilty', 'acquitted')),
  updated_at timestamptz not null default pg_catalog.now(),
  primary key (recipe_id, user_id)
);

create table public.cooked_results (
  id uuid primary key default pg_catalog.gen_random_uuid(),
  recipe_id uuid not null references public.recipes (id) on delete cascade,
  owner_id uuid not null references auth.users (id) on delete cascade,
  original_path text not null,
  public_path text,
  taste_score integer not null check (taste_score between 1 and 5),
  verdict text not null check (char_length(verdict) between 1 and 200),
  moderation_state text not null default 'pending' check (moderation_state in ('pending', 'approved', 'rejected')),
  moderation_note text,
  photo_ready boolean not null default false,
  media_type text,
  idempotency_key text not null,
  created_at timestamptz not null default pg_catalog.now(),
  updated_at timestamptz not null default pg_catalog.now(),
  unique (owner_id, idempotency_key),
  constraint cooked_results_key_length check (char_length(idempotency_key) between 8 and 128)
);

create table public.moderation_reports (
  id uuid primary key default pg_catalog.gen_random_uuid(),
  reporter_id uuid not null references auth.users (id) on delete cascade,
  target_type text not null check (target_type in ('recipe', 'cooked_result')),
  target_id uuid not null,
  reason text not null check (char_length(reason) between 1 and 200),
  review_state text not null default 'open' check (review_state in ('open', 'reviewed')),
  created_at timestamptz not null default pg_catalog.now(),
  unique (reporter_id, target_type, target_id)
);

create table public.user_blocks (
  blocker_id uuid not null references auth.users (id) on delete cascade,
  blocked_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default pg_catalog.now(),
  primary key (blocker_id, blocked_id),
  constraint user_blocks_not_self check (blocker_id <> blocked_id)
);

create table private.staff_users (
  user_id uuid primary key references auth.users (id) on delete cascade,
  created_at timestamptz not null default pg_catalog.now()
);

create table public.clip_jobs (
  id uuid primary key default pg_catalog.gen_random_uuid(),
  owner_id uuid not null references auth.users (id) on delete cascade,
  cooked_result_id uuid not null references public.cooked_results (id) on delete cascade,
  status text not null check (status in ('queued', 'processing', 'ready', 'failed')),
  storage_path text,
  idempotency_key text not null,
  created_at timestamptz not null default pg_catalog.now(),
  updated_at timestamptz not null default pg_catalog.now(),
  unique (owner_id, idempotency_key),
  constraint clip_jobs_key_length check (char_length(idempotency_key) between 8 and 128)
);

create table private.account_deletion_keys (
  user_id uuid not null,
  idempotency_key text not null,
  created_at timestamptz not null default pg_catalog.now(),
  primary key (user_id, idempotency_key)
);

alter table infra.job_receipts add column user_id uuid;
create unique index job_receipts_user_idempotency on infra.job_receipts (user_id, idempotency_key);

create index recipes_owner_created on public.recipes (owner_id, created_at desc);
create index recipes_public_created on public.recipes (created_at desc) where visibility = 'public';
create index cooked_results_recipe on public.cooked_results (recipe_id, created_at desc);

alter table public.recipes enable row level security;
alter table public.generation_jobs enable row level security;
alter table public.recipe_votes enable row level security;
alter table public.cooked_results enable row level security;
alter table public.moderation_reports enable row level security;
alter table public.user_blocks enable row level security;
alter table public.clip_jobs enable row level security;
alter table private.credit_ledger enable row level security;
alter table private.staff_users enable row level security;
alter table private.account_deletion_keys enable row level security;

revoke all on table public.recipes from public, anon, authenticated;
revoke all on table public.generation_jobs from public, anon, authenticated;
revoke all on table public.recipe_votes from public, anon, authenticated;
revoke all on table public.cooked_results from public, anon, authenticated;
revoke all on table public.moderation_reports from public, anon, authenticated;
revoke all on table public.user_blocks from public, anon, authenticated;
revoke all on table public.clip_jobs from public, anon, authenticated;
revoke all on table private.credit_ledger from public, anon, authenticated, service_role;
revoke all on table private.staff_users from public, anon, authenticated, service_role;
revoke all on table private.account_deletion_keys from public, anon, authenticated, service_role;

grant select on table public.recipes to anon, authenticated;

create policy recipes_select_public
  on public.recipes
  for select
  to anon, authenticated
  using (visibility = 'public' and moderation_state = 'approved');

create policy recipes_select_own
  on public.recipes
  for select
  to authenticated
  using (owner_id = (select auth.uid()));

grant select (id, display_name) on table public.profiles to anon;

create policy profiles_select_public_authors
  on public.profiles
  for select
  to anon, authenticated
  using (
    exists (
      select 1
      from public.recipes as recipe
      where recipe.owner_id = profiles.id
        and recipe.visibility = 'public'
        and recipe.moderation_state = 'approved'
    )
  );

create trigger recipes_set_updated_at
  before update on public.recipes
  for each row
  execute function private.set_updated_at();

create trigger generation_jobs_set_updated_at
  before update on public.generation_jobs
  for each row
  execute function private.set_updated_at();

create trigger cooked_results_set_updated_at
  before update on public.cooked_results
  for each row
  execute function private.set_updated_at();

create trigger clip_jobs_set_updated_at
  before update on public.clip_jobs
  for each row
  execute function private.set_updated_at();

create or replace function private.utc_day()
returns date
language sql
stable
security definer
set search_path = ''
as $$
  select (pg_catalog.now() at time zone 'utc')::date;
$$;

create or replace function private.allowance_snapshot(p_user_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  used integer;
begin
  select coalesce(sum(amount), 0)
  into used
  from private.credit_ledger
  where user_id = p_user_id
    and day = private.utc_day()
    and entry_type in ('reserve', 'refund');

  return pg_catalog.jsonb_build_object(
    'freeRemaining', pg_catalog.greatest(0, 3 - used),
    'earnedRemaining', 0,
    'dailyMaximum', 3,
    'resetsAt', (
      (pg_catalog.date_trunc('day', pg_catalog.now() at time zone 'utc') + interval '1 day')
      at time zone 'utc'
    )
  );
end;
$$;

create or replace function private.assert_generation_request(p_request jsonb)
returns void
language plpgsql
immutable
set search_path = ''
as $$
declare
  ingredient jsonb;
  exclusion text;
  included text[];
  servings integer;
  weirdness integer;
begin
  if pg_catalog.jsonb_typeof(p_request) <> 'object' then
    raise exception 'invalid generation request' using errcode = '22023';
  end if;
  servings := (p_request ->> 'servings')::integer;
  weirdness := (p_request ->> 'weirdness')::integer;
  if servings is null or servings < 1 or servings > 12
    or weirdness is null or weirdness < 0 or weirdness > 100
    or pg_catalog.jsonb_typeof(p_request -> 'ingredients') <> 'array'
    or pg_catalog.jsonb_array_length(p_request -> 'ingredients') < 1
    or pg_catalog.jsonb_array_length(p_request -> 'ingredients') > 20
    or pg_catalog.jsonb_typeof(p_request -> 'excludedIngredients') <> 'array'
    or pg_catalog.jsonb_array_length(p_request -> 'excludedIngredients') > 20 then
    raise exception 'invalid generation request' using errcode = '22023';
  end if;

  included := array[]::text[];
  for ingredient in select value from pg_catalog.jsonb_array_elements(p_request -> 'ingredients') as value
  loop
    if pg_catalog.jsonb_typeof(ingredient) <> 'object'
      or char_length(ingredient ->> 'name') < 1
      or char_length(ingredient ->> 'name') > 60
      or (ingredient ? 'quantity' and char_length(ingredient ->> 'quantity') > 40) then
      raise exception 'invalid generation request' using errcode = '22023';
    end if;
    included := array_append(included, lower(ingredient ->> 'name'));
  end loop;

  for exclusion in
    select value
    from pg_catalog.jsonb_array_elements_text(p_request -> 'excludedIngredients') as value
  loop
    if char_length(exclusion) < 1 or char_length(exclusion) > 60 or lower(exclusion) = any (included) then
      raise exception 'invalid generation request' using errcode = '22023';
    end if;
  end loop;
exception
  when invalid_text_representation then
    raise exception 'invalid generation request' using errcode = '22023';
end;
$$;

create or replace function private.enqueue_generation(
  p_user_id uuid,
  p_idempotency_key text,
  p_request jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  existing public.generation_jobs%rowtype;
  used integer;
  new_id uuid;
  message_id bigint;
  payload jsonb;
begin
  if p_user_id is null or p_idempotency_key is null
    or char_length(p_idempotency_key) < 8
    or char_length(p_idempotency_key) > 128 then
    raise exception 'invalid generation request' using errcode = '22023';
  end if;
  perform private.assert_generation_request(p_request);
  perform 1 from public.profiles where id = p_user_id for update;
  if not found then
    raise exception 'profile missing' using errcode = '22023';
  end if;

  select *
  into existing
  from public.generation_jobs
  where owner_id = p_user_id
    and idempotency_key = p_idempotency_key;
  if found then
    return pg_catalog.jsonb_build_object(
      'jobId', existing.id,
      'status', existing.status,
      'recipeId', existing.recipe_id,
      'allowance', private.allowance_snapshot(p_user_id)
    );
  end if;

  select coalesce(sum(amount), 0)
  into used
  from private.credit_ledger
  where user_id = p_user_id
    and day = private.utc_day()
    and entry_type in ('reserve', 'refund');
  if used >= 3 then
    raise exception 'daily_limit' using errcode = 'P0001';
  end if;

  insert into public.generation_jobs (owner_id, idempotency_key, status, request)
  values (p_user_id, p_idempotency_key, 'queued', p_request)
  returning id into new_id;

  insert into private.credit_ledger (user_id, day, entry_type, amount, idempotency_key, job_id)
  values (p_user_id, private.utc_day(), 'reserve', 1, p_idempotency_key, new_id);

  payload := pg_catalog.jsonb_build_object(
    'type', 'generate_recipe',
    'idempotencyKey', p_idempotency_key,
    'payload', pg_catalog.jsonb_build_object(
      'idempotencyKey', p_idempotency_key,
      'requestedBy', p_user_id,
      'jobId', new_id
    )
  );
  select pgmq.send('jobs', payload) into message_id;

  return pg_catalog.jsonb_build_object(
    'jobId', new_id,
    'status', 'queued',
    'recipeId', null,
    'allowance', private.allowance_snapshot(p_user_id)
  );
end;
$$;

create or replace function private.complete_generation(p_job_id uuid, p_document jsonb)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  job public.generation_jobs%rowtype;
  image_key text;
  ingredient_text text;
begin
  select * into job from public.generation_jobs where id = p_job_id for update;
  if not found then
    raise exception 'job not found' using errcode = 'P0002';
  end if;
  if job.status in ('complete', 'failed') then
    return;
  end if;
  image_key := p_document ->> 'sampleImageKey';
  if coalesce(p_document ->> 'title', '') = ''
    or image_key not in ('rice', 'mac')
    or pg_catalog.jsonb_typeof(p_document -> 'steps') <> 'array'
    or pg_catalog.jsonb_typeof(p_document -> 'ingredients') <> 'array' then
    raise exception 'invalid recipe document' using errcode = '22023';
  end if;

  select coalesce(string_agg(lower(item ->> 'name'), ' '), '')
  into ingredient_text
  from pg_catalog.jsonb_array_elements(p_document -> 'ingredients') as item;

  insert into public.recipes (
    id, owner_id, slug, title, description, request, document, ingredient_text,
    sample_image_key, weirdness, crime_level, regret_potential, moderation_state
  )
  values (
    p_job_id,
    job.owner_id,
    'case-' || replace(p_job_id::text, '-', ''),
    p_document ->> 'title',
    coalesce(p_document ->> 'description', ''),
    job.request,
    p_document,
    ingredient_text,
    image_key,
    (job.request ->> 'weirdness')::integer,
    (p_document ->> 'crimeLevel')::integer,
    (p_document ->> 'regretPotential')::integer,
    'approved'
  )
  on conflict (id) do nothing;

  update public.generation_jobs
  set status = 'complete', recipe_id = p_job_id, error_category = null
  where id = p_job_id;

  insert into private.credit_ledger (user_id, day, entry_type, amount, idempotency_key, job_id)
  values (job.owner_id, private.utc_day(), 'consume', 0, job.idempotency_key, p_job_id)
  on conflict (user_id, idempotency_key, entry_type) do nothing;
end;
$$;

create or replace function private.fail_generation(p_job_id uuid, p_category text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  job public.generation_jobs%rowtype;
  reserved_day date;
begin
  select * into job from public.generation_jobs where id = p_job_id for update;
  if not found or job.status = 'complete' or job.status = 'failed' then
    return;
  end if;
  select day into reserved_day
  from private.credit_ledger
  where job_id = p_job_id and entry_type = 'reserve';
  update public.generation_jobs
  set status = 'failed', error_category = left(coalesce(p_category, 'failed'), 80)
  where id = p_job_id;
  if reserved_day is null then
    return;
  end if;
  insert into private.credit_ledger (user_id, day, entry_type, amount, idempotency_key, job_id)
  values (job.owner_id, reserved_day, 'refund', -1, job.idempotency_key, p_job_id)
  on conflict (user_id, idempotency_key, entry_type) do nothing;
end;
$$;

create or replace function private.recipe_visible(p_recipe public.recipes, p_viewer uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select
    (p_viewer is not null and p_recipe.owner_id = p_viewer)
    or (
      p_recipe.visibility = 'public'
      and p_recipe.moderation_state = 'approved'
      and not exists (
        select 1
        from public.user_blocks as block
        where p_viewer is not null
          and block.blocker_id = p_viewer
          and block.blocked_id = p_recipe.owner_id
      )
    );
$$;

create or replace function private.recipe_payload(p_recipe_id uuid, p_viewer uuid, p_full boolean)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  recipe public.recipes%rowtype;
  author text;
  guilty integer;
  acquitted integer;
  mine text;
  cooked jsonb;
begin
  select * into recipe from public.recipes where id = p_recipe_id;
  if not found or not private.recipe_visible(recipe, p_viewer) then
    return null;
  end if;
  select coalesce(nullif(profile.display_name, ''), 'Cook')
  into author
  from public.profiles as profile
  where profile.id = recipe.owner_id;

  select
    count(*) filter (where verdict = 'guilty'),
    count(*) filter (where verdict = 'acquitted')
  into guilty, acquitted
  from public.recipe_votes
  where recipe_id = recipe.id;

  if p_viewer is not null then
    select verdict into mine
    from public.recipe_votes
    where recipe_id = recipe.id and user_id = p_viewer;
  end if;

  if p_full then
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
      'id', cooked_row.id,
      'taste', cooked_row.taste_score,
      'verdict', cooked_row.verdict,
      'status', cooked_row.moderation_state,
      'bucket', case
        when cooked_row.moderation_state = 'approved' and cooked_row.public_path is not null then 'public-media'
        when p_viewer is not null and cooked_row.owner_id = p_viewer then 'uploads'
        else null
      end,
      'path', case
        when cooked_row.moderation_state = 'approved' then cooked_row.public_path
        when p_viewer is not null and cooked_row.owner_id = p_viewer then cooked_row.original_path
        else null
      end,
      'mine', p_viewer is not null and cooked_row.owner_id = p_viewer
    ) order by cooked_row.created_at), '[]'::jsonb)
    into cooked
    from public.cooked_results as cooked_row
    where cooked_row.recipe_id = recipe.id
      and (
        (cooked_row.moderation_state = 'approved' and recipe.visibility = 'public')
        or (p_viewer is not null and cooked_row.owner_id = p_viewer)
      );
  end if;

  return pg_catalog.jsonb_build_object(
    'id', recipe.id,
    'ownerId', recipe.owner_id,
    'slug', recipe.slug,
    'title', recipe.title,
    'description', recipe.description,
    'visibility', recipe.visibility,
    'owned', p_viewer is not null and recipe.owner_id = p_viewer,
    'author', author,
    'weirdness', recipe.weirdness,
    'crimeLevel', recipe.crime_level,
    'regretPotential', recipe.regret_potential,
    'sampleImageKey', recipe.sample_image_key,
    'servings', (recipe.document ->> 'servings')::integer,
    'prepMinutes', (recipe.document ->> 'prepMinutes')::integer,
    'cookMinutes', (recipe.document ->> 'cookMinutes')::integer,
    'ingredients', case when p_full then recipe.document -> 'ingredients' else '[]'::jsonb end,
    'steps', case when p_full then recipe.document -> 'steps' else '[]'::jsonb end,
    'request', case when p_full and p_viewer is not null and recipe.owner_id = p_viewer then recipe.request else null end,
    'votes', pg_catalog.jsonb_build_object('guilty', guilty, 'acquitted', acquitted, 'mine', mine),
    'cookedResults', coalesce(cooked, '[]'::jsonb),
    'createdAt', recipe.created_at
  );
end;
$$;

create or replace function private.list_my_kitchen(p_user_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  recipes jsonb;
  jobs jsonb;
begin
  select coalesce(pg_catalog.jsonb_agg(private.recipe_payload(recipe.id, p_user_id, false) order by recipe.created_at desc), '[]'::jsonb)
  into recipes
  from public.recipes as recipe
  where recipe.owner_id = p_user_id;

  select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
    'jobId', job.id,
    'status', job.status,
    'recipeId', job.recipe_id,
    'errorCategory', job.error_category,
    'createdAt', job.created_at
  ) order by job.created_at desc), '[]'::jsonb)
  into jobs
  from public.generation_jobs as job
  where job.owner_id = p_user_id
    and job.status in ('queued', 'processing', 'failed');

  return pg_catalog.jsonb_build_object(
    'recipes', recipes,
    'jobs', jobs,
    'allowance', private.allowance_snapshot(p_user_id)
  );
end;
$$;

create or replace function private.job_status(p_user_id uuid, p_job_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  job public.generation_jobs%rowtype;
begin
  select * into job
  from public.generation_jobs
  where id = p_job_id and owner_id = p_user_id;
  if not found then
    return null;
  end if;
  return pg_catalog.jsonb_build_object(
    'jobId', job.id,
    'status', job.status,
    'recipeId', job.recipe_id,
    'errorCategory', job.error_category,
    'allowance', private.allowance_snapshot(p_user_id)
  );
end;
$$;

create or replace function private.list_public_recipes(
  p_viewer uuid,
  p_query text,
  p_sort text,
  p_cursor text,
  p_limit integer
)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  lim integer := least(greatest(coalesce(p_limit, 20), 1), 50);
  escaped text := replace(replace(replace(coalesce(p_query, ''), '\', '\\'), '%', '\%'), '_', '\_');
  sort_key text := case when p_sort in ('newest', 'trending', 'most_voted') then p_sort else 'newest' end;
  cursor_votes integer;
  cursor_epoch numeric;
  cursor_id uuid;
  rec record;
  items jsonb := '[]'::jsonb;
  included integer := 0;
  next_cursor text;
  page_votes integer;
  page_epoch numeric;
  page_id uuid;
begin
  if p_cursor is not null and p_cursor <> '' then
    begin
      if sort_key = 'newest' then
        cursor_epoch := split_part(p_cursor, '|', 1)::numeric;
        cursor_id := split_part(p_cursor, '|', 2)::uuid;
      else
        cursor_votes := split_part(p_cursor, '|', 1)::integer;
        cursor_epoch := split_part(p_cursor, '|', 2)::numeric;
        cursor_id := split_part(p_cursor, '|', 3)::uuid;
      end if;
    exception
      when invalid_text_representation then
        raise exception 'invalid cursor' using errcode = '22023';
    end;
  end if;

  for rec in
    select
      recipe.id,
      recipe.created_at,
      (
        select count(*)::integer
        from public.recipe_votes as vote
        where vote.recipe_id = recipe.id
      ) as vote_total
    from public.recipes as recipe
    where recipe.visibility = 'public'
      and recipe.moderation_state = 'approved'
      and (
        p_viewer is null
        or not exists (
          select 1 from public.user_blocks as block
          where block.blocker_id = p_viewer and block.blocked_id = recipe.owner_id
        )
      )
      and (
        escaped = ''
        or recipe.title ilike '%' || escaped || '%' escape '\'
        or recipe.description ilike '%' || escaped || '%' escape '\'
        or recipe.ingredient_text ilike '%' || escaped || '%' escape '\'
      )
      and (
        p_cursor is null or p_cursor = ''
        or (
          sort_key = 'newest' and (
            extract(epoch from recipe.created_at) < cursor_epoch
            or (extract(epoch from recipe.created_at) = cursor_epoch and recipe.id < cursor_id)
          )
        )
        or (
          sort_key <> 'newest' and (
            (
              select count(*) from public.recipe_votes as vote where vote.recipe_id = recipe.id
            ) < cursor_votes
            or (
              (select count(*) from public.recipe_votes as vote where vote.recipe_id = recipe.id) = cursor_votes
              and extract(epoch from recipe.created_at) < cursor_epoch
            )
            or (
              (select count(*) from public.recipe_votes as vote where vote.recipe_id = recipe.id) = cursor_votes
              and extract(epoch from recipe.created_at) = cursor_epoch
              and recipe.id < cursor_id
            )
          )
        )
      )
    order by
      case when sort_key = 'newest' then extract(epoch from recipe.created_at) end desc,
      case when sort_key <> 'newest' then (
        select count(*) from public.recipe_votes as vote where vote.recipe_id = recipe.id
      ) end desc,
      recipe.created_at desc,
      recipe.id desc
    limit lim + 1
  loop
    if included = lim then
      if sort_key = 'newest' then
        next_cursor := page_epoch::text || '|' || page_id::text;
      else
        next_cursor := page_votes::text || '|' || page_epoch::text || '|' || page_id::text;
      end if;
      exit;
    end if;
    items := items || pg_catalog.jsonb_build_array(private.recipe_payload(rec.id, p_viewer, false));
    included := included + 1;
    page_votes := rec.vote_total;
    page_epoch := extract(epoch from rec.created_at);
    page_id := rec.id;
  end loop;

  return pg_catalog.jsonb_build_object('recipes', items, 'nextCursor', next_cursor);
end;
$$;

create or replace function private.get_recipe(p_viewer uuid, p_recipe_id uuid)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select private.recipe_payload(p_recipe_id, p_viewer, true);
$$;

create or replace function private.get_recipe_by_slug(p_viewer uuid, p_slug text)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  recipe_id uuid;
begin
  select id into recipe_id from public.recipes where slug = p_slug;
  if recipe_id is null then
    return null;
  end if;
  return private.recipe_payload(recipe_id, p_viewer, true);
end;
$$;

create or replace function private.publish_recipe(p_user_id uuid, p_recipe_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
begin
  update public.recipes
  set visibility = 'public', published_at = coalesce(published_at, pg_catalog.now())
  where id = p_recipe_id
    and owner_id = p_user_id
    and moderation_state = 'approved';
  if not found then
    raise exception 'recipe cannot be published' using errcode = '22023';
  end if;
  return private.recipe_payload(p_recipe_id, p_user_id, true);
end;
$$;

create or replace function private.set_vote(p_user_id uuid, p_recipe_id uuid, p_verdict text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_verdict not in ('guilty', 'acquitted') then
    raise exception 'invalid vote' using errcode = '22023';
  end if;
  if not exists (
    select 1 from public.recipes
    where id = p_recipe_id and visibility = 'public' and moderation_state = 'approved'
  ) then
    raise exception 'recipe not found' using errcode = 'P0002';
  end if;
  insert into public.recipe_votes (recipe_id, user_id, verdict)
  values (p_recipe_id, p_user_id, p_verdict)
  on conflict (recipe_id, user_id) do update set verdict = excluded.verdict, updated_at = pg_catalog.now();
  return private.recipe_payload(p_recipe_id, p_user_id, true);
end;
$$;

create or replace function private.enqueue_job(
  p_type text,
  p_idempotency_key text,
  p_user_id uuid,
  p_extra jsonb
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  payload jsonb;
begin
  payload := pg_catalog.jsonb_build_object(
    'type', p_type,
    'idempotencyKey', p_idempotency_key,
    'payload', pg_catalog.jsonb_build_object(
      'idempotencyKey', p_idempotency_key,
      'requestedBy', p_user_id
    ) || coalesce(p_extra, '{}'::jsonb)
  );
  perform pgmq.send('jobs', payload);
end;
$$;

create or replace function private.create_cooked_result(
  p_user_id uuid,
  p_recipe_id uuid,
  p_path text,
  p_taste integer,
  p_verdict text,
  p_idempotency_key text
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  existing_id uuid;
  new_id uuid;
begin
  if p_taste < 1 or p_taste > 5
    or char_length(btrim(p_verdict)) < 1
    or char_length(p_verdict) > 200
    or p_path !~ ('^' || p_user_id::text || '/[A-Za-z0-9._-]{8,80}$')
    or char_length(p_idempotency_key) < 8 then
    raise exception 'invalid cooked result' using errcode = '22023';
  end if;
  if not exists (
    select 1 from public.recipes as recipe
    where recipe.id = p_recipe_id
      and private.recipe_visible(recipe, p_user_id)
  ) then
    raise exception 'recipe not found' using errcode = 'P0002';
  end if;

  select id into existing_id
  from public.cooked_results
  where owner_id = p_user_id and idempotency_key = p_idempotency_key;
  if existing_id is not null then
    return pg_catalog.jsonb_build_object('resultId', existing_id, 'status', 'pending');
  end if;

  insert into public.cooked_results (
    recipe_id, owner_id, original_path, taste_score, verdict, idempotency_key
  )
  values (p_recipe_id, p_user_id, p_path, p_taste, btrim(p_verdict), p_idempotency_key)
  returning id into new_id;

  perform private.enqueue_job(
    'moderate_photo',
    p_idempotency_key,
    p_user_id,
    pg_catalog.jsonb_build_object('resultId', new_id)
  );
  return pg_catalog.jsonb_build_object('resultId', new_id, 'status', 'pending');
end;
$$;

create or replace function private.mark_photo_checked(
  p_result_id uuid,
  p_ok boolean,
  p_note text,
  p_media_type text default null
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  update public.cooked_results
  set
    photo_ready = p_ok,
    media_type = coalesce(p_media_type, media_type),
    moderation_state = case when p_ok then moderation_state else 'rejected' end,
    moderation_note = case when p_ok then null else left(coalesce(p_note, 'invalid photo'), 200) end
  where id = p_result_id
    and moderation_state = 'pending';
end;
$$;

create or replace function private.photo_source(p_result_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  row public.cooked_results%rowtype;
begin
  select * into row from public.cooked_results where id = p_result_id;
  if not found or row.moderation_state <> 'pending' or row.photo_ready then
    return null;
  end if;
  return pg_catalog.jsonb_build_object(
    'resultId', row.id,
    'bucket', 'uploads',
    'path', row.original_path,
    'ownerId', row.owner_id
  );
end;
$$;

create or replace function private.is_staff(p_user_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from private.staff_users where user_id = p_user_id);
$$;

create or replace function private.staff_decision(
  p_staff_id uuid,
  p_result_id uuid,
  p_decision text,
  p_note text,
  p_public_path text
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  row public.cooked_results%rowtype;
begin
  if not private.is_staff(p_staff_id) then
    raise exception 'staff only' using errcode = '42501';
  end if;
  if p_decision not in ('approve', 'reject', 'takedown') then
    raise exception 'invalid decision' using errcode = '22023';
  end if;
  select * into row from public.cooked_results where id = p_result_id for update;
  if not found then
    raise exception 'cooked result not found' using errcode = 'P0002';
  end if;
  if p_decision = 'approve' and (not row.photo_ready or p_public_path is null) then
    raise exception 'photo is not ready' using errcode = '22023';
  end if;

  update public.cooked_results
  set
    moderation_state = case when p_decision = 'approve' then 'approved' else 'rejected' end,
    public_path = case
      when p_decision = 'approve' then p_public_path
      else null
    end,
    moderation_note = nullif(left(coalesce(p_note, ''), 200), '')
  where id = p_result_id;

  update public.moderation_reports
  set review_state = 'reviewed'
  where target_type = 'cooked_result' and target_id = p_result_id;

  return pg_catalog.jsonb_build_object(
    'originalPath', row.original_path,
    'previousPublicPath', row.public_path,
    'ownerId', row.owner_id
  );
end;
$$;

create or replace function private.create_report(
  p_user_id uuid,
  p_target_type text,
  p_target_id uuid,
  p_reason text
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_target_type not in ('recipe', 'cooked_result')
    or char_length(btrim(p_reason)) < 1
    or char_length(p_reason) > 200 then
    raise exception 'invalid report' using errcode = '22023';
  end if;
  if p_target_type = 'recipe' and not exists (
    select 1 from public.recipes where id = p_target_id and visibility = 'public'
  ) then
    raise exception 'target not found' using errcode = 'P0002';
  end if;
  if p_target_type = 'cooked_result' and not exists (
    select 1 from public.cooked_results where id = p_target_id and moderation_state = 'approved'
  ) then
    raise exception 'target not found' using errcode = 'P0002';
  end if;
  insert into public.moderation_reports (reporter_id, target_type, target_id, reason)
  values (p_user_id, p_target_type, p_target_id, btrim(p_reason))
  on conflict (reporter_id, target_type, target_id) do update set reason = excluded.reason, review_state = 'open';
end;
$$;

create or replace function private.set_block(p_blocker uuid, p_blocked uuid, p_active boolean)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_blocker = p_blocked or p_blocked is null then
    raise exception 'invalid block' using errcode = '22023';
  end if;
  if p_active then
    insert into public.user_blocks (blocker_id, blocked_id)
    values (p_blocker, p_blocked)
    on conflict do nothing;
  else
    delete from public.user_blocks
    where blocker_id = p_blocker and blocked_id = p_blocked;
  end if;
end;
$$;

create or replace function private.list_blocks(p_user_id uuid)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
    'userId', block.blocked_id,
    'displayName', coalesce(nullif(profile.display_name, ''), 'Cook')
  )), '[]'::jsonb)
  from public.user_blocks as block
  left join public.profiles as profile on profile.id = block.blocked_id
  where block.blocker_id = p_user_id;
$$;

create or replace function private.moderation_queue(p_staff_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
begin
  if not private.is_staff(p_staff_id) then
    raise exception 'staff only' using errcode = '42501';
  end if;
  return pg_catalog.jsonb_build_object(
    'cooked', coalesce((
      select pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'id', cooked.id,
        'recipeId', cooked.recipe_id,
        'title', recipe.title,
        'verdict', cooked.verdict,
        'taste', cooked.taste_score,
        'status', cooked.moderation_state,
        'photoReady', cooked.photo_ready,
        'bucket', 'uploads',
        'path', cooked.original_path,
        'note', cooked.moderation_note
      ) order by cooked.created_at)
      from public.cooked_results as cooked
      join public.recipes as recipe on recipe.id = cooked.recipe_id
      where cooked.moderation_state = 'pending'
    ), '[]'::jsonb),
    'reports', coalesce((
      select pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'id', report.id,
        'targetType', report.target_type,
        'targetId', report.target_id,
        'reason', report.reason,
        'createdAt', report.created_at
      ) order by report.created_at)
      from public.moderation_reports as report
      where report.review_state = 'open'
    ), '[]'::jsonb)
  );
end;
$$;

create or replace function private.create_clip(
  p_user_id uuid,
  p_result_id uuid,
  p_idempotency_key text
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  existing public.clip_jobs%rowtype;
  new_id uuid;
begin
  if char_length(p_idempotency_key) < 8 then
    raise exception 'invalid clip request' using errcode = '22023';
  end if;
  if not exists (
    select 1 from public.cooked_results
    where id = p_result_id
      and owner_id = p_user_id
      and moderation_state = 'approved'
      and public_path is not null
  ) then
    raise exception 'approved cooked photo required' using errcode = '22023';
  end if;

  select * into existing
  from public.clip_jobs
  where owner_id = p_user_id and idempotency_key = p_idempotency_key;
  if found then
    return pg_catalog.jsonb_build_object('clipId', existing.id, 'status', existing.status);
  end if;

  insert into public.clip_jobs (owner_id, cooked_result_id, status, idempotency_key)
  values (p_user_id, p_result_id, 'queued', p_idempotency_key)
  returning id into new_id;

  perform private.enqueue_job(
    'render_clip',
    p_idempotency_key,
    p_user_id,
    pg_catalog.jsonb_build_object('clipId', new_id)
  );
  return pg_catalog.jsonb_build_object('clipId', new_id, 'status', 'queued');
end;
$$;

create or replace function private.clip_source(p_clip_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  clip public.clip_jobs%rowtype;
  photo text;
begin
  select * into clip from public.clip_jobs where id = p_clip_id;
  if not found or clip.status in ('ready', 'failed') then
    return null;
  end if;
  select public_path into photo
  from public.cooked_results
  where id = clip.cooked_result_id
    and moderation_state = 'approved'
    and public_path is not null;
  if photo is null then
    return null;
  end if;
  return pg_catalog.jsonb_build_object(
    'clipId', clip.id,
    'ownerId', clip.owner_id,
    'bucket', 'public-media',
    'path', photo
  );
end;
$$;

create or replace function private.complete_clip(p_clip_id uuid, p_path text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  update public.clip_jobs
  set status = 'ready', storage_path = p_path
  where id = p_clip_id and status <> 'ready';
end;
$$;

create or replace function private.fail_clip(p_clip_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  update public.clip_jobs
  set status = 'failed'
  where id = p_clip_id and status not in ('ready', 'failed');
end;
$$;

create or replace function private.get_clip(p_user_id uuid, p_clip_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  clip public.clip_jobs%rowtype;
begin
  select * into clip from public.clip_jobs where id = p_clip_id and owner_id = p_user_id;
  if not found then
    return null;
  end if;
  return pg_catalog.jsonb_build_object(
    'clipId', clip.id,
    'status', clip.status,
    'bucket', case when clip.storage_path is null then null else 'clips' end,
    'path', clip.storage_path
  );
end;
$$;

drop function if exists private.delete_account(uuid);

create or replace function private.delete_account(p_user_id uuid, p_idempotency_key text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_user_id is null or char_length(p_idempotency_key) < 8 then
    raise exception 'invalid account deletion' using errcode = '22023';
  end if;
  insert into private.account_deletion_keys (user_id, idempotency_key)
  values (p_user_id, p_idempotency_key)
  on conflict do nothing;

  delete from storage.objects
  where bucket_id in ('uploads', 'public-media', 'clips')
    and (storage.foldername(name))[1] = p_user_id::text;

  delete from auth.sessions where user_id = p_user_id;
  delete from auth.users where id = p_user_id;
end;
$$;

revoke all on function private.utc_day() from public, anon, authenticated;
revoke all on function private.allowance_snapshot(uuid) from public, anon, authenticated;
revoke all on function private.assert_generation_request(jsonb) from public, anon, authenticated;
revoke all on function private.enqueue_generation(uuid, text, jsonb) from public, anon, authenticated;
revoke all on function private.complete_generation(uuid, jsonb) from public, anon, authenticated;
revoke all on function private.fail_generation(uuid, text) from public, anon, authenticated;
revoke all on function private.recipe_visible(public.recipes, uuid) from public, anon, authenticated;
revoke all on function private.recipe_payload(uuid, uuid, boolean) from public, anon, authenticated;
revoke all on function private.list_my_kitchen(uuid) from public, anon, authenticated;
revoke all on function private.job_status(uuid, uuid) from public, anon, authenticated;
revoke all on function private.list_public_recipes(uuid, text, text, text, integer) from public, anon, authenticated;
revoke all on function private.get_recipe(uuid, uuid) from public, anon, authenticated;
revoke all on function private.get_recipe_by_slug(uuid, text) from public, anon, authenticated;
revoke all on function private.publish_recipe(uuid, uuid) from public, anon, authenticated;
revoke all on function private.set_vote(uuid, uuid, text) from public, anon, authenticated;
revoke all on function private.enqueue_job(text, text, uuid, jsonb) from public, anon, authenticated;
revoke all on function private.create_cooked_result(uuid, uuid, text, integer, text, text) from public, anon, authenticated;
revoke all on function private.mark_photo_checked(uuid, boolean, text, text) from public, anon, authenticated;
revoke all on function private.photo_source(uuid) from public, anon, authenticated;
revoke all on function private.is_staff(uuid) from public, anon, authenticated;
revoke all on function private.staff_decision(uuid, uuid, text, text, text) from public, anon, authenticated;
revoke all on function private.create_report(uuid, text, uuid, text) from public, anon, authenticated;
revoke all on function private.set_block(uuid, uuid, boolean) from public, anon, authenticated;
revoke all on function private.list_blocks(uuid) from public, anon, authenticated;
revoke all on function private.moderation_queue(uuid) from public, anon, authenticated;
revoke all on function private.create_clip(uuid, uuid, text) from public, anon, authenticated;
revoke all on function private.clip_source(uuid) from public, anon, authenticated;
revoke all on function private.complete_clip(uuid, text) from public, anon, authenticated;
revoke all on function private.fail_clip(uuid) from public, anon, authenticated;
revoke all on function private.get_clip(uuid, uuid) from public, anon, authenticated;
revoke all on function private.delete_account(uuid, text) from public, anon, authenticated;

grant execute on function private.enqueue_generation(uuid, text, jsonb) to service_role;
grant execute on function private.complete_generation(uuid, jsonb) to service_role;
grant execute on function private.fail_generation(uuid, text) to service_role;
grant execute on function private.allowance_snapshot(uuid) to service_role;
grant execute on function private.list_my_kitchen(uuid) to service_role;
grant execute on function private.job_status(uuid, uuid) to service_role;
grant execute on function private.list_public_recipes(uuid, text, text, text, integer) to service_role;
grant execute on function private.get_recipe(uuid, uuid) to service_role;
grant execute on function private.get_recipe_by_slug(uuid, text) to service_role;
grant execute on function private.publish_recipe(uuid, uuid) to service_role;
grant execute on function private.set_vote(uuid, uuid, text) to service_role;
grant execute on function private.create_cooked_result(uuid, uuid, text, integer, text, text) to service_role;
grant execute on function private.mark_photo_checked(uuid, boolean, text, text) to service_role;
grant execute on function private.photo_source(uuid) to service_role;
grant execute on function private.is_staff(uuid) to service_role;
grant execute on function private.staff_decision(uuid, uuid, text, text, text) to service_role;
grant execute on function private.create_report(uuid, text, uuid, text) to service_role;
grant execute on function private.set_block(uuid, uuid, boolean) to service_role;
grant execute on function private.list_blocks(uuid) to service_role;
grant execute on function private.moderation_queue(uuid) to service_role;
grant execute on function private.create_clip(uuid, uuid, text) to service_role;
grant execute on function private.clip_source(uuid) to service_role;
grant execute on function private.complete_clip(uuid, text) to service_role;
grant execute on function private.fail_clip(uuid) to service_role;
grant execute on function private.get_clip(uuid, uuid) to service_role;
grant execute on function private.delete_account(uuid, text) to service_role;
