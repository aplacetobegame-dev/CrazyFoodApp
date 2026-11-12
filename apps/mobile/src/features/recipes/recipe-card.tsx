import { router } from "expo-router";
import { Pressable, Text, View } from "react-native";
import { ConceptArt, Note, ui } from "@/features/preview/preview-ui";
import type { RecipeView } from "@/lib/backend";

export function RecipeCard({ recipe }: { recipe: RecipeView }) {
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={recipe.title}
      onPress={() => router.push(`/case/${recipe.id}`)}
      style={({ pressed }) => [ui.panel, pressed && ui.faded]}>
      <ConceptArt recipe={{ art: recipe.sampleImageKey, title: recipe.title }} />
      <View style={ui.flex}>
        <Text style={ui.heading}>{recipe.title}</Text>
        <Text style={ui.body}>{recipe.description}</Text>
        <View style={ui.wrap}>
          <Note>Crime {recipe.crimeLevel}/100</Note>
          <Note>{recipe.votes.guilty} Guilty</Note>
          <Note>{recipe.votes.acquitted} Acquitted</Note>
          {recipe.owned && <Note>{recipe.visibility === "public" ? "Public" : "Private draft"}</Note>}
        </View>
      </View>
    </Pressable>
  );
}
