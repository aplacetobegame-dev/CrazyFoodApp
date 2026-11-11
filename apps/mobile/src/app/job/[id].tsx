import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { Action, Body, FoodPage, Heading, Panel } from "@/features/preview/preview-ui";
import { ApiError, backend, type GenerationJob } from "@/lib/backend";

export default function JobRoute() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [job, setJob] = useState<GenerationJob | null>(null);
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (!id) return;
    let active = true;
    async function load() {
      try {
        const next = await backend.job(id);
        if (!active) return;
        setJob(next);
        if (next.status === "complete" && next.recipeId) router.replace(`/case/${next.recipeId}`);
      } catch (caught) {
        if (active) setError(caught instanceof ApiError ? caught.message : "The generation status is unavailable.");
      }
    }
    void load();
    const timer = setInterval(() => void load(), 2000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [id]);

  const failed = job?.status === "failed";
  return (
    <FoodPage title="Generating Recipe" onBack={() => router.back()}>
      <Panel>
        <Heading>{failed ? "Generation failed" : "On the case"}</Heading>
        <Body>
          {failed
            ? "This request did not finish. The reserved daily slot was returned."
            : "The sample recipe is being saved. You can leave this screen and find it in My Cases."}
        </Body>
        {!!error && <Body>{error}</Body>}
        {job?.status && <Body>Status: {job.status}</Body>}
        <Action label="Back to My Cases" kind="outline" onPress={() => router.replace("/cases")} />
      </Panel>
    </FoodPage>
  );
}
