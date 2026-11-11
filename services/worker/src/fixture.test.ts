import assert from "node:assert/strict";
import test from "node:test";
import type { GenerationRequest } from "@food-felonies/contracts";
import { buildFixtureRecipe } from "./fixture.ts";

const request: GenerationRequest = {
  ingredients: [{ name: "Rice", quantity: "1 cup" }, { name: "Egg" }],
  excludedIngredients: ["peanuts"],
  servings: 2,
  weirdness: 72,
  constraints: { maxMinutes: 30, equipment: ["Stovetop"], dietary: [] },
};

test("fixture recipe keeps the request and leaves exclusions out of the steps", () => {
  const recipe = buildFixtureRecipe(request);
  assert.equal(recipe.crimeLevel, 72);
  assert.equal(recipe.sampleImageKey, "rice");
  assert.equal(recipe.servings, 2);
  assert.match(recipe.steps[0] ?? "", /Leave out peanuts/);
  assert.equal(recipe.steps.some((step) => step.toLowerCase().includes("add peanuts")), false);
});
