FROM node:24-alpine

RUN apk add --no-cache ffmpeg \
  && corepack enable

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/contracts/package.json packages/contracts/package.json
COPY services/worker/package.json services/worker/package.json

RUN pnpm install --frozen-lockfile --filter @food-felonies/worker...

COPY packages/contracts packages/contracts
COPY services/worker services/worker

WORKDIR /app/services/worker

ENV PORT=8080
EXPOSE 8080

CMD ["pnpm", "start"]
