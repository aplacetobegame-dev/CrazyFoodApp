import { router, useLocalSearchParams } from "expo-router";
import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import { Text } from "react-native";
import { Action, Badge, Body, ConceptArt, FoodPage, Heading, Note, Panel, ProofArt, ui } from "@/features/preview/preview-ui";
import { ApiError, backend, type RecipeView } from "@/lib/backend";

export default function CaseRoute() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [recipe, setRecipe] = useState<RecipeView | null>(null);
  const [error, setError] = useState<string>();
  const [clipMessage, setClipMessage] = useState<string>();

  const load = useCallback(async () => {
    if (!id) return;
    const next = await backend.recipe(id);
    setRecipe(next);
  }, [id]);

  useFocusEffect(useCallback(() => {
    let active = true;
    void load().catch((caught: unknown) => {
      if (active) setError(caught instanceof ApiError ? caught.message : "That case is unavailable.");
    });
    return () => {
      active = false;
    };
  }, [load]));

  async function vote(verdict: "guilty" | "acquitted") {
    if (!id) return;
    setRecipe(await backend.vote(id, verdict));
  }

  async function publish() {
    if (!id) return;
    setRecipe(await backend.publish(id));
  }

  async function shareClip(resultId: string) {
    setClipMessage(undefined);
    try {
      const created = await backend.createClip(resultId, crypto.randomUUID());
      const ready = await waitForClip(created.clipId);
      if (!ready.downloadUrl) {
        setClipMessage("The clip is not ready yet.");
        return;
      }
      const { Share } = await import("react-native");
      await Share.share({ message: `${recipe?.title ?? "Food Felonies"} ${ready.downloadUrl}`, url: ready.downloadUrl });
    } catch (caught) {
      setClipMessage(caught instanceof Error ? caught.message : "The clip could not be created.");
    }
  }

  if (!recipe) {
    return (
      <FoodPage title="Case" onBack={() => router.back()}>
        <Panel><Heading>{error ?? "Loading case"}</Heading></Panel>
      </FoodPage>
    );
  }

  return (
    <FoodPage title={recipe.visibility === "public" ? "Recipe Case File" : "Private Case File"} onBack={() => router.back()}>
      <Panel>
        <Badge>{recipe.visibility === "public" ? "PUBLIC" : "PRIVATE DRAFT"}</Badge>
        <Text accessibilityRole="header" style={ui.title}>{recipe.title}</Text>
        <Body>{recipe.description}</Body>
        <ConceptArt recipe={{ art: recipe.sampleImageKey, title: recipe.title }} square />
        <Note>Sample concept image · Case by {recipe.author}</Note>
      </Panel>
      <Panel>
        <Heading>Crime Level {recipe.crimeLevel}/100</Heading>
        <Note>Regret Potential {recipe.regretPotential}/100 · Prep {recipe.prepMinutes ?? "—"} min · Cook {recipe.cookMinutes ?? "—"} min · Serves {recipe.servings ?? "—"}</Note>
      </Panel>
      <Panel>
        <Heading>Ingredients</Heading>
        {recipe.ingredients.map((item) => <Body key={item.name}>• {item.quantity ? `${item.quantity} ${item.name}` : item.name}</Body>)}
        <Heading>Instructions</Heading>
        {recipe.steps.map((step, index) => <Body key={step}>{index + 1}. {step}</Body>)}
      </Panel>
      <Action label="I cooked it — add proof" onPress={() => router.push(`/cook/${recipe.id}`)} />
      {recipe.owned && recipe.visibility !== "public" && <Action label="Publish case" kind="outline" onPress={() => void publish()} />}
      <Heading>Cooked Results</Heading>
      {recipe.cookedResults.length === 0 && <Panel><Heading>No cooked proof yet</Heading><Body>Made it? Add a photo of your dish and tell us how it tasted.</Body></Panel>}
      {recipe.cookedResults.map((photo) => (
        <Panel key={photo.id}>
          <Badge>{photo.status.toUpperCase()}</Badge>
          {!!photo.imageUrl && <ProofArt uri={photo.imageUrl} label="Cooked result photo" />}
          <Text style={ui.bold}>Taste {photo.taste}/5 · Crime {recipe.crimeLevel}/100</Text>
          <Body>{photo.verdict}</Body>
          {photo.mine && photo.status === "approved" && <Action label="Share clip" kind="outline" onPress={() => void shareClip(photo.id)} />}
        </Panel>
      ))}
      {!!clipMessage && <Body>{clipMessage}</Body>}
      {recipe.visibility === "public" && (
        <Panel>
          <Heading>Community Verdict</Heading>
          <Action kind={recipe.votes.mine === "guilty" ? "red" : "outline"} label={`Guilty · ${recipe.votes.guilty}`} onPress={() => void vote("guilty")} />
          <Action kind={recipe.votes.mine === "acquitted" ? "green" : "outline"} label={`Acquitted · ${recipe.votes.acquitted}`} onPress={() => void vote("acquitted")} />
          <Action label="Report case" kind="outline" onPress={() => void backend.report({ targetType: "recipe", targetId: recipe.id, reason: "Needs review" })} />
          {!recipe.owned && <Action label="Block author" kind="outline" onPress={() => void backend.block(recipe.ownerId)} />}
        </Panel>
      )}
      {!!error && <Body>{error}</Body>}
    </FoodPage>
  );
}

async function waitForClip(id: string) {
  for (let attempt = 0; attempt < 15; attempt += 1) {
    const clip = await backend.clip(id);
    if (clip.status === "ready" || clip.status === "failed") return clip;
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
  return backend.clip(id);
}
