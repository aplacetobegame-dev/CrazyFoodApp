import { Redirect } from "expo-router";
import { useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { colors } from "@/components/food-felonies-theme";
import { Action, Badge, ChefMark, Field, Heading, Note, Panel, ui } from "@/features/preview/preview-ui";
import { getSupabase } from "@/lib/client";
import { useAuth } from "@/lib/auth";

export default function SignInScreen() {
  const { ready, session } = useAuth();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (!ready) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator />
      </View>
    );
  }
  if (session) {
    return <Redirect href="/home" />;
  }

  async function sendCode() {
    setError(null);
    const trimmed = email.trim().toLowerCase();
    if (!trimmed.includes("@")) {
      setError("Enter a valid email address.");
      return;
    }
    setBusy(true);
    const { error: sendError } = await getSupabase().auth.signInWithOtp({
      email: trimmed,
      options: { shouldCreateUser: true },
    });
    setBusy(false);
    if (sendError) {
      setError(sendError.message);
      return;
    }
    setCodeSent(true);
  }

  async function verifyCode() {
    setError(null);
    setBusy(true);
    const { error: verifyError } = await getSupabase().auth.verifyOtp({
      email: email.trim().toLowerCase(),
      token: code.trim(),
      type: "email",
    });
    setBusy(false);
    if (verifyError) {
      setError(verifyError.message);
    }
  }

  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={styles.brand}>
          <ChefMark />
          <Text style={styles.title}>Food <Text style={ui.redText}>Felonies</Text></Text>
          <Badge>THE CULINARY CASE FILES</Badge>
        </View>
        <Panel>
          <Heading>{codeSent ? "Check your email" : "Sign in"}</Heading>
          <Note>{codeSent ? "Enter the one-time code from your email." : "We’ll send a one-time code to your email."}</Note>
          <Text style={ui.bold}>Email</Text>
          <Field accessibilityLabel="Email" editable={!busy} autoCapitalize="none" autoComplete="email"
            keyboardType="email-address" value={email}
            onChangeText={(value) => { setEmail(value); setCodeSent(false); setCode(""); }} />
          {codeSent && (
            <>
              <Text style={ui.bold}>Code</Text>
              <Field accessibilityLabel="Sign-in code" autoComplete="one-time-code"
                keyboardType="number-pad" value={code} onChangeText={setCode} />
            </>
          )}
          <Action disabled={busy}
            label={codeSent ? (busy ? "Checking" : "Sign in") : (busy ? "Sending" : "Send code")}
            onPress={() => void (codeSent ? verifyCode() : sendCode())} />
          {error && <Text accessibilityRole="alert" style={[ui.body, ui.redText]}>{error}</Text>}
        </Panel>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.canvas },
  loading: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.canvas },
  content: { flexGrow: 1, justifyContent: "center", alignSelf: "center", width: "100%", maxWidth: 470, padding: 20, gap: 20 },
  brand: { alignItems: "center", gap: 8, paddingVertical: 8 },
  title: { ...ui.title, fontSize: 42, lineHeight: 47, textAlign: "center" },
});
