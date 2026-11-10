import { router } from "expo-router";
import { Action, Badge, Body, FoodPage, Heading, Panel } from "@/features/preview/preview-ui";

export default function DiscoverRoute() {
  return (
    <FoodPage title="Discover" creamHeader>
      <Panel tone="mustard">
        <Badge>THE CULINARY CASE FILES</Badge>
        <Heading>What’s in your kitchen?</Heading>
        <Body>Turn the ingredients you have into a recipe idea.</Body>
        <Action label="Create a recipe" onPress={() => router.navigate("/new-recipe")} />
      </Panel>
      <Panel>
        <Heading>No public recipes yet</Heading>
        <Body>Published recipes will appear here.</Body>
      </Panel>
    </FoodPage>
  );
}
