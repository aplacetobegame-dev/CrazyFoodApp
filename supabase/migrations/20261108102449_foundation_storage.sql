-- Private originals and a locked bucket for later approved derivatives.
-- Clients can write only their own prefix in `uploads`. `public-media` has no client policy.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values
  (
    'uploads',
    'uploads',
    false,
    10485760,
    array['image/jpeg', 'image/png', 'image/webp', 'image/heic']::text[]
  ),
  (
    'public-media',
    'public-media',
    false,
    5242880,
    array['image/jpeg', 'image/png', 'image/webp']::text[]
  )
on conflict (id) do update
set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

create policy uploads_insert_own
  on storage.objects
  for insert
  to authenticated
  with check (
    bucket_id = 'uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy uploads_select_own
  on storage.objects
  for select
  to authenticated
  using (
    bucket_id = 'uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy uploads_update_own
  on storage.objects
  for update
  to authenticated
  using (
    bucket_id = 'uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  )
  with check (
    bucket_id = 'uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy uploads_delete_own
  on storage.objects
  for delete
  to authenticated
  using (
    bucket_id = 'uploads'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
