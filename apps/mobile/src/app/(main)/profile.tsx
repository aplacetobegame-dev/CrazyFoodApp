import { useEffect, useState } from "react";
import { Platform, Text } from "react-native";
import { router } from "expo-router";
import { Action, Badge, FoodPage, Heading, Note, Panel, ui } from "@/features/preview/preview-ui";
import { backend } from "@/lib/backend";
import { getSupabase } from "@/lib/client";
import { useAuth } from "@/lib/auth";
import { publicSupabaseConfig } from "@/lib/public-config";

type PlatformStatus = {
  health: string;
  profile: string;
  serverSession: string;
};

export default function ProfileRoute() {
  const { session, signOut } = useAuth();
  const [staff, setStaff] = useState(false);
  const [deleteError, setDeleteError] = useState<string>();
  const [confirmDelete, setConfirmDelete] = useState(false);
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
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 8000);
      try {
        const healthResponse = await fetch(`${url}/functions/v1/health`, {
          headers: { apikey: publishableKey },
          signal: controller.signal,
        });
        const health = healthResponse.ok ? "Edge health ok" : "Edge health unavailable";

        const { data, error } = await getSupabase()
          .from("profiles")
          .select("display_name")
          .eq("id", current.user.id)
          .abortSignal(controller.signal)
          .maybeSingle();
        const profile = error ? "Profile unavailable" : (data?.display_name || "Profile ready");

        let serverSession = "Native session";
        if (Platform.OS === "web") {
          const response = await fetch("/api/session", { signal: controller.signal });
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
      } finally {
        clearTimeout(timer);
      }
    }

    void backend.staff().then((result) => {
      if (active) setStaff(result.staff);
    }).catch(() => undefined);

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

  if (!session) return null;

  return (
    <FoodPage title="Profile" creamHeader>
      <Panel>
        <Badge tone="green">CONNECTED ACCOUNT</Badge>
        <Text accessibilityLabel="Account email" style={ui.body}>{session.user.email}</Text>
        <Action label="Sign out" kind="outline" onPress={() => void signOut()} />
        {staff && <Action label="Staff queue" kind="outline" onPress={() => router.push("/moderation")} />}
        <Action label={confirmDelete ? "Confirm delete account" : "Delete account"} kind="red" onPress={() => {
          if (!confirmDelete) {
            setConfirmDelete(true);
            return;
          }
          void backend.deleteAccount(crypto.randomUUID()).then(() => signOut()).catch((caught: unknown) => {
            setDeleteError(caught instanceof Error ? caught.message : "The account could not be deleted.");
          });
        }} />
        {!!deleteError && <Text accessibilityRole="alert" style={[ui.body, ui.redText]}>{deleteError}</Text>}
      </Panel>
      <Panel>
        <Heading>Connection status</Heading>
        <Note>{status.profile}</Note>
        <Note>{status.health}</Note>
        <Note>{status.serverSession}</Note>
      </Panel>
    </FoodPage>
  );
}
