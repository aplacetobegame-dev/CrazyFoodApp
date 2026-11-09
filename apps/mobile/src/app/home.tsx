import { Link, Redirect } from "expo-router";
import { useEffect, useState } from "react";
import { ActivityIndicator, Platform, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { colors } from "@/components/food-felonies-theme";
import { Action, Badge, ChefMark, Heading, Note, Panel, ui } from "@/features/preview/preview-ui";
import { getSupabase } from "@/lib/client";
import { useAuth } from "@/lib/auth";
import { publicSupabaseConfig } from "@/lib/public-config";

type PlatformStatus = {
  health: string;
  profile: string;
  serverSession: string;
};

export default function HomeScreen() {
  const { ready, session, signOut } = useAuth();
  const [status, setStatus] = useState<PlatformStatus>({
    health: "Checking",
    profile: "Checking",
    serverSession: Platform.OS === "web" ? "Checking" : "Native session",
  });

  useEffect(() => {
    if (!session) {
      return;
    }
    const current = session;
    let active = true;
    const { url, publishableKey } = publicSupabaseConfig();

    async function load() {
      const healthResponse = await fetch(`${url}/functions/v1/health`, {
        headers: { apikey: publishableKey },
      });
      const health = healthResponse.ok ? "Edge health ok" : "Edge health unavailable";

      const { data, error } = await getSupabase()
        .from("profiles")
        .select("display_name")
        .eq("id", current.user.id)
        .maybeSingle();
      const profile = error ? "Profile unavailable" : (data?.display_name || "Profile ready");

      let serverSession = "Native session";
      if (Platform.OS === "web") {
        const response = await fetch("/api/session");
        if (!response.ok) {
          serverSession = "Server session unavailable";
        } else {
          const body = (await response.json()) as { email?: string | null };
          serverSession = body.email ? `Server session ${body.email}` : "Server session missing";
        }
      }

      if (active) {
        setStatus({ health, profile, serverSession });
      }
    }

    void load().catch(() => {
      if (active) {
        setStatus({
          health: "Edge health unavailable",
          profile: "Profile unavailable",
          serverSession: "Server session unavailable",
        });
      }
    });

    return () => {
      active = false;
    };
  }, [session]);

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
    <SafeAreaView style={styles.screen}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={ui.rowLine}><ChefMark /><Text style={[ui.title, ui.flex]}>Food Felonies</Text></View>
        <Panel>
          <Badge tone="green">CONNECTED ACCOUNT</Badge>
          <Heading>Profile</Heading>
          <Text accessibilityLabel="Account email" style={ui.body}>{session.user.email}</Text>
          <Link href="/create" asChild>
            <Pressable accessibilityRole="button" style={ui.action}>
              <Text style={ui.actionText}>Create a Recipe</Text>
            </Pressable>
          </Link>
          <Action label="Sign out" kind="outline" onPress={() => void signOut()} />
        </Panel>
        <Panel>
          <Heading>Connection status</Heading>
          <Note>{status.profile}</Note>
          <Note>{status.health}</Note>
          <Note>{status.serverSession}</Note>
        </Panel>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.canvas },
  loading: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.canvas },
  content: { flexGrow: 1, alignSelf: "center", width: "100%", maxWidth: 540, padding: 20, gap: 16 },
});
