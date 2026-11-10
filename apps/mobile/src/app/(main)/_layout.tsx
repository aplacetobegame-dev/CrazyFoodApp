import { Redirect } from "expo-router";
import { Tabs, type BottomTabBarProps } from "expo-router/js-tabs";
import { ActivityIndicator, StyleSheet, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors } from "@/components/food-felonies-theme";
import { FoodTabs, type FoodTab } from "@/components/food-tabs";
import { useAuth } from "@/lib/auth";

const tabRoutes = {
  discover: "discover",
  create: "new-recipe",
  cases: "cases",
  profile: "profile",
} satisfies Record<FoodTab, string>;

function MainTabBar({ state, emitter, navigateToTab }: BottomTabBarProps) {
  const selected = state.routes[state.index]?.name;
  const active = (Object.keys(tabRoutes) as FoodTab[]).find((tab) => tabRoutes[tab] === selected) ?? "discover";

  return (
    <SafeAreaView edges={["bottom", "left", "right"]} style={styles.footer}>
      <View style={styles.bar}>
        <FoodTabs active={active} onSelect={(tab) => {
          const route = state.routes.find((item) => item.name === tabRoutes[tab]);
          if (!route) return;
          const event = emitter.emit({ type: "tabPress", target: route.key, canPreventDefault: true });
          if (!event.defaultPrevented) navigateToTab(route.key);
        }} />
      </View>
    </SafeAreaView>
  );
}

export default function MainLayout() {
  const { ready, session } = useAuth();
  if (!ready) return <View style={styles.loading}><ActivityIndicator /></View>;
  if (!session) return <Redirect href="/sign-in" />;

  return (
    <Tabs key={session.user.id} backBehavior="firstRoute" tabBar={(props) => <MainTabBar {...props} />}
      screenOptions={{ headerShown: false, sceneStyle: styles.scene }}>
      <Tabs.Screen name="discover" />
      <Tabs.Screen name="new-recipe" />
      <Tabs.Screen name="cases" />
      <Tabs.Screen name="profile" />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  scene: { backgroundColor: colors.canvas },
  loading: { flex: 1, alignItems: "center", justifyContent: "center" },
  footer: { backgroundColor: colors.canvas, borderTopWidth: 1, borderTopColor: colors.border },
  bar: { width: "100%", maxWidth: 560, alignSelf: "center", paddingHorizontal: 12, paddingVertical: 5 },
});
