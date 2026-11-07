# Food Felonies — Product and Technical Design

**Status:** Development blueprint  
**Working name:** Food Felonies (placeholder)  
**Last reviewed:** 2026-11-07  
**Repository state:** Greenfield; no application source or commits were present when this document was written.

## 1. Product summary

Food Felonies is a mobile-first recipe generator and community for unusual-but-cookable food ideas. Users can start with ingredients they have, exclude ingredients they cannot or do not want to eat, choose servings, and set a slider from ordinary to culinary chaos. The app returns a structured recipe, an AI-generated concept image, and satirical case-file stats such as Crime Level and Regret Potential.

The community loop is built around evidence of what happened in a real kitchen. A recipe can be published before anyone cooks it, but a “I cooked it” review requires a photo of the actual dish, a taste score, and a short verdict. Recipe pages show the generated concept first and actual cooked attempts below it. This is the primary product distinction: the joke is paired with visible, user-submitted proof.

AI pantry matching, recipe generation, and voting already appear in adjacent products such as [Chowy](https://www.chowy.app/), [Supper](https://supperapp.io/), and [Samsung Food](https://samsungfood.com/). Food Felonies should compete through its comedy and “show us what you actually made” format rather than through a larger recipe catalog.

### Product goals

- Generate recipes that honor available ingredients, exclusions, serving count, and the user's chosen weirdness level.
- Make generated recipes safe enough to attempt and clearly label the generated image as a concept.
- Make a cooked-result photo the required evidence for a cooked review and review score.
- Let users publish, find, vote on, and share case files without forcing social posting.
- Keep generation costs and ad placements understandable and bounded.

### Out of scope for v1

- AI-generated video. Social clips are rendered from a user’s cooked-result photo.
- Subscriptions, paid credit packs, or cash rewards.
- Automatic publishing before the user has reviewed and confirmed the post.
- Treating the generated concept image as proof that a recipe was cooked.
- Nutrition, medical, or allergy-safety guarantees.

## 2. Main user experience

### 2.1 Create a recipe

The Create screen collects:

- Ingredients on hand, with optional quantities.
- Ingredients to exclude, including allergies and strong dislikes.
- Servings.
- A 0–100 “Normal → Food Felony” slider.
- Optional cuisine, time, equipment, and dietary constraints.

The app explains that exclusions are sent to the recipe service to generate the recipe. A generation request reserves one daily slot and queues both recipe and concept-image generation. The user sees a job status and can leave the screen; the recipe is saved when complete.

### 2.2 Recipe case file

A recipe detail page contains the recipe name, ingredients, instructions, generated concept image, crime stats, and community vote. The concept image must be labeled **AI-generated concept image**. The image model must not draw labels or recipe text; the app renders those as accessible UI text.

### 2.3 Cooked-result photo and score

The cooked-result flow is a core feature, not an optional reaction:

1. The user taps **I cooked it — add proof**.
2. The in-app camera opens first so they can photograph the dish they made. If camera permission is denied or the device cannot use a camera, offer gallery selection as a fallback.
3. The user submits the photo, a taste score from 1 to 5, and a short verdict.
4. The upload is validated and moderated before it appears publicly.
5. The page shows the actual cooked-result photo below the generated concept image. Directly beneath each cooked photo, show **Taste: n/5**, the user’s verdict, and the recipe’s **Crime Level: n/100**.

The page order is fixed:

~~~text
Recipe name and case-file summary
[AI-generated concept image]
[Crime Level and other satirical recipe stats]
Recipe ingredients and instructions
“I cooked it — add proof”
Cooked results
  [actual user-cooked photo]
  Taste score · short verdict · Crime Level
  [next actual user-cooked photo]
  Taste score · short verdict · Crime Level
Community votes and comments, if enabled
~~~

If no one has cooked the recipe yet, show an empty state inviting the current user to make it and add the first photo. Do not show a fake cooked photo or imply that the AI concept image is the user's result. Private recipes stay private; a cooked photo is visible to others only when its recipe is public and moderation has approved the photo.

A recipe’s Crime Level is a satirical recipe attribute, not a measure of food safety or the user’s taste score. Keep these values visually distinct. Ordinary community votes do not require a cooked photo; a cooked review and its score always do.

### 2.4 Publish and discover

Recipes are private drafts by default. The owner explicitly publishes a case file to make it available in the in-app feed, search, and public web page. Public pages use server-rendered HTML with recipe title, description, and an Open Graph image. Private drafts and unapproved photos must not appear in sitemaps, search results, metadata, or social share URLs.

Community members can submit one current vote per recipe, shown as **Guilty** or **Acquitted**. A vote is separate from a cooked score. Search and feed ranking should initially be simple and explainable: newest, trending votes, and ingredient match. Do not let paid placements alter vote totals.

### 2.5 Share a cooked result externally

A social reward is available only for a user’s own approved cooked-result photo. On request, render a short 9:16 MP4 with that photo, the recipe name, Crime Level, taste score, and the user’s verdict. The app shows a preview and editable caption, then asks the user to confirm each destination before any platform upload starts.

Do not include the AI concept image in the reward-eligible clip. For TikTok, create media that follows TikTok’s current sharing rules, including its restrictions on app logos and watermarks. Apply the platform’s AI-content disclosure metadata when required by its current rules.

## 3. Monetization and daily generation allowance

### Generation allowance

Each user may generate up to five recipes per UTC calendar day:

- Three free generations.
- Up to two extra daily slots earned from completed rewarded ads and verified public social posts, combined.
- One rewarded ad or one qualifying social post earns one extra slot, up to the two-slot daily cap.
- Earned slots are for that UTC day and do not roll over.
- A social post earns at most one slot per user per recipe, even if the same cooked result is published to both TikTok and Instagram.
- Users can use all three free generations without watching an ad or connecting a social account.
- Reserve quota atomically when the generation is queued. If generation permanently fails, refund the reserved slot exactly once. A retry of the same idempotent request does not consume another slot.

The API returns remaining free and earned slots and the time until reset. A user at the limit sees the choice to watch an available rewarded ad or publish an eligible cooked result; neither is required to keep using the app the next day.

### Ads

- Use clearly labeled native ads in the feed at a modest, configurable frequency.
- Offer rewarded ads only when the user chooses an extra generation. Explain the reward before playback.
- Never force an interstitial after generating a recipe or submitting a photo.
- Verify rewarded-ad callbacks server-side with AdMob SSV. Deduplicate by AdMob transaction ID and validate the signed callback. [AdMob SSV documentation](https://developers.google.com/admob/android/ssv)
- Keep ad events and recipe votes independent; ads must not affect ranking or public stats.

Social sharing is an optional user action for distribution and a daily generation reward, not a prerequisite for using the core product.

## 4. Technical architecture

### 4.1 Application stack

- **Client:** Expo + React Native for iOS and Android; Expo Router for navigation and deep links.
- **Public recipe web pages:** Expo Router web server rendering, deployed to a server-capable Expo hosting target. Use dynamic routes and server-generated metadata; static output alone is not sufficient for an open-ended user-generated recipe catalog. Expo documents dynamic SSR and route metadata in its [server-rendering guide](https://docs.expo.dev/router/web/server-rendering/).
- **Backend:** Supabase Auth, Postgres, Storage, and Queues (PGMQ).
- **API boundary:** Supabase Edge Functions authenticate app requests and call narrowly scoped Postgres functions for transactions such as credit reservation plus enqueue.
- **Workers:** TypeScript worker service on Google Cloud Run pulls durable jobs, calls Gemini, processes images, renders MP4s, and publishes approved social posts.
- **Secrets:** Gemini keys, Supabase service credentials, signing keys, ad validation keys, and social refresh tokens stay on the server. The mobile/web clients never receive provider secrets or broad database credentials.

~~~mermaid
flowchart LR
  App[Expo iOS / Android] --> Edge[Supabase Edge Functions]
  Web[SSR public recipe pages] --> DB[(Supabase Postgres)]
  Edge --> DB
  Edge --> Storage[(Supabase Storage)]
  Edge --> Q[Supabase Queues / PGMQ]
  Q --> Worker[TypeScript worker on Cloud Run]
  Worker --> Gemini[Gemini text and image APIs]
  Worker --> Storage
  Worker --> TikTok[TikTok Content Posting API]
  Worker --> Instagram[Instagram Content Publishing API]
  AdMob[AdMob SSV] --> Edge
  TikTok --> Webhooks[Verified provider webhooks]
  Instagram --> Worker
  Webhooks --> Edge
~~~

Supabase documents Queues as a Postgres-native durable queue built on PGMQ; use a private worker role and keep queue functions unavailable to ordinary clients. [Supabase Queues](https://supabase.com/docs/guides/queues) The queue consumer must tolerate redelivery: visibility timeout, retries, dead-letter/archival handling, and idempotent side effects are required. Keep a queue adapter boundary so the worker can move to another managed queue if operating requirements or the current Queues service maturity require it.

### 4.2 Generation pipeline

1. Client calls the authenticated generation endpoint with an idempotency key.
2. A database transaction checks the user’s daily free/earned allowance, reserves one generation slot, creates the generation job, and enqueues it. No job or reservation is committed if the transaction fails.
3. The worker validates the request and calls the Gemini text model using structured JSON output.
4. The worker validates the recipe schema and constraints, then calls the Gemini image model once for a square 1K concept image.
5. The worker stores the image and structured recipe, marks the job complete, and makes the draft visible to its owner.
6. On a permanent failure, the worker marks the job failed and writes one refund ledger entry. Retries use the same job ID and cannot produce duplicate charges, recipes, or refunds.

Use configurable model IDs: an initial text-model candidate such as Gemini 3.1 Flash Lite and image model gemini-3.1-flash-lite-image. Keep model names and prompts versioned in server configuration, not client code. Return structured recipe data using the Gemini API’s [structured output / JSON-schema feature](https://ai.google.dev/gemini-api/docs/structured-output). The image prompt should depict the dish only, with no typography, labels, logos, or recipe text.

The current listed standard paid price for a 1K image from Gemini 3.1 Flash Lite Image is about $0.0336. At the maximum five images per day for 1,000 users over 30 days, image output alone is about **$5,040/month** before text generation, retries, storage, moderation, ad revenue, or video rendering. This estimate assumes one image per successful generation and should be rechecked before launch because provider pricing and model availability change. [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

### 4.3 Worker and failure handling

- Use a bounded number of worker attempts with exponential backoff for transient provider, network, and storage errors.
- Record provider request IDs, prompt version, model ID, latency, and sanitized error category. Do not log access tokens, signed media URLs, or full sensitive prompts.
- Treat model output as untrusted data: schema-validate it, enforce ingredient exclusions, moderate it, and reject or regenerate if constraints are violated.
- Make every handler idempotent. Uniqueness constraints and ledger keys, rather than “worker ran once” assumptions, protect against duplicate side effects.
- Archive exhausted messages and expose a supportable retry path for transient jobs.

## 5. Data model

Initial Postgres entities:

| Entity | Key fields and purpose |
| --- | --- |
| profiles | user ID, display name, avatar, timezone, account status |
| recipes | owner, slug, visibility, title, request constraints, structured recipe, generated image path, weirdness, crime stats, prompt/model version, moderation state, timestamps |
| generation_jobs | owner, request idempotency key, status, attempt count, provider IDs, error category, reserved ledger entry |
| cooked_results | recipe, submitting user, private original photo path, approved public image path, taste score 1–5, short verdict, moderation state |
| recipe_votes | recipe, user, vote value (Guilty or Acquitted); one current vote per user and recipe |
| credit_ledger | user, daily bucket, entry type, amount, source ID, idempotency key; append-only record of reserve, earn, consume, and refund |
| social_connections | user, provider, account type, scopes, encrypted token reference, expiry and revocation state |
| social_publications | cooked result, provider, preview asset, publish ID, status, final provider state, credit-award reference |
| moderation_reports | reporter, target, reason, review state, timestamps |
| user_blocks | blocker, blocked user; unique pair |

Use row-level security for user-owned data. Public recipe access must require published visibility and approved content. Only the server can read/write provider tokens, credit ledger rows, and queue messages. Store raw uploads in a private bucket; serve a re-encoded, metadata-stripped public derivative only after moderation approval. Provide account deletion and revoke connected social tokens during deletion.

Suggested constraints:

- Unique generation request per user and idempotency key.
- Unique AdMob transaction ID.
- At most one social reward per user and recipe, regardless of provider count.
- At most one vote per user and recipe.
- Only one cooked-result rating per submission, with score constrained to 1–5.
- A public cooked-result record must reference a successfully moderated image.
- Ledger entries are immutable; corrections are compensating entries, not updates.

## 6. API contracts

All client routes require Supabase Auth unless marked as a provider callback. Validate request sizes and rate limits at the API boundary. Use versioned routes, stable error codes, pagination cursors, and an Idempotency-Key header for mutations.

| Operation | Contract |
| --- | --- |
| Generate recipe | **POST /v1/generations** with ingredients, exclusions, servings, weirdness, constraints, and idempotency key. Returns 202 with job ID and remaining daily slots. |
| Read generation | **GET /v1/generations/{jobId}** returns queued, processing, complete, or failed state; completed state includes recipe ID. |
| Read/search recipes | **GET /v1/recipes** supports text, ingredient, and sort filters. **GET /v1/recipes/{slug}** returns only public, approved recipes to anonymous clients. |
| Publish case file | **POST /v1/recipes/{recipeId}/publish** checks ownership and moderation, then makes the recipe discoverable. |
| Vote | **PUT /v1/recipes/{recipeId}/vote** sets Guilty or Acquitted for the authenticated user. No photo required. |
| Upload cooked photo | **POST /v1/uploads/sign** returns a short-lived private upload URL and object key; **POST /v1/recipes/{recipeId}/cooked-results** submits the uploaded photo, taste score, and verdict for moderation. The photo is required. |
| Social preview | **POST /v1/social/previews** takes an approved cooked-result ID and platform, queues rendering, and returns a preview job ID. No provider upload occurs yet. |
| Confirm social post | **POST /v1/social/publications** takes a ready preview and explicit confirmation; returns publication ID and pending status. |
| Read social status | **GET /v1/social/publications/{publicationId}** returns rendering/publishing/processing/published/failed state and reward status. |
| Rewarded ad callback | **GET /v1/webhooks/admob/ssv** is a server callback; verify signature, transaction ID, user mapping, reward amount, and daily cap before granting credit. |
| Social provider callback | **POST /v1/webhooks/tiktok** validates provider signature and publication ID, then applies the final state idempotently. Instagram status is polled or received through an available provider notification mechanism. |

Generation request example:

~~~json
{
  "ingredients": [
    { "name": "eggs", "quantity": "2" },
    { "name": "leftover rice", "quantity": "1 cup" }
  ],
  "excludedIngredients": ["peanuts"],
  "servings": 2,
  "weirdness": 72,
  "constraints": {
    "maxMinutes": 30,
    "equipment": ["stovetop"],
    "dietary": []
  }
}
~~~

The generation response is asynchronous:

~~~json
{
  "jobId": "gen_123",
  "status": "queued",
  "allowance": {
    "freeRemaining": 2,
    "earnedRemaining": 1,
    "dailyMaximum": 5,
    "resetsAt": "2026-11-08T00:00:00Z"
  }
}
~~~

Use JSON schema validation for recipe title, description, servings, ingredient quantities, ordered steps, time estimates, allergen declarations, satire stats, and image prompt. Record both the user’s selected exclusions and the final model output so a mismatch can be surfaced and corrected.

## 7. Social API behavior

### TikTok

Assume the app has completed the audit/verification needed for public Direct Post, per the product decision. Keep the API client secret server-side. Start upload only after explicit consent, show the user the destination and editable caption, and track the returned publish ID through final completion. TikTok supports status polling and content-posting webhooks; its PUBLISH_COMPLETE state indicates that a Direct Post has been posted. Award a social credit only after a final successful state confirms the post was published, and only once per recipe. If a user chooses a non-public destination or TikTok cannot confirm completion, do not award the verified-public-post credit. [TikTok status API](https://developers.tiktok.com/docs/en/content-posting-api-reference-get-video-status) · [TikTok Direct Post](https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post) · [TikTok content sharing guidelines](https://developers.tiktok.com/docs/en/content-sharing-guidelines)

If public Direct Post verification is not in place in a deployment, the API may restrict posts to private visibility. In that case, disable the verified-post credit and offer the ordinary share flow until the required access is available.

### Instagram

Use Meta’s official Content Publishing API for a connected professional Creator or Business account. Create a media container from a publicly fetchable, short-lived asset URL, wait for processing to finish, then publish and persist the resulting provider media ID. Do not treat container creation or upload acceptance as proof of publication. Personal accounts use the operating system’s share sheet; this path is useful for sharing but cannot grant a verified-post credit. [Instagram Content Publishing](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing)

### Shared state machine

~~~text
preview_requested
  -> rendering
  -> ready_for_confirmation
  -> publishing
  -> provider_processing
  -> published
  -> credit_awarded

Any failure -> failed
User cancels before publishing -> cancelled
~~~

Persist provider IDs and each state transition. Use webhooks where available and bounded polling as a fallback. A webhook may arrive more than once or out of order; verify its source, look up the publication by provider ID, and reject duplicate transitions. Keep OAuth refresh tokens encrypted and support disconnection and token revocation.

## 8. Safety, privacy, and moderation

- Add clear allergy/exclusion input and validate generated ingredients against it before returning a recipe. Do not claim that a generated recipe is medically or allergy safe.
- Use recipe output checks to reject dangerous food handling instructions and unsupported health claims. Keep weirdness about flavor combinations, not unsafe preparation.
- Strip EXIF/location metadata from cooked photos; validate MIME type, file size, and decoded image dimensions. Keep originals private and serve a resized derivative.
- Moderate recipe text, generated images, user photos, captions, and verdicts before public display or social publishing. Provide report, block, takedown, and support-contact flows.
- Keep draft recipes and pending uploads inaccessible to other users and search engines.
- Apply rate limits, abuse controls, account deletion, retention limits, and audit logs for moderator actions.
- Clearly identify AI-generated recipe content and concept images. The community’s real cooked-result photo remains visually separate from the AI concept.
- Follow the current platform review and user-generated-content requirements. Apple’s App Review Guidelines call for filtering, reporting, timely responses, blocking, and published contact information for UGC apps. [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

## 9. Non-functional requirements and monitoring

- **Correctness:** No user may consume more than five daily generation slots; duplicate callbacks, retries, or repeated requests cannot create duplicate credits.
- **Privacy:** RLS covers every user-owned table. Public read policies expose only published recipes and approved cooked-result derivatives.
- **Availability:** Generation is asynchronous and recoverable. The client can resume a job after app restart.
- **Latency:** Show queue and provider state promptly; measure p50/p95 time from accepted request to recipe ready. Establish launch targets after provider baseline measurements.
- **Accessibility:** Screen-reader labels for the weirdness slider, ratings, camera action, crime metrics, and votes; color is never the only vote/status indicator.
- **Observability:** Track generation volume, recipe and image failure rate, queue depth and age, retries, refund count, cost per successful generation, rewarded-ad completion, social publication completion, moderation time, photo-to-review conversion, and feed reports.
- **Cost controls:** Per-user and global daily limits, provider spend alerts, image size limits, prompt limits, retry limits, and a feature flag for disabling image generation during provider incidents.

## 10. Verification plan and acceptance criteria

This section is the implementation team’s QA plan; no application code or tests are included in this document change.

- Concurrent generation calls at the daily boundary never exceed three free plus two earned slots.
- Replaying an idempotency key creates no second generation job or charge.
- Duplicate AdMob SSV callbacks grant one reward; invalid signatures and reused transaction IDs grant none.
- Provider retries do not create duplicate recipes or images; permanent failure refunds exactly once.
- A cooked review cannot be submitted without an image, valid 1–5 score, and verdict.
- Recipe detail layout always places the AI concept first, cooked-result photos beneath, and each cooked photo’s score, verdict, and Crime Level directly below that photo.
- Private recipes and pending images are not served to anonymous users or indexed; publishing creates the public route and metadata.
- TikTok and Instagram credits are granted only once after verified final publication, never on preview, upload acceptance, or processing state.
- Instagram personal-account share-sheet posts do not receive a verified credit.
- Camera denial provides the gallery fallback; failed uploads can resume without duplicate cooked-result records.
- Report/block/takedown behavior is accessible from public content; rejected media never becomes public.

## 11. Delivery sequence

1. **Foundation:** Expo app, Supabase project, auth, RLS, migrations, private storage, queue and worker deployment.
2. **Recipe generation:** Structured recipe contract, Gemini adapters, job status UI, image generation, failure/refund path, spend monitoring.
3. **Core community:** Private drafts, publish flow, feed/search, recipe votes, server-rendered public recipe pages and metadata.
4. **Cooked proof:** Camera-first upload, metadata stripping, moderation, score/verdict, generated-image-above/cooked-photo-below recipe layout.
5. **Monetization:** Daily ledger, AdMob rewarded flow and SSV, clearly labeled feed ads.
6. **Social posting:** Preview rendering, TikTok Direct Post, Instagram professional publishing, status callbacks, deduped reward grants.
7. **Launch hardening:** Store review requirements, moderation operations, provider failure drills, cost dashboards, accessibility and privacy review.

## 12. Decisions and assumptions

- Food Felonies is a working name; final branding is open.
- The product launches on iOS and Android, with public web recipe pages.
- The repo is greenfield; implementation begins from this document.
- The user explicitly wants three free generations plus at most two earned generations per day, with a hard total of five.
- Rewarded ads and verified social publishing share the same two-extra-slot daily cap.
- Public case-file publishing is explicit. Cooked results are separate, photo-required submissions.
- TikTok public Direct Post audit is treated as completed for launch planning. Instagram API rewards require a professional Creator or Business account; personal accounts use non-rewarded OS sharing.
- Only a cooked-result photo can earn a social reward. A user confirms every external post.
- UTC defines the v1 daily reset; display the exact reset time in the client. Revisit this if user research strongly favors local-midnight resets.
- The provider prices and model IDs in this document are planning inputs and must be revalidated before launch.
- The social APIs, queue service, app-store review rules, and model pricing can change; keep provider-specific details behind adapters and review the linked documentation during implementation.

## References

- Competitor product examples: [Chowy](https://www.chowy.app/), [Supper](https://supperapp.io/), [Samsung Food](https://samsungfood.com/)
- Gemini API: [structured outputs](https://ai.google.dev/gemini-api/docs/structured-output), [pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Queue: [Supabase Queues](https://supabase.com/docs/guides/queues)
- Web rendering: [Expo Router server rendering](https://docs.expo.dev/router/web/server-rendering/)
- Ads: [AdMob rewarded-ad server-side verification](https://developers.google.com/admob/android/ssv)
- TikTok: [Direct Post](https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post), [status](https://developers.tiktok.com/docs/en/content-posting-api-reference-get-video-status), [sharing guidelines](https://developers.tiktok.com/docs/en/content-sharing-guidelines)
- Instagram: [Content Publishing API with Instagram Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing)
- UGC: [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

