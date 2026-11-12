import { parseGenerationRequest } from "@food-felonies/contracts";
import postgres from "postgres";
import { buildFixtureRecipe } from "./fixture.ts";
import { PermanentJobError, type JobEffects } from "./handler.ts";
import { prepareCookedPhoto, renderStillClip } from "./media.ts";
import type { ObjectStore } from "./storage.ts";

type Sql = ReturnType<typeof postgres>;

function sqlState(error: unknown): string | null {
  if (typeof error === "object" && error !== null && "code" in error && typeof error.code === "string") {
    return error.code;
  }
  return null;
}

type Source = { bucket: string; path: string; ownerId: string } | null;

export function createJobEffects(sql: Sql, storage: ObjectStore | null): JobEffects {
  return {
    async completeGeneration(jobId) {
      const rows = await sql<{ status: string; request: unknown }[]>`
        select status, request from public.generation_jobs where id = ${jobId}::uuid
      `;
      const job = rows[0];
      if (!job) throw new PermanentJobError("missing_job");
      if (job.status === "complete" || job.status === "failed") return;
      const request = parseGenerationRequest(job.request);
      if (!request) throw new PermanentJobError("invalid_request");
      const document = buildFixtureRecipe(request);
      try {
        await sql`select private.complete_generation(${jobId}::uuid, ${sql.json(document)})`;
      } catch (error) {
        const code = sqlState(error);
        if (code === "22023" || code === "P0002") throw new PermanentJobError(code);
        throw error;
      }
    },

    async failGeneration(jobId, category) {
      await sql`select private.fail_generation(${jobId}::uuid, ${category})`;
    },

    async reviewPhoto(resultId) {
      const rows = await sql<{ source: Source }[]>`
        select private.photo_source(${resultId}::uuid) as source
      `;
      const photo = rows[0]?.source ?? null;
      if (!photo) return;
      if (!storage) throw new Error("storage_unconfigured");
      const bytes = await storage.download(photo.bucket, photo.path);
      const prepared = await prepareCookedPhoto(bytes);
      if ("error" in prepared) {
        await sql`select private.mark_photo_checked(${resultId}::uuid, false, ${prepared.error})`;
        return;
      }
      await storage.upload(photo.bucket, photo.path, prepared.bytes, prepared.contentType);
      await sql`select private.mark_photo_checked(${resultId}::uuid, true, null, ${prepared.contentType})`;
    },

    async rejectPhoto(resultId) {
      await sql`select private.mark_photo_checked(${resultId}::uuid, false, 'exhausted')`;
    },

    async renderClip(clipId) {
      const rows = await sql<{ source: Source }[]>`
        select private.clip_source(${clipId}::uuid) as source
      `;
      const clip = rows[0]?.source ?? null;
      if (!clip) return;
      if (!storage) throw new Error("storage_unconfigured");
      const bytes = await storage.download(clip.bucket, clip.path);
      const video = await renderStillClip(bytes);
      const path = `${clip.ownerId}/${clipId}.mp4`;
      await storage.upload("clips", path, video, "video/mp4");
      await sql`select private.complete_clip(${clipId}::uuid, ${path})`;
    },

    async failClip(clipId) {
      await sql`select private.fail_clip(${clipId}::uuid)`;
    },
  };
}
