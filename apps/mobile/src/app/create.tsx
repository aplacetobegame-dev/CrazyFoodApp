import { Redirect, router, useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback, useRef } from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";
import { CreateRecipeScreen } from "@/features/create/create-recipe-screen";
import { isUiPreview } from "@/lib/app-mode";
import { usePreview } from "@/features/preview/preview-data";
import { openPreview, selectPreviewTab } from "@/features/preview/preview-navigation";
import { useAuth } from "@/lib/auth";

export default function CreateRoute() {
  const { preview } = useLocalSearchParams<{ preview?: string }>();
  if (isUiPreview) {
    return <PreviewCreateRoute />;
  }
  if (__DEV__ && preview === "1") {
    return <CreateRecipeScreen preview onBack={() => router.replace("/")} />;
  }
  return <ConnectedCreateRoute />;
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

function ConnectedCreateRoute() {
  const { ready, session } = useAuth();
  if (!ready) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator />
      </View>
    );
  }
  if (!session) {
    return <Redirect href="/sign-in" />;
  }

  return (
    <CreateRecipeScreen
      key={session.user.id}
      onBack={() => {
        if (router.canGoBack()) {
          router.back();
        } else {
          router.replace("/home");
        }
      }}
    />
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: "center", alignItems: "center" },
});
