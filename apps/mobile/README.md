# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Run pnpm install from the repository root.
2. Start Metro from the repository root.

   ```sh
   pnpm run mobile --test
   ```

3. On Android, open [Expo Go for SDK 58](https://expo.dev/go?device=true&platform=android&sdkVersion=58) and scan the terminal QR code while connected to the same Wi-Fi as the computer.

Test mode opens Discover with sample recipes and skips sign-in and Supabase. Drafts, votes, selected photos, and sample outcomes stay in the preview session.

- Open a sample case from Discover to try the public share-card link, reporting, blocking, or in-app camera and gallery.
- Generate a sample draft to try generation and publish failure and retry.
- Save a cooked review to try approval, rejection, replacement, and sample posting outcomes.
- Open Profile for rewarded-ad verification, account dialogs, sample clip playback, and the separate staff moderation queue.
- Open /recipe/pickle-rice in the Metro web preview to test a direct anonymous sample link.

### Test with Supabase

Set the following in apps/mobile/.env.local:

```dotenv
EXPO_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_YOUR_KEY
```

For local Supabase on a phone, use your computer's LAN address in the URL. Run pnpm run mobile from the repository root to start the connected app. Release builds use the connected flow.

You can start developing by editing the files inside the **src/app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **example** directory and create a blank **src/app** directory where you can start developing.

### Other setup steps

- To set up ESLint for linting, run `npx expo lint`, or follow our guide on ["Using ESLint and Prettier"](https://docs.expo.dev/guides/using-eslint/)
- If you'd like to set up unit testing, follow our guide on ["Unit Testing with Jest"](https://docs.expo.dev/develop/unit-testing/)
- Learn more about the TypeScript setup in this template in our guide on ["Using TypeScript"](https://docs.expo.dev/guides/typescript/)

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
