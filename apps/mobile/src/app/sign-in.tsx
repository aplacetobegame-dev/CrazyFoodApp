import { Redirect } from "expo-router";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { supabase } from "@/lib/client";
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
      <View style={styles.screen}>
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
    const { error: sendError } = await supabase.auth.signInWithOtp({
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
    const { error: verifyError } = await supabase.auth.verifyOtp({
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
    <View style={styles.screen}>
      <View style={styles.card}>
        <Text style={styles.title}>Food Felonies</Text>
        <Text style={styles.subtitle}>Sign in with an email code.</Text>
        <Text style={styles.label} nativeID="email-label">
          Email
        </Text>
        <TextInput
          accessibilityLabel="Email"
          aria-labelledby="email-label"
          autoCapitalize="none"
          autoComplete="email"
          keyboardType="email-address"
          onChangeText={setEmail}
          style={styles.input}
          value={email}
        />
        {codeSent ? (
          <>
            <Text style={styles.label} nativeID="code-label">
              Code
            </Text>
            <TextInput
              accessibilityLabel="Sign-in code"
              aria-labelledby="code-label"
              autoComplete="one-time-code"
              keyboardType="number-pad"
              onChangeText={setCode}
              style={styles.input}
              value={code}
            />
            <Pressable accessibilityRole="button" disabled={busy} onPress={() => void verifyCode()} style={styles.button}>
              <Text style={styles.buttonText}>{busy ? "Checking" : "Sign in"}</Text>
            </Pressable>
            <Text style={styles.hint}>
              Local mail is captured at http://127.0.0.1:55324. Open the message and enter the code.
            </Text>
          </>
        ) : (
          <Pressable accessibilityRole="button" disabled={busy} onPress={() => void sendCode()} style={styles.button}>
            <Text style={styles.buttonText}>{busy ? "Sending" : "Send code"}</Text>
          </Pressable>
        )}
        {error ? <Text style={styles.error}>{error}</Text> : null}
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
  subtitle: {
    fontSize: 16,
    marginBottom: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
  },
  input: {
    borderWidth: 1,
    borderColor: "#c8c2b8",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    backgroundColor: "#fff",
  },
  button: {
    backgroundColor: "#1f1a17",
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  hint: {
    fontSize: 14,
    lineHeight: 20,
  },
  error: {
    color: "#8d1d18",
    fontSize: 14,
  },
});
