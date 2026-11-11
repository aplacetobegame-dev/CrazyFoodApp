import type { GenerationRequest, RecipeDocument } from "@food-felonies/contracts";

export function buildFixtureRecipe(request: GenerationRequest): RecipeDocument {
  const lead = request.ingredients[0]?.name ?? "Kitchen";
  const names = request.ingredients.map((item) => item.quantity ? `${item.quantity} ${item.name}` : item.name);
  const minutes = request.constraints.maxMinutes ?? 20;
  const title = (request.weirdness >= 70 ? `${lead} Felony` : request.weirdness >= 40 ? `Suspicious ${lead}` : `${lead} Case`).slice(0, 120);
  const avoid = request.excludedIngredients.length > 0
    ? `Leave out ${request.excludedIngredients.join(", ")}.`
    : "Use the ingredients you listed.";
  return {
    title,
    description: `Sample recipe using ${names.join(", ")}. Weirdness ${request.weirdness}/100. Fixture content, not a model response.`.slice(0, 500),
    servings: request.servings,
    ingredients: request.ingredients,
    steps: [
      `Gather ${names.join(", ")}. ${avoid}`,
      `Cook over medium heat for about ${minutes} minutes, until the dish is hot through.`,
      `Serve ${request.servings}.`,
    ],
    prepMinutes: 10,
    cookMinutes: minutes,
    crimeLevel: request.weirdness,
    regretPotential: Math.round(request.weirdness * 0.55),
    sampleImageKey: request.weirdness >= 50 ? "rice" : "mac",
    exclusionsHonored: request.excludedIngredients,
  };
}
