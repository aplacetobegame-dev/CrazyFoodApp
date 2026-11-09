import { router } from "expo-router";
import type { FoodTab } from "@/components/food-tabs";

export function previewRoute(screen: string, caseId?: string) {
  return { pathname: "/preview/[screen]" as const, params: { screen, caseId } };
}

export function openPreview(screen: string, caseId?: string) {
  router.push(previewRoute(screen, caseId));
}

export function selectPreviewTab(tab: FoodTab) {
  if (tab === "create") {
    router.replace("/create");
  } else {
    router.replace(previewRoute(tab));
  }
}

export function backFromPreview() {
  if (router.canGoBack()) {
    router.back();
  } else {
    router.replace(previewRoute("discover"));
  }
}
