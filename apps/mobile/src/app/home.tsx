import { Redirect } from "expo-router";
import { useEffect, useState } from "react";
import { ActivityIndicator, Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { supabase } from "@/lib/client";
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

      const { data, error } = await supabase
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
      <View style={styles.screen}>
        <ActivityIndicator />
      </View>
    );
  }
  if (!session) {
    return <Redirect href="/sign-in" />;
  }

  return (
    <View style={styles.screen}>
      <View style={styles.card}>
        <Text style={styles.title}>Signed in</Text>
        <Text accessibilityLabel="Account email">{session.user.email}</Text>
        <Text>{status.profile}</Text>
        <Text>{status.health}</Text>
        <Text>{status.serverSession}</Text>
        <Pressable accessibilityRole="button" onPress={() => void signOut()} style={styles.button}>
          <Text style={styles.buttonText}>Sign out</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    backgroundColor: "#f6f3ee",
  },
  card: {
    width: "100%",
    maxWidth: 420,
    gap: 12,
  },
  title: {
    fontSize: 32,
    fontWeight: "700",
  },
  button: {
    backgroundColor: "#1f1a17",
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 8,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});
