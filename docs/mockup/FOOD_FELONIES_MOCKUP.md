# Food Felonies v1 mockup brief

Food Felonies is a mobile-first recipe generator and community for unusual, cookable food. Users enter ingredients, exclusions, servings, and a weirdness level. The app creates a private recipe with an AI concept image. Users can publish the recipe, cook it, and submit a real photo with a taste score and verdict. The public case file shows the concept above the results from real kitchens.

The v1 mockups cover iOS and Android, plus public recipe pages for mobile and desktop web.
See the [product and technical design](../PRODUCT_AND_TECH_DESIGN.md) for the underlying requirements.
This brief covers layouts, controls, copy, transitions, and state variants. Screen names, navigation, example copy, and layout suggestions are proposed design choices. Product rules come from the blueprint. Section 9 lists the decisions to resolve before finalizing the mocks.

## 1. Navigation and prototype paths

Use four bottom tabs. Keep them visible on top-level mobile screens. Give the camera and clip preview room to take over the screen when needed.

| Tab | Contents |
| --- | --- |
| **Discover** | Feed, search, ingredient filters, and public case files. |
| **Create** | Ingredient form, current allowance, and the generation entry point. |
| **My Cases** | Generation jobs, recipes grouped by privacy state, and the user's cooked submissions. |
| **Profile** | Account details, connected accounts, privacy, support, and account deletion. |

Connect these paths in the prototype.

| Path | Frames to link |
| --- | --- |
| **Generate and publish** | Create → Generation status → Private case file → Publish confirmation → Public case file |
| **Cook and prove it** | Case file → Camera → Photo preview → Cooked review form → Pending review → Approved cooked result |
| **Discover and vote** | Discover → Search → Public case file → Select or change vote |
| **Earn via ad** | Allowance sheet → Reward offer → Provider ad → Verifying reward → Slot added |
| **Earn via social post** | Approved cooked result → Destination → Account connection if needed → Clip preview → Confirm → Post status → Reward outcome |
| **Open a shared link** | Social link preview → Public recipe web page → Open app or sign in for an action |
| **Report content** | Public case or cooked result → Overflow → Report → Confirmation |

## 2. Visual language and reusable components

The case-file theme belongs in titles, Crime Level, and verdicts. Keep cooking instructions, permissions, privacy, and errors plain. As a starting point, use a warm neutral background, dark readable text, and an accent for case-file details. Treat colors and typography as working directions while branding is open.

| Component | Design notes |
| --- | --- |
| **AI concept image** | Square recipe hero with the visible label **AI-generated concept image** outside the image. Keep the label on concept thumbnails too. Identify the recipe itself as AI-generated in the summary. |
| **Cooked-result card** | Real dish photo, immediately followed by **Taste: 4/5**, the verdict, and **Crime Level: 72/100**. Put attribution, date, and overflow controls outside that three-line group. Use a text label such as **Cooked by Maya** to distinguish the photo from the concept. |
| **Recipe card** | Concept thumbnail, title, short description, Crime Level, and Guilty / Acquitted counts. Use the same card in the feed and search. |
| **Stats and votes** | Treat Crime Level as a recipe stat out of 100, Taste as a review rating out of 5, and Guilty / Acquitted as labeled vote buttons. Crime Level describes the joke and carries no food safety meaning. |
| **Status labels** | Use text for **Private draft**, **Public**, **Queued**, **Generating**, **Pending review**, **Approved**, **Rejected**, and **Failed**. Pair any color with a label or icon. |
| **Allowance** | Compact free and earned counts on Create. The detailed sheet adds the reset time and eligible earning actions. |
| **Feed ad** | Native card with a visible **Ad** label and its own layout. Keep its controls distinct from recipe votes. |

Design visible focus and selected states. Give the weirdness slider, taste selector, camera controls, votes, and stat badges accessible names and values. Test long titles, long ingredient lists, text scaling, and screen-reader reading order. Keep bottom actions reachable when the keyboard is open, and include a compact phone and a wide web frame.

### Sample case for the mockups

Reuse the same case through creation, voting, proof, and sharing. The names and numbers below are sample data.

| Field | Sample |
| --- | --- |
| Case | **Pickle-Maple Crispy Rice** |
| Summary | Leftover rice crisped in a pan with egg, dill pickles, and a little maple syrup. |
| Create inputs | Leftover rice, eggs, dill pickles, maple syrup. Exclude peanuts. Two servings, stovetop, up to 30 minutes, weirdness 72/100. |
| Stats | **Crime Level 72/100** · **Regret Potential 38/100** |
| AI concept | Square, polished image of a plated rice cake. Render the label in the UI. |
| Cooked proof | Phone photo of a browned rice cake on a home plate, submitted by Maya. |
| Taste and verdict | **Taste: 4/5** · “The pickle crunch actually works.” |
| Community vote | **Guilty 18** · **Acquitted 7** |

## 3. Entry, discovery, and generation

### 01 — Welcome and authentication

- Show the product name, a short description, and sign-in and account-creation actions. Use a line such as “Make a recipe. Cook it. Show the evidence.”
- When authentication interrupts an action, return the user to that action after sign-in where possible. Mock a generic authentication form until the sign-in method is chosen.
- Mock first visit, invalid or failed sign-in, expired session. Public web recipes remain readable anonymously.

### 02 — Discover feed

- Show a header, search entry, sort control, scrolling recipe cards, and a clearly labeled ad between cards. Start with **Newest** and **Trending** as feed sorts.
- Open a public case by tapping its card. Keep votes in the case file so feed card interactions stay simple.
- Mock loading skeletons, loaded feed with an ad, empty feed, load error with retry, loading another page.

### 03 — Search and results

- Show a search field, selected ingredient chips, filter and clear controls, sort, and recipe cards. Show **Ingredient match** when ingredients are supplied.
- Let the user change the query or remove one ingredient without clearing the rest.
- Mock initial search, text query, active ingredient filters, no results, loading, and error.

### 04 — Create recipe

- Show the allowance near the top. Follow with **Ingredients on hand**, **Exclude ingredients**, servings, a **Normal → Food Felony** slider with a visible 0–100 value, and expandable **More options** for cuisine, time, equipment, and dietary constraints. Put **Generate recipe** at the bottom.
- Add or remove ingredients, optionally enter a quantity on each, add exclusion chips, step servings up or down, and adjust weirdness. Show a brief note beside the exclusions, such as “We send these exclusions to the recipe service when you generate a recipe.” Avoid claims of allergy safety.
- Mock initial and filled form, invalid fields, request in progress, generation temporarily unavailable, and no available slots. With no slots, open the allowance sheet and keep the user's inputs.

### 05 — Generation status

- Show the job status, a concise explanation, and **Back to My Cases**. While the job runs, show copy such as “You can leave this screen. Your recipe will appear in My Cases when it’s ready.”
- Show **Open case file** on completion. The saved case starts private. A user returning after an app restart can reopen the same job.
- Mock queued, generating, ready, and permanent failure. After a permanent failure, show **Slot returned** and a retry action. Use status labels without percentage estimates unless the app can measure progress.

### 06 — My Cases

- Group **Recipes** and **Cooked submissions**. Within Recipes, show active jobs and label completed cases as private or public. On a cooked submission, show its thumbnail, recipe title, and moderation status.
- Open an active job, a case file, or the user's own submission status. Make the primary empty-state action **Create a recipe**.
- Mock first use, active job, completed private draft, published recipe, pending proof, and failed job or rejected proof.

## 4. Case file and cooked proof

### 07 — Recipe case file

Use one layout for the private draft and public recipe. Preserve this scroll order in mobile and web mocks.

| Order | Section | UI details |
| --- | --- | --- |
| 1 | **Name and summary** | Recipe title, description, servings, estimated time, AI-generated recipe label, and private or public status where useful. Put owner or share actions in the header. |
| 2 | **Concept image** | Square hero with the visible **AI-generated concept image** label. |
| 3 | **Case stats** | Crime Level and other available satirical stats, each with a readable label and value. |
| 4 | **Recipe** | Ingredients with quantities and numbered instructions. Surface relevant allergen declarations where available. |
| 5 | **Cook action** | **I cooked it — add proof** opens the camera flow. |
| 6 | **Cooked results** | Real photos. Directly beneath each, show taste, verdict, and recipe Crime Level in that order. For the empty state, use copy such as “Be the first to cook it and add a photo.” |
| 7 | **Community** | **Guilty** and **Acquitted** with totals and the user's current selection. Users can change their one current vote. Comments appear only if enabled. |

Mock the private owner view with **Publish case file** and the public view with **Share case link**. On public content, include reporting and blocking in an overflow menu. Use a private status treatment for pending proof visible to its submitter, separate from the public cooked-results list. Show approved proof publicly only when the recipe is public as well. Create public variants with zero and multiple cooked results, plus one with a selected vote.

### 08 — Publish case file

- Use a confirmation sheet with recipe title, privacy change, and the **Publish case file** action. Use copy such as “Your case will appear in Discover, search, and on a public web page. Cooked photos appear publicly after approval.”
- Mock review, submitting, success with **View public case** or **Share case link**, and blocked or failed publication with a clear next step.
- Publication requires explicit owner confirmation and the recipe must pass moderation.

### 09 — Camera, permissions, and photo review

- Use a full-screen camera with close and capture controls. After capture, show the photo with **Retake** and **Use photo**.
- Mock the system camera prompt. If permission is denied or the camera is unavailable, show **Choose from gallery** and mock the system gallery picker handoff.
- Mock first permission request, granted, denied, camera unavailable, capture cancelled, selected image invalid, and selected photo ready.

### 10 — Cooked review form

- Show a photo preview with a replace action, a labeled **Taste** selector from 1 to 5, short **Verdict** field, and **Submit for review**.
- Require the photo, a valid rating, and verdict. Keep all inputs visible or recoverable if the upload fails. Show upload progress and a retry path.
- Mock incomplete, valid, uploading, failed with retry, and accepted for moderation. Confirm submission with copy such as “Your photo and verdict are in review.”

### 11 — Cooked proof status

- Show the photo, taste, verdict, recipe title, and current status. This can be a detail view reached from My Cases.
- Mock **Pending review**, **Approved** on a private case, **Approved** and publicly visible, and **Rejected**. Use a reason or support action when available.
- Offer **Share my cooked result** for the user's own approved submission. Keep public visibility separate from moderation approval.

## 5. Daily allowance and rewarded ads

### 12 — Daily allowance

- Use a sheet with free slots remaining, earned slots remaining, earned slots used toward the daily cap, and the exact reset time. Present the reset in local time with the date when it falls tomorrow, and explain that the allowance follows the UTC day.
- Use copy such as “You get 3 free generations each day. Earn up to 2 more.” Earned slots expire at reset. An eligible ad or verified public social post earns one slot.
- Offer **Watch an ad** and **Share an eligible cooked result** when available. If the user has reached the earning cap, show when the next free slots are available.
- Mock free slots available, earned slots available, no usable slots with earning available, no eligible earning action, and earning cap reached.

### 13 — Rewarded ad

- Explain the reward before launch. Label the action **Watch ad for 1 generation**. Sketch the provider handoff and the app's return screen.
- Mock ad unavailable, ad closed early, **Verifying reward**, and **1 generation added**. Update the allowance after verification.
- Enter from an explicit earning action. The recipe generation and photo submission flows have no forced ad step.

## 6. Social sharing

### 14 — Choose cooked result and destination

- From the allowance sheet, list the user's approved cooked results. From an approved result, preselect that photo. Show TikTok, Instagram, and ordinary device sharing where applicable. Display the connected account and explain reward eligibility by destination.
- Mock no eligible photo, account connection required, account expired, TikTok public posting unavailable, Instagram personal account, and reward already earned for the recipe.
- A reward requires a verified public post. Instagram verified posting uses a connected Creator or Business account. Personal accounts can share through the device share sheet. If TikTok public posting is unavailable, offer ordinary sharing where supported. The device share sheet earns no verified slot.

### 15 — Connect or reconnect account

- Show the provider and purpose, **Connect account**, provider handoff, and a return state showing the connected account. Account connection alone leaves the post unsubmitted.
- Mock connecting, connected, cancelled, failed, expired, and reconnect required. Let the user return to destination selection.

### 16 — Clip preview and confirm

- Show a playable **9:16** MP4 preview with the real cooked photo, recipe name, Crime Level, Taste, and verdict. Use safe margins around the on-video text. Show the destination, connected account, editable caption, and visibility options where supported.
- Confirm each destination individually with a button such as **Post to TikTok**. Before confirmation, allow the user to go back or cancel. Follow the provider's required disclosure and posting controls when those are confirmed for implementation.
- Mock rendering, ready, preview failed with retry, caption validation, and cancelled. Build the clip from the cooked photo. The AI concept belongs on the case file.

### 17 — Publication status and reward

- Use one status card per destination, with the recipe and photo thumbnail. Separate the platform status from the reward outcome.
- Mock **Publishing**, **Platform processing**, **Published**, **Failed**, **1 generation added**, and **Published without a reward**. Explain why when known, such as a non-public post, the daily earning cap, or an earlier reward for this recipe.
- Grant the slot after verified public publication. A user earns at most one social slot per recipe across both platforms.

## 7. Profile, safety, and public web

| ID | Surface | Layout, actions, and states |
| --- | --- | --- |
| 18 | **Profile and settings** | Display name and avatar, connected accounts, privacy, support, sign-out, and delete account. Include disconnect and deletion confirmations and completion or error states. Keep account settings separate from any future public profile. |
| 19 | **Report content** | Open from a public recipe or cooked result. Show the target, reason picker, **Submit report**, success, and retryable failure. |
| 20 | **Block user** | Show the account and explain the effect before confirmation. Include success and failure. Final confirmation copy depends on the chosen block behavior. |
| 21 | **Support and privacy** | Show where to contact support and open the chosen privacy information. A link or a simple screen can serve as the entry point. |
| 22 | **Public recipe page** | Mock mobile and desktop web with the same case-file order. Read access is anonymous. Show an app or sign-in entry for authenticated actions. Include unavailable-content and deep-link landing variants. |
| 23 | **Public link preview** | Mock the shared card with recipe title, description, and image. Use published and approved content for public pages, preview metadata, search results, and sitemaps. |
| 24 | **Internal moderation** | Suggested staff surfaces are a queue and detail view for recipes, images, verdicts, captions, and reports. Show review state, the content and report reason, approve, reject, takedown, and action history. Keep these surfaces outside the consumer navigation. |

## 8. Frame handoff checklist

Start with one realistic end-to-end prototype. Create a recipe, open the private case, publish it, then capture and submit the cooked proof. Finish on the public case with the AI concept and real cooked photo clearly distinguished, with the review directly below the cooked photo. Add the reward and web paths after that prototype reads clearly.

Before handing off the mocks, check the following.

- [ ] The case file follows the fixed reading order on mobile and public web.
- [ ] Every concept image is clearly labeled, and empty cooked results invite the first real photo.
- [ ] Crime Level, Taste, and votes look and read like three different values.
- [ ] The camera opens first, gallery fallback is reachable, and upload retry preserves the entered review.
- [ ] Draft, pending, rejected, and approved states show the right audience and actions.
- [ ] The allowance shows separate free and earned counts, the reset, and the cap. The generation failure shows the returned slot.
- [ ] Ad verification and social reward verification each have a waiting and outcome frame.
- [ ] Social preview uses the cooked photo, and each destination has an explicit confirmation.
- [ ] Both public share paths are legible. **Share case link** sends the recipe URL. **Share my cooked result** opens the clip flow.
- [ ] Report, block, support, disconnect, and account deletion can each be found in the prototype.
- [ ] Loading, empty, error, permission, and signed-out states are accounted for. Reuse component variants for states that share a layout.

## 9. Open decisions before finalizing

- **Branding and language.** Food Felonies is a working name. Final colors, type, and the exact scale labels remain open.
- **Sign-in and onboarding.** Choose the supported sign-in methods and whether users can browse Discover before signing in on mobile. The public web recipe is readable without an account.
- **Form limits.** Confirm ingredient and verdict lengths, servings range, and the supported cuisine, equipment, and dietary choices before finalizing validation copy.
- **Community scope.** Confirm whether comments ship, what blocking changes for each user, and whether authors can unpublish recipes or revise submitted proof.
- **Web actions and account settings.** Decide which actions are completed on web and which hand off to the app. Confirm the profile fields users can edit and the support channel.
- **Moderation and social.** Confirm which rejection details users can see, how resubmission works, what happens to external sharing for an approved result on a private case, and the required provider controls for each posting flow.
