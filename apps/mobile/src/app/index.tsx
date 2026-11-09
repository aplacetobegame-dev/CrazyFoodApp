import { Redirect } from "expo-router";
import { ActivityIndicator, View } from "react-native";
import { isUiPreview } from "@/lib/app-mode";
import { previewRoute } from "@/features/preview/preview-navigation";
import { useAuth } from "@/lib/auth";

export default function Index() {
  return isUiPreview ? <Redirect href={previewRoute("discover")} /> : <ConnectedIndex />;
}

function ConnectedIndex() {
  const { ready, session } = useAuth();
  if (!ready) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }
  if (session) {
    return <Redirect href="/home" />;
  }
  return <Redirect href="/sign-in" />;
}
