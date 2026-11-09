import { Asset } from "expo-asset";
import type { GenerateMetadataFunction } from "expo-router/server";
import { sampleRecipes } from "@/features/preview/preview-data";
import { conceptSource } from "@/features/preview/preview-ui";
import { isUiPreview } from "@/lib/app-mode";

export const generateMetadata: GenerateMetadataFunction = (request, params) => {
  const recipe = isUiPreview ? sampleRecipes.find((item) => item.id === params.slug) : undefined;
  const robots = "noindex, nofollow";

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
