import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import { Action, Body, FoodPage, Heading, Panel } from "@/features/preview/preview-ui";
import { RecipeCard } from "@/features/recipes/recipe-card";
import { backend, type GenerationJob, type RecipeView } from "@/lib/backend";

export default function CasesRoute() {
  const [recipes, setRecipes] = useState<RecipeView[]>([]);
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [error, setError] = useState<string>();

  useFocusEffect(useCallback(() => {
    let active = true;
    void backend.mine().then((kitchen) => {
      if (!active) return;
      setRecipes(kitchen.recipes);
      setJobs(kitchen.jobs);
    }).catch((caught: unknown) => {
      if (active) setError(caught instanceof Error ? caught.message : "My Cases is unavailable.");
    });
    return () => {
      active = false;
    };
  }, []));

  return (
    <FoodPage title="My Cases" creamHeader>
      {!!error && <Body>{error}</Body>}
      {jobs.map((job) => (
        <Panel key={job.jobId}>
          <Heading>{job.status === "failed" ? "Generation failed" : "Generation in progress"}</Heading>
          <Body>Status: {job.status}</Body>
          <Action label="Open status" kind="outline" onPress={() => router.push(`/job/${job.jobId}`)} />
        </Panel>
      ))}
      {recipes.map((recipe) => <RecipeCard key={recipe.id} recipe={recipe} />)}
      {recipes.length === 0 && jobs.length === 0 && !error && (
        <Panel>
          <Heading>No saved cases yet</Heading>
          <Body>Your recipe drafts and published cases will appear here.</Body>
          <Action label="Create a recipe" onPress={() => router.navigate("/new-recipe")} />
        </Panel>
      )}
    </FoodPage>
  );
}
