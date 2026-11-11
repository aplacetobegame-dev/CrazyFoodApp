# Food Felonies — investigation report

**Date:** 2026-11-11  
**Scope:** Full repository read of the Expo app, Supabase migrations and Edge Functions, the queue worker, contracts, deploy files, and `docs/PRODUCT_AND_TECH_DESIGN.md`.  
**Checks run:** `pnpm typecheck` passed (contracts, mobile, worker). `pnpm test` passed (6 tests: 2 contract, 4 worker). The mobile app has no test script, so it was skipped.  
**Purpose:** Backlog for later work. Findings are ordered so the first items are defects in code that already ships, and the later items are product work that was never built.

This is a snapshot. The design doc still describes the repo as greenfield. The code is past that: a local preview of the whole product, plus a thin connected foundation (sign-in, profiles, private storage buckets, an echo queue, and a worker).

## How to use this list

| Label | Meaning |
| --- | --- |
| Bug | Behavior is wrong in code that already runs. |
| Latent | The path exists and will fail, but no screen calls it yet. |
| Gap | Promised by the design or by the current-phase plan, and not built. |
| Risk | Config or deploy file that will misbehave when used as written. |

Severity is High, Medium, or Low for the current staging goal: sign in, queue a job, keep a private recipe, publish it, and attach cooked proof.

---

## 1. What is actually built

Two apps share one codebase, selected by `EXPO_PUBLIC_APP_MODE`.

| Mode | How it starts | What the user gets |
| --- | --- | --- |
| Preview | `pnpm run mobile --test`, or `pnpm start` inside `apps/mobile` while `__DEV__` is on | Full Food Felonies UI in memory. Sample recipes, votes, camera, moderation, ads, and social posting are local fixtures. Nothing is saved. |
| Connected | `pnpm run mobile` from the repo root | Email code sign-in, empty Discover, empty My Cases, a Create form that refuses to generate, and a Profile page that pings health, the profile row, and (on web) `/api/session`. |

`isUiPreview` is `__DEV__ && EXPO_PUBLIC_APP_MODE !== "connected"` in `apps/mobile/src/lib/app-mode.ts`. Release builds never enter preview mode. A dev server started without the root script enters preview mode, because the env var is unset.

Backend today:

- `public.profiles` with row-level security, created from `auth.users`.
- Private Storage buckets `uploads` and `public-media`. Clients may touch only their own prefix in `uploads`.
- PGMQ queue `jobs`, plus `infra.api_idempotency_keys` and `infra.job_receipts`.
- Edge Function `v1`: `POST /jobs/echo` and `DELETE /account`. Health function returns `{ ok: true }` with no dependency checks.
- Worker on Cloud Run shape: poll `jobs`, write a receipt for a valid echo message, archive it. Invalid messages are archived with no receipt. Exhausted messages are archived with no receipt.

Not in the database at all: recipes, generation jobs, credit ledger, votes, cooked results, reports, blocks, social accounts, publications, or ad transactions. The client never calls the echo endpoint or account deletion.

---

## 2. Bugs and latent defects

### High — native weirdness slider does not follow the value

`apps/mobile/src/features/create/weirdness-slider.tsx` passes `value={initialValue}` into `@react-native-community/slider`. That prop is the controlled value. `initialValue` stays at 50 (connected) or 72 (preview) while `onValueChange` updates a different piece of state. Each drag re-renders the slider back to the start, so the thumb fights the finger. The number beside the slider can move while the thumb snaps back, and Generate can submit the wrong weirdness.

The web slider (`weirdness-slider.web.tsx`) correctly binds `value={value}`.

**Later work:** Drive the native slider from `value`. Confirm on an iOS and Android device that the thumb, the announced value, and the submitted number stay the same. Do not “fix” it by making the web slider uncontrolled.

### High — web server auth drops refreshed cookies

`apps/mobile/src/lib/supabase-server.ts` implements `setAll()` as a no-op. `apps/mobile/src/app/api/session+api.ts` then calls `getUser()` with that client. `supabase/config.toml` has `enable_refresh_token_rotation = true` and `jwt_expiry = 3600`.

`getUser()` refreshes an expired access token and must write the new cookies. Those writes are discarded. Rotation invalidates the refresh token the browser still holds. After about an hour, the Profile “server session” check on web can sign the browser session out.

Native skips this route (`serverSession` is the literal `"Native session"`). The bug is the web connected flow, and any later server route that reuses this helper.

**Later work:** Persist `setAll` onto the response (`Set-Cookie`) using the Expo server request/response cookies API. Add a test that an expired access token plus a valid refresh token returns a new cookie pair. Until that exists, do not add more server routes on this helper.

### High — profile updates cannot run the `updated_at` trigger

`supabase/migrations/20261108102448_foundation_profiles.sql` grants `authenticated` permission to update `display_name`, and a `BEFORE UPDATE` trigger calls `private.set_updated_at()`. That function is not `SECURITY DEFINER`. The same migration revokes `USAGE` on schema `private` and `EXECUTE` on the function from `authenticated`.

A trigger runs as the user who issued the update. An authenticated profile update should fail with permission denied for the schema or the function. No screen edits `display_name` yet, so this is untriggered. The grant and the policy were written so that update would work.

**Later work:** Make `set_updated_at` `SECURITY DEFINER` with a locked `search_path`, or move it to a schema the authenticated role may execute, and add a SQL test that an authenticated update of `display_name` succeeds and changes `updated_at`.

### Medium — sign-in can spin forever

`apps/mobile/src/lib/auth.tsx` sets `ready` only inside `getSession().then(...)`. There is no `.catch`. A SecureStore or AsyncStorage failure leaves `ready` false, and both the index route and the sign-in screen render an endless spinner. `LargeSecureStore.decrypt` also returns null or can throw on corrupt ciphertext (`apps/mobile/src/lib/client.ts`).

**Later work:** On failure, set `ready` true with `session` null and show the sign-in screen plus a retry. Clear undecryptable session blobs instead of hanging.

### Medium — account deletion does not remove stored files

`private.delete_account` deletes `auth.users` and relies on cascades for `profiles` and idempotency keys. Objects in `storage.objects` under `uploads/<user id>/` are not deleted. The Edge Function requires an `Idempotency-Key` and then ignores it. There is no connected-app control that calls `DELETE /v1/account`.

The design requires media cleanup and token revocation on deletion. Storage buckets already exist, so files can outlive the user as soon as an upload is added.

**Later work:** In the same transaction path, delete that user’s storage objects, revoke sessions, and record the idempotency key. Add a connected Profile action only after the cleanup is real. The preview “delete account” copy says the session is cleared; staff moderation history and the draft number counter in `preview-data.tsx` survive that reset. Clear those too, or change the copy.

### Medium — connected Create advertises an allowance it does not have

`create-recipe-screen.tsx` always shows “3 free daily · Up to 2 earned”. Generate in connected mode opens a dialog: the endpoint and the live balance are not implemented (`setDialog({ kind: "unavailable" })` around the comment on line 191). Inputs are kept, which is right. The allowance line is not.

Servings have a floor of 1 and no ceiling. A request can ask for an absurd serving count. Cap it when the contract exists (a small upper bound such as 12 or 24 is enough to decide later).

### Medium — worker looks healthy when it is not working

`services/worker/src/index.ts` returns `200` from `GET /health` with no database check. Poll errors are logged and the loop continues. `SIGTERM` closes the SQL pool while a batch may still be using it.

`services/worker/cloudrun-service.yaml` is marked “do not apply yet”, and as written it will not run a pull worker:

- `autoscaling.knative.dev/minScale` is `"0"`, so the process exits when HTTP traffic stops. The poll loop is not HTTP traffic.
- CPU throttling is left at the Cloud Run default, which freezes timers between requests. A polling worker needs CPU always allocated.
- The design asks for a continuously running pool. This file describes the opposite.

The web image (`apps/mobile/Dockerfile`) copies source and runs `node server.js`, which serves `dist/`. The image never runs `expo export`, and `dist/` is gitignored. A build of that Dockerfile has nothing to serve.

**Later work:** Before any deploy, set min instances to 1, disable CPU throttling, and fail `/health` when the database or the last poll is down. Build the Expo web bundle inside the image, or stop documenting the Dockerfile as deployable.

### Low — sign-in and auth config are looser than the staging plan

- `sign-in.tsx` calls `signInWithOtp` with `shouldCreateUser: true`.
- `supabase/config.toml` has `enable_signup = true` in both `[auth]` and `[auth.email]`, and `[auth.email] enable_confirmations = false`.
- The design’s current phase says public signup stays off and testers use provisioned accounts.
- Email validation is `includes("@")`. There is no resend control; changing the email is the only way to request another code.
- `[auth.email] max_frequency = "1s"` allows a new message every second, up to the coarser `sign_in_sign_ups` limit.
- `[auth.email.template.magic_link] content_path` is `./supabase/templates/magic_link.html`. The CLI resolves that path from the `supabase/` directory, so it looks for `supabase/supabase/templates/magic_link.html`. The template that exists is `supabase/templates/magic_link.html`. Confirm on `supabase start` and point `content_path` at `./templates/magic_link.html`.

**Later work:** Staging should create users only from an allowlist or the dashboard. Keep local signup if it is useful, and make that split explicit in config rather than in the client.

### Low — other code notes

- Invalid queue messages are archived and dropped (`handler.ts`). That is acceptable for echo and unsafe for a future generation job, which must refund a reserved slot exactly once. Receipts are unique on `message_id`, not on the business idempotency key, so two messages with one key would both “succeed”.
- `getSession()` is the connected gate. It trusts local storage. Prefer `getUser()` when the app starts, then listen for auth changes.
- Profile status fetches have no timeout. A hung health URL stays on “Checking”.
- `app.json` does not register `expo-camera` or `expo-image-picker`. Expo Go supplies the permissions. A standalone build will be missing `NSCameraUsageDescription` and the photo-library string. Add the plugins before any binary that leaves Expo Go.
- Splash and Android icon colors are still the Expo blue (`#208AEF`, `#E6F4FE`), not the forest/cream brand.
- `apps/mobile/src/app/home.tsx` only redirects to `/profile`. Nothing in the connected UI needs that route.
- `apps/mobile/README.md` still contains the create-expo-app “reset-project” section. `npm run reset-project` is not a script in this repo.

---

## 3. Preview UI — real bugs versus fixtures

The preview is intentionally local. These are the spots that will mislead a tester or violate the case-file rules.

| Item | Kind | Detail |
| --- | --- | --- |
| Generated case ignores the form | Fixture | `makeDraft` in `preview-data.tsx` copies the pickle-rice recipe and stores the request beside it. The case screen says so. Weirdness, exclusions, cuisine, and time do not change the recipe, crime level, or steps. |
| Allowance is not consumed | Fixture | Creating a case does not reduce the “3 free” balance. Rewarded-ad and social screens only mutate `rewardKeys` in memory, capped at 2. |
| Public web case is a sample card | Gap | `/recipe/[slug]` lists two bundled recipes, forces `noindex`, and does not render cooked photos or votes. Connected mode redirects that route home. |
| Sample cooked review has no photo | OK | The pickle-rice “Sam Rivera” review says the photo is withheld. That matches the rule against fake cooked photos. |
| Case order | Mostly matches | Concept image, then stats, then ingredients and steps, then “I cooked it”, then cooked results, then Guilty/Acquitted. Votes are hidden on private drafts. |
| One proof per case | Fixture | `addProof` replaces the previous proof for that case. The product model allows a new submission after rejection. |
| Staff queue | Fixture | Decisions append in memory and do not change Discover. They also survive preview account deletion. |
| Trending sort | Gap | Discover’s “Trending” chip leaves feed order unchanged. “Newest” and “Most Voted” do sort. |
| Camera and gallery | Implemented in preview | Permission denial offers the gallery. Connected mode has no cooked-proof flow. |

Do not treat a green preview walkthrough as proof that generation, moderation, or rewards work.

---

## 4. Unbuilt product work

Mapped to section 11 of `docs/PRODUCT_AND_TECH_DESIGN.md`. The design’s first end-to-end milestone is still open: staging sign-in → Create → queued job → private recipe still in My Cases after a restart. Today sign-in works and the rest stops at the “Generation unavailable” dialog.

### Phase step 2 — generate and save

- Shared recipe contract (the contracts package only models an echo job).
- Tables for recipes, generation jobs, and the daily credit ledger.
- One transaction that reserves a slot and enqueues the job.
- Deterministic fixture provider in the worker, private draft persistence, and a single refund on permanent failure.
- Create, job status, allowance, and My Cases wired to those APIs.
- Resume after the app is killed.

### Phase step 3 — publish and discover

- Explicit publish, paginated feed and search, Guilty/Acquitted votes, anonymous read of approved public cases only.
- Public server-rendered page and share metadata on the staging URL.
- Private drafts absent from search, metadata, and anonymous fetches.

### Phase step 4 — cooked proof and moderation

- Camera-first upload, gallery fallback, MIME and size checks, EXIF strip, private original, approved derivative.
- Taste score 1–5 and a short verdict required.
- Staff review, reports, blocks, takedown, and account deletion that also deletes media.
- Public case layout with the concept image above real cooked photos.

### Phase step 5 — clip export

- Short clip from the approved cooked photo only, private preview asset, system share sheet.
- Logs for queue age, failures, refunds, and moderation state.

### Explicitly deferred by the design (do not build in the current phase)

Gemini, generated concept images, AdMob and SSV, Instagram, TikTok, custom domain, and production SMTP. The preview screens for ads and social posting are prototypes. The connected app correctly hides them. Earned slots stay at zero until those integrations exist; the current phase is three free generations per UTC day.

### Acceptance tests from the design that have no automated coverage

Concurrent daily cap, idempotent generation, single refund, duplicate ad callbacks, private-draft anonymity, cooked review rejected without a photo, and camera-denial fallback. The worker tests cover echo ack, duplicate receipt, exhaustion, and a thrown handler. They do not cover Postgres, PGMQ, or the Edge Function.

---

## 5. Docs, quality gates, and security posture

- `docs/PRODUCT_AND_TECH_DESIGN.md` says the repository had no application source when it was written (reviewed 2026-11-07). It is still the right blueprint. The “repository state” line is stale and will send the next reader looking for a greenfield repo.
- No CI workflow. Typecheck and the six unit tests are local-only. Mobile lint is a separate Expo config; root ESLint ignores `apps/mobile/**` and `supabase/functions/**`.
- Connected mode throws during render if `EXPO_PUBLIC_SUPABASE_URL` or the publishable key is missing (`public-config.ts`). That is a redbox, not a setup screen. The same helper rejects keys that contain `service_role` or `sb_secret_`, which is the right guard.
- `private` is listed in the Data API schemas so the Edge Function can call it. `enqueue_echo` and `delete_account` are granted only to `service_role`. Keep new private functions on that pattern. A grant to `authenticated` would expose them immediately.
- Storage policies for `uploads` restrict the first folder to `auth.uid()`. `public-media` has no client policy. That split matches the design. Nothing in the connected app uploads yet.
- The worker’s `DATABASE_URL` in `.env.example` is the local superuser. The design asks for a restricted worker role before any shared staging database.
- CORS on `v1` is `Access-Control-Allow-Origin: *`. Fine for a bearer-token mobile call. Do not add cookie credentials to that function without a specific origin list.
- Queue and ledger tables enable row-level security and revoke client access. There are no policies because clients must not read them. That is correct only while the grants stay empty.

---

## 6. Suggested order of work

1. Fix the native weirdness slider and confirm it on device.
2. Fix web session cookie writes before any other server route uses `createRequestSupabase`.
3. Fix the profile `updated_at` trigger and cover it with a database test.
4. Make sign-in recover from storage errors, and decide staging signup (allowlist versus open OTP).
5. Correct the magic-link template path and confirm a local code email.
6. Build phase step 2: recipe contract, ledger, enqueue, fixture worker, Create and My Cases. This is the first user-visible milestone.
7. Only then publish, Discover, votes, and the public page.
8. Cooked proof, storage deletion, and moderation.
9. Revisit the Cloud Run service and the web Dockerfile before any deploy. Do not apply `cloudrun-service.yaml` as it stands.

Items 1–5 are small and independent. Item 6 is the product. The preview app can stay as the design reference while step 2 replaces the “Generation unavailable” dialog.
