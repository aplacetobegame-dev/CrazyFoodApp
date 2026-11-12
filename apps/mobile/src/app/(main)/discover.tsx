import { router } from "expo-router";
import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import { Action, Badge, Body, Field, FoodPage, Heading, Panel } from "@/features/preview/preview-ui";
import { RecipeCard } from "@/features/recipes/recipe-card";
import { backend, type RecipeView } from "@/lib/backend";

const sorts = [
  { id: "trending", label: "Trending" },
  { id: "newest", label: "Newest" },
  { id: "most_voted", label: "Most voted" },
] as const;

export default function DiscoverRoute() {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<(typeof sorts)[number]["id"]>("newest");
  const [recipes, setRecipes] = useState<RecipeView[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [error, setError] = useState<string>();

  const load = useCallback(async (nextCursor?: string | null) => {
    const page = await backend.discover(query, sort, nextCursor);
    setRecipes((current) => nextCursor ? [...current, ...page.recipes] : page.recipes);
    setCursor(page.nextCursor);
  }, [query, sort]);

  useFocusEffect(useCallback(() => {
    let active = true;
    void load(null).catch((caught: unknown) => {
      if (active) setError(caught instanceof Error ? caught.message : "Discover is unavailable.");
    });
    return () => {
      active = false;
    };
  }, [load]));

  return (
    <FoodPage title="Discover" creamHeader>
      <Panel tone="mustard">
        <Badge>THE CULINARY CASE FILES</Badge>
        <Heading>What’s in your kitchen?</Heading>
        <Body>Turn the ingredients you have into a recipe idea.</Body>
        <Action label="Create a recipe" onPress={() => router.navigate("/new-recipe")} />
      </Panel>
      <Field accessibilityLabel="Search recipes" placeholder="Search recipes or ingredients" value={query} onChangeText={setQuery} onSubmitEditing={() => void load(null)} />
      <Panel>
        {sorts.map((item) => (
          <Action key={item.id} kind={sort === item.id ? "green" : "outline"} label={item.label} onPress={() => setSort(item.id)} />
        ))}
      </Panel>
      {!!error && <Body>{error}</Body>}
      {recipes.length === 0 && !error && (
        <Panel>
          <Heading>No public recipes yet</Heading>
          <Body>Published recipes will appear here.</Body>
        </Panel>
      )}
      {recipes.map((recipe) => <RecipeCard key={recipe.id} recipe={recipe} />)}
      {!!cursor && <Action label="Load more" kind="outline" onPress={() => void load(cursor)} />}
    </FoodPage>
  );
}
