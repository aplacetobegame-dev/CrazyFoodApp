import { Asset } from "expo-asset";
import type { GenerateMetadataFunction } from "expo-router/server";
import { sampleRecipes } from "@/features/preview/preview-data";
import { conceptSource } from "@/features/preview/preview-ui";
import { fetchPublicRecipe } from "@/lib/backend";
import { isUiPreview } from "@/lib/app-mode";

export const generateMetadata: GenerateMetadataFunction = async (request, params) => {
  const robots = "noindex, nofollow";
  if (!isUiPreview) {
    const recipe = await fetchPublicRecipe(String(params.slug ?? ""));
    if (!recipe) return { title: "Recipe unavailable · Food Felonies", robots };
    const image = Asset.fromModule(conceptSource({ art: recipe.sampleImageKey })).uri;
    return {
      title: `${recipe.title} · Food Felonies`,
      description: recipe.description,
      openGraph: {
        title: recipe.title,
        description: recipe.description,
        images: request ? new URL(image, request.url).href : image,
      },
    };
  }
  const recipe = sampleRecipes.find((item) => item.id === params.slug);

  if (!recipe) return { title: "Recipe Unavailable · Food Felonies Preview", robots };

  const image = Asset.fromModule(conceptSource(recipe)).uri;
  return {
    title: `${recipe.title} · Food Felonies Preview`,
    description: recipe.description,
    robots,
    openGraph: {
      title: recipe.title,
      description: recipe.description,
      images: request ? new URL(image, request.url).href : image,
    },
  };
};

export { PublicRecipePreview as default } from "@/features/preview/public-recipe";
