import { DefaultTheme, ThemeProvider } from "expo-router";
import { Stack, type StackCardStyleInterpolator, type StackNavigationOptions } from "expo-router/js-stack";
import { useEffect, useState } from "react";
import { AccessibilityInfo, Easing, StyleSheet, View } from "react-native";
import { colors } from "@/components/food-felonies-theme";
import { useFoodFonts } from "@/components/food-fonts";
import { PreviewProvider } from "@/features/preview/preview-data";
import { isUiPreview } from "@/lib/app-mode";
import { AuthProvider } from "@/lib/auth";

const theme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, background: colors.canvas, card: colors.canvas },
};

const transitionSpec = {
  open: { animation: "timing", config: { duration: 210, easing: Easing.out(Easing.cubic) } },
  close: { animation: "timing", config: { duration: 170, easing: Easing.inOut(Easing.quad) } },
} satisfies StackNavigationOptions["transitionSpec"];

const gentleEntrance: StackCardStyleInterpolator = ({ current }) => ({
  cardStyle: {
    opacity: current.progress,
    transform: [{
      translateY: current.progress.interpolate({
        inputRange: [0, 1],
        outputRange: [6, 0],
        extrapolate: "clamp",
      }),
    }],
  },
});

export default function RootLayout() {
  const fontsReady = useFoodFonts();
  const [reduceMotion, setReduceMotion] = useState(true);

  useEffect(() => {
    let active = true;
    const subscription = AccessibilityInfo.addEventListener("reduceMotionChanged", setReduceMotion);
    void AccessibilityInfo.isReduceMotionEnabled().then((enabled) => {
      if (active) setReduceMotion(enabled);
    }).catch(() => {
      // Keep motion off if the device preference is unavailable.
    });

    return () => {
      active = false;
      subscription.remove();
    };
  }, []);

  if (!fontsReady) return <View style={styles.surface} />;

  const stack = (
    <Stack
      screenOptions={({ navigation, route }) => {
        const state = navigation.getState();
        return {
          headerShown: false,
          cardStyle: styles.surface,
          cardOverlayEnabled: false,
          cardShadowEnabled: false,
          // Keep just the screen immediately below the active card visible during the fade.
          detachPreviousScreen: reduceMotion || state.routes[state.index]?.key !== route.key,
          animation: reduceMotion ? "none" : "fade",
          cardStyleInterpolator: reduceMotion ? undefined : gentleEntrance,
          transitionSpec,
        };
      }}
    >
      <Stack.Protected guard={isUiPreview}>
        <Stack.Screen name="preview/[screen]" />
        <Stack.Screen name="recipe/[slug]" />
        <Stack.Screen name="staff/[item]" />
      </Stack.Protected>
      <Stack.Protected guard={!isUiPreview}>
        <Stack.Screen name="(main)" />
        <Stack.Screen name="home" />
        <Stack.Screen name="sign-in" />
      </Stack.Protected>
    </Stack>
  );

  return (
    <ThemeProvider value={theme}>
      <View style={styles.surface}>
        {isUiPreview ? <PreviewProvider>{stack}</PreviewProvider> : <AuthProvider>{stack}</AuthProvider>}
      </View>
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  surface: { flex: 1, backgroundColor: colors.canvas },
});
