# Small Changes and Onboarding A/B Tests

**Start here:** ship the three small changes, then run Test 1 on the first onboarding screen.

I wrote this from the design doc and haven't seen the app's code. The onboarding flow below is assumed, so adjust the steps to match what shipped.

## Part 1: Small changes to make first

### 1. Show the AI concept next to the real photo in the share clip

- **Change:** make the clip a reveal: AI concept, real photo, Crime Level, taste score, verdict stamp.
- **Why:** the gap between promise and reality is the joke. Design doc section 2.5 currently leaves the concept out of the reward-eligible clip.
- **Keep:** an "AI-generated concept" label on screen and the platform's AI disclosure. TikTok restricts app logos and watermarks, so the case-file look has to identify the app.
- **Done when:** a clip shows both images, and the user still previews it and confirms each post.

### 2. Add a one-tap share that doesn't require cooking

- **Change:** add a "Share this case file" button on every recipe. It creates an image with the dish name, AI concept, Crime Level and "Guilty or Acquitted?", then opens the phone's share sheet.
- **Why:** most people who generate a recipe won't cook it, and they currently have nothing to share.
- **Keep:** no generation reward for this share. The image is labeled as an AI concept, and private recipes need the owner to publish them first.
- **Done when:** a user can share within two taps of seeing a recipe, and the link opens the public case-file page.

### 3. Let people vote from a shared link without an account

- **Change:** add Guilty and Acquitted buttons to the public page. After voting, show the results and prompt the install.
- **Why:** design doc section 6 requires an account for client routes, which stops a curious visitor at the point they're most likely to join in.
- **Keep:** one vote per browser, rate limits and bot protection. Store anonymous votes separately from account votes so abuse can be filtered out.
- **Done when:** a logged-out visitor can vote in one tap, and repeat votes from the same browser don't count.

## Part 2: How to A/B test onboarding

### What "heavy" testing can mean at this size

Run tests back to back, one at a time, and only test big differences. Small tweaks can't be measured with a few hundred people.

| Baseline conversion | Lift you want to detect | People needed per version | Total |
|---|---|---|---|
| 50% | +20 points (to 70%) | about 95 | about 190 |
| 50% | +10 points (to 60%) | about 390 | about 780 |

These assume 80% power at a 5% significance level. So the 100–300 person quiet release has room for about one or two tests, and only for changes large enough to move a step by around 20 points. Add more tests as traffic grows.

### Assumed onboarding sequence

1. First screen
2. Enter ingredients and exclusions
3. Set the Crime Level slider
4. Sign up
5. Wait for generation
6. Case-file reveal
7. Dare to cook it
8. Upload proof
9. Share

### Setup

- **Tool:** use one tool for analytics and flags. PostHog supports both for React Native. Firebase A/B Testing is the alternative.
- **Assignment:** split 50/50 on first launch, keep each device in its version, and only count people who actually saw the tested screen.
- **Events:** `onboarding_viewed`, `ingredients_submitted`, `exclusions_viewed`, `slider_set`, `signup_completed`, `generation_requested`, `recipe_viewed`, `cook_dare_accepted`, `proof_uploaded`, `share_completed`. Attach `experiment` and `variant` to each.
- **Rules:** set the sample size before starting, don't stop early because one version looks ahead, and run each test for at least 7 full days so all weekdays are covered.
- **Decision:** ship the variant only if the 95% confidence interval for the difference excludes zero and no guardrail got worse. If the result is unclear, keep the simpler version.
- **Privacy:** update the privacy policy for analytics, and don't send ingredient exclusions to the analytics tool because they can reveal allergies or health details.

### Test 1 (start here): the first screen

**Hypothesis:** opening with the dare, instead of explaining the app, gets more new users to generate a first recipe.

| | A: Explain (control) | B: The dare |
|---|---|---|
| Visual | AI recipe card | AI concept next to a real cooked result, with a verdict stamp |
| Headline | "Turn your ingredients into wild recipes" | "The AI promised this. You made that." |
| Subtext | "Pick your ingredients and choose how weird it gets." | "What's in your fridge? Time to face the jury." |
| Button | "Get started" | "Commit a food crime" |

If the app already has a first screen, use it as version A instead.

| | |
|---|---|
| **Primary metric** | % of people who saw the screen and requested a recipe within their first session |
| **Secondary** | Recipe viewed, cook dare accepted, proof uploaded within 7 days, shared |
| **Guardrails** | Day-1 return, exclusions step viewed, support and safety reports |
| **Sample** | At least 95 people per version, and only a change of about 20 points will be reliably detected |

The real photo in version B must be one you have the rights to and must not be presented as a user's dish unless it is one. Label its AI image.

### Next tests, in order

Run these one at a time. Each one targets a single step.

| # | Step | A | B | Primary metric |
|---|---|---|---|---|
| 2 | Sign-up timing | Sign up before the first recipe | Sign up after the first recipe | First recipe viewed and account created |
| 3 | Ingredient entry | Blank field | One-tap "starter fridge" suggestions | Ingredients submitted |
| 4 | Slider start | Starts at 50 | Starts at 80 | First recipe saved or shared |
| 5 | Waiting screen | Progress status | Fake "trial in progress" comedy lines | Recipe viewed |
| 6 | Cook dare | "I cooked it" button only | "Cook it tonight?" dare with a set reminder | Proof uploaded within 7 days |
| 7 | Proof ask | Photo, score and verdict on one screen | Photo first, then score and verdict | Proof upload completion |
| 8 | Share prompt | Button on the results page | Prompt straight after the verdict is posted | Shares per cooked result |

Test 6 is the most important one, because generating a recipe to actually cooking it is the step the app depends on. Proof uploads will be rare, so expect it to need more people than the first tests. Run it as soon as traffic allows.

### Never test these

- Removing or hiding allergy and ingredient exclusions
- Removing the AI labels or the AI disclosure
- Posting to social accounts without the user's confirmation
- Forcing ads or social posts in order to use the three free generations
- Changing the daily generation limits or reward rules between versions
