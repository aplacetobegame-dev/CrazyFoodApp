import * as ImagePicker from "expo-image-picker";
import { CameraView, useCameraPermissions } from "expo-camera";
import { router, useLocalSearchParams } from "expo-router";
import { useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { colors } from "@/components/food-felonies-theme";
import { Action, Body, Field, FoodPage, Heading, Note, Panel, ui } from "@/features/preview/preview-ui";
import { ApiError, backend, uploadSignedPhoto } from "@/lib/backend";

export default function CookRoute() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const camera = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [uri, setUri] = useState<string>();
  const [contentType, setContentType] = useState("image/jpeg");
  const [taste, setTaste] = useState(0);
  const [verdict, setVerdict] = useState("");
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);

  async function choosePhoto() {
    setError(undefined);
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["images"], quality: 0.75 });
    const asset = result.assets?.[0];
    if (!result.canceled && asset?.uri) {
      setUri(asset.uri);
      setContentType(asset.mimeType ?? "image/jpeg");
    }
  }

  async function capture() {
    setError(undefined);
    if (!permission?.granted) {
      const next = await requestPermission();
      if (!next.granted) {
        setError("Camera permission was denied. You can choose a photo from your gallery.");
        return;
      }
    }
    const photo = await camera.current?.takePictureAsync({ quality: 0.75 });
    if (!photo?.uri) {
      setError("The camera did not return a photo. Choose one from your gallery.");
      return;
    }
    setUri(photo.uri);
    setContentType("image/jpeg");
  }

  async function submit() {
    if (!id || !uri || !taste || !verdict.trim()) {
      setError("Add a photo, pick a taste rating, and write a short verdict.");
      return;
    }
    setBusy(true);
    setError(undefined);
    try {
      const signed = await backend.signUpload();
      await uploadSignedPhoto(signed.path, signed.token, uri, contentType);
      await backend.cooked(id, { path: signed.path, taste, verdict: verdict.trim() }, crypto.randomUUID());
      router.replace(`/case/${id}`);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "The cooked proof could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <FoodPage title="Add Cooked Proof" onBack={() => router.back()}>
      <Panel>
        <Heading>Photograph the dish</Heading>
        {permission?.granted ? (
          <View style={styles.camera}>
            <CameraView ref={camera} style={StyleSheet.absoluteFill} facing="back" mode="picture" />
          </View>
        ) : (
          <Body>The camera is optional. Gallery selection works if permission is denied.</Body>
        )}
        <Action label={permission?.granted ? "Take photo" : "Enable camera"} onPress={() => void capture()} />
        <Action label="Choose from gallery" kind="outline" onPress={() => void choosePhoto()} />
        {!!uri && <Note>Photo selected.</Note>}
      </Panel>
      <Panel>
        <Heading>Taste</Heading>
        <View style={ui.wrap}>
          {[1, 2, 3, 4, 5].map((rating) => (
            <Pressable key={rating} accessibilityRole="button" accessibilityLabel={`Rate taste ${rating} out of 5`}
              onPress={() => setTaste(rating)}>
              <Text style={ui.heading}>{rating <= taste ? "★" : "☆"}</Text>
            </Pressable>
          ))}
        </View>
        <Field accessibilityLabel="Your verdict" multiline maxLength={200} value={verdict} onChangeText={setVerdict} placeholder="How did it turn out?" />
      </Panel>
      {!!error && <Text accessibilityRole="alert" style={[ui.body, ui.redText]}>{error}</Text>}
      <Action label={busy ? "Saving" : "Submit proof"} disabled={busy} onPress={() => void submit()} />
    </FoodPage>
  );
}

const styles = StyleSheet.create({
  camera: { height: 240, borderRadius: 16, overflow: "hidden", backgroundColor: colors.forestDeep },
});
