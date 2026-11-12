import { Redirect, router, useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback, useRef } from "react";
import { CreateRecipeScreen } from "@/features/create/create-recipe-screen";
import { isUiPreview } from "@/lib/app-mode";
import { usePreview } from "@/features/preview/preview-data";
import { openPreview, selectPreviewTab } from "@/features/preview/preview-navigation";

export default function CreateRoute() {
  const { preview } = useLocalSearchParams<{ preview?: string }>();
  if (isUiPreview) {
    return <PreviewCreateRoute />;
  }
  if (__DEV__ && preview === "1") {
    return <CreateRecipeScreen preview onBack={() => router.replace("/")} />;
  }
  return <Redirect href="/new-recipe" />;
}

function PreviewCreateRoute() {
  const { makeDraft } = usePreview();
  const submitted = useRef(false);

  useFocusEffect(useCallback(() => {
    submitted.current = false;
  }, []));

  return (
    <CreateRecipeScreen preview onSelectTab={selectPreviewTab}
      onPreviewGenerate={(request) => {
        if (submitted.current) return;
        submitted.current = true;
        openPreview("generate", makeDraft(request));
      }} />
  );
}
