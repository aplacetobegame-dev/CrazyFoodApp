# Checked in for a later deploy. This image is not built or published in the local foundation pass.
FROM node:24-alpine

RUN corepack enable

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/contracts/package.json packages/contracts/package.json
COPY services/worker/package.json services/worker/package.json
COPY apps/mobile/package.json apps/mobile/package.json

RUN pnpm install --frozen-lockfile --filter @food-felonies/mobile...

COPY apps/mobile apps/mobile

ARG EXPO_PUBLIC_SUPABASE_URL=http://127.0.0.1:55321
ARG EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=build-placeholder
ENV EXPO_PUBLIC_SUPABASE_URL=$EXPO_PUBLIC_SUPABASE_URL
ENV EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=$EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY
ENV CI=1

RUN pnpm --filter @food-felonies/mobile export:web

WORKDIR /app/apps/mobile

ENV PORT=8080
EXPOSE 8080

CMD ["node", "server.js"]
