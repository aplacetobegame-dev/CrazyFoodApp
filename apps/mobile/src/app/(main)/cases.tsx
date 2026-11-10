import { router } from "expo-router";
import { Action, Body, FoodPage, Heading, Panel } from "@/features/preview/preview-ui";

export default function CasesRoute() {
  return (
    <FoodPage title="My Cases" creamHeader>
      <Panel>
        <Heading>No saved cases yet</Heading>
        <Body>Your recipe drafts and published cases will appear here.</Body>
        <Action label="Create a recipe" onPress={() => router.navigate("/new-recipe")} />
      </Panel>
    </FoodPage>
  );
}
