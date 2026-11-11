import { useEffect, useState } from "react";
import { router } from "expo-router";
import { CreateRecipeScreen } from "@/features/create/create-recipe-screen";
import type { RecipeInput } from "@/features/preview/preview-data";
import { ApiError, backend } from "@/lib/backend";

function toRequest(input: RecipeInput) {
  return {
    ingredients: input.ingredients.map((item) => item.quantity ? { name: item.name, quantity: item.quantity } : { name: item.name }),
    excludedIngredients: input.exclusions,
    servings: input.servings,
    weirdness: input.weirdness,
    constraints: {
      maxMinutes: input.maxMinutes,
      equipment: input.equipment ? [input.equipment] : [],
      cuisine: input.cuisine || undefined,
      dietary: input.dietary ? [input.dietary] : [],
    },
  };
}

export default function NewRecipeRoute() {
  const [allowanceText, setAllowanceText] = useState("3 free daily");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string>();

  useEffect(() => {
    let active = true;
    void backend.allowance().then((allowance) => {
      if (active) setAllowanceText(`${allowance.freeRemaining} of ${allowance.dailyMaximum} free left today`);
    }).catch(() => {
      if (active) setAllowanceText("3 free daily");
    });
    return () => {
      active = false;
    };
  }, []);

  async function generate(input: RecipeInput) {
    if (busy) return;
    setBusy(true);
    setNotice(undefined);
    try {
      const job = await backend.generate(toRequest(input), crypto.randomUUID());
      router.push(`/job/${job.jobId}`);
    } catch (error) {
      setNotice(error instanceof ApiError ? error.message : "Recipe generation could not be started.");
    } finally {
      setBusy(false);
    }
  }

  return <CreateRecipeScreen allowanceText={allowanceText} busy={busy} notice={notice} onGenerate={(input) => void generate(input)} />;
}
