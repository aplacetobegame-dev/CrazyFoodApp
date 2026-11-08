# Checked in for a later deploy. This image is not built or published in the local foundation pass.
# Export the web bundle first: pnpm --filter @food-felonies/mobile export:web
FROM node:24-alpine

RUN corepack enable

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/contracts/package.json packages/contracts/package.json
COPY services/worker/package.json services/worker/package.json
COPY apps/mobile/package.json apps/mobile/package.json

RUN pnpm install --frozen-lockfile --filter @food-felonies/mobile...

COPY apps/mobile apps/mobile

WORKDIR /app/apps/mobile

ENV PORT=8080
EXPOSE 8080

CMD ["node", "server.js"]
