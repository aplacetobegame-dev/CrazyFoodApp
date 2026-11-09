import { Redirect, router, useLocalSearchParams } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors } from "@/components/food-felonies-theme";
import { isUiPreview } from "@/lib/app-mode";
import { sampleRecipes, type RecipeCase } from "./preview-data";
import { previewRoute } from "./preview-navigation";
import { Action, Badge, Body, ChefMark, ConceptArt, Field, Heading, Note, Panel, PreviewPage, ui } from "./preview-ui";

export function PublicRecipePreview() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const recipe = sampleRecipes.find((item) => item.id === slug);
  if (!isUiPreview) return <Redirect href="/" />;

  return (
    <SafeAreaView style={styles.page}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={ui.rowLine}>
          <ChefMark />
          <View style={ui.flex}><Text style={ui.title}>Food Felonies</Text><Badge>PUBLIC RECIPE PREVIEW</Badge></View>
        </View>
        {recipe ? (
          <>
            <View style={styles.columns}>
              <View style={styles.column}>
                <Panel>
                  <Badge>CASE #{recipe.number}</Badge>
                  <Text accessibilityRole="header" style={ui.title}>{recipe.title}</Text>
                  <Body>{recipe.description}</Body>
                  <ConceptArt recipe={recipe} square />
                  <Note>AI-generated concept image</Note>
                </Panel>
              </View>
              <View style={styles.column}>
                <Panel>
                  <Heading>Case notes</Heading>
                  <View style={ui.wrap}>
                    <Badge tone="red">Crime {recipe.crime}/100</Badge><Badge>Regret {recipe.regret}/100</Badge>
                  </View>
                  <Body>Prep {recipe.prep} min · Cook {recipe.cook} min · Serves {recipe.serves}</Body>
                  <Heading>Ingredients</Heading>
                  {recipe.ingredients.map((ingredient) => <Body key={ingredient}>• {ingredient}</Body>)}
                  <Heading>Instructions</Heading>
                  {recipe.steps.map((step, index) => <Body key={step}>{index + 1}. {step}</Body>)}
                </Panel>
              </View>
            </View>
            <Panel>
              <Heading>Cooked Results</Heading>
              <Body>Open the app case to try voting or add a local photo of what you cooked.</Body>
              <Action label="Open app case" onPress={() => router.push(previewRoute("case", recipe.id))} />
            </Panel>
            <Note>Bundled public sample · Available anonymously in test mode</Note>
          </>
        ) : (
          <Panel>
            <Heading>Recipe unavailable</Heading>
            <Body>This preview link may be invalid or the sample may be unavailable.</Body>
            <Action label="Explore recipes" onPress={() => router.replace(previewRoute("discover"))} />
          </Panel>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

export function ShareCardScreen({ recipe }: { recipe: RecipeCase }) {
  const path = `/recipe/${recipe.id}`;
  return (
    <PreviewPage title="Share Link Preview" creamHeader>
      <Panel>
        <Badge>LINK CARD EXAMPLE</Badge>
        <ConceptArt recipe={recipe} />
        <Heading>{recipe.title}</Heading>
        <Body>{recipe.description}</Body>
        <Note>Food Felonies · AI recipe concept</Note>
      </Panel>
      <Panel>
        <Heading>Local recipe path</Heading>
        <Field accessibilityLabel="Local recipe path" readOnly value={path} />
        <Action label="Open public recipe" onPress={() => router.push({ pathname: "/recipe/[slug]", params: { slug: recipe.id } })} />
        <Note>On Expo Go, add this path after /-- in your development URL to test a direct launch.</Note>
      </Panel>
    </PreviewPage>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: colors.canvas },
  content: { width: "100%", maxWidth: 1100, alignSelf: "center", padding: 18, paddingBottom: 28, gap: 15 },
  columns: { flexDirection: "row", flexWrap: "wrap", gap: 15, alignItems: "flex-start" },
  column: { flexGrow: 1, flexBasis: 300, minWidth: 0 },
});
