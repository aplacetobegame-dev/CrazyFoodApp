import * as ImagePicker from "expo-image-picker";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useCallback, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { router, useFocusEffect, useIsFocused } from "expo-router";
import { colors } from "@/components/food-felonies-theme";
import { Icon } from "@/features/create/create-art";
import { usePreview, type ProofStatus, type RecipeCase } from "./preview-data";
import { previewRoute } from "./preview-navigation";
import { Action, Badge, Body, Chips, Field, Heading, Note, Panel, PreviewPage, ProofArt, ui } from "./preview-ui";

export function CameraScreen({ recipe }: { recipe: RecipeCase }) {
  const { setPhoto } = usePreview();
  const camera = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const focused = useIsFocused();
  const [ready, setReady] = useState(false);
  const [cameraError, setCameraError] = useState(false);
  const [busy, setBusy] = useState(false);
  const [picking, setPicking] = useState(false);
  const [notice, setNotice] = useState("");

  useFocusEffect(useCallback(() => () => setReady(false), []));

  function reviewPhoto(uri: string) {
    setPhoto({ caseId: recipe.id, uri });
    router.replace(previewRoute("photo", recipe.id));
  }

  async function enableCamera() {
    setCameraError(false);
    setNotice("");
    try {
      const result = await requestPermission();
      if (!result.granted) setNotice("Camera permission was denied. You can choose a photo from your gallery.");
    } catch {
      setNotice("Camera permission is unavailable. You can choose a photo from your gallery.");
    }
  }

  async function capture() {
    if (!ready || !camera.current || busy) return;
    setBusy(true);
    setNotice("");
    try {
      const photo = await camera.current.takePictureAsync({ quality: 0.75 });
      if (photo?.uri) reviewPhoto(photo.uri);
      else setNotice("The camera did not return a photo. Try again or choose one from your gallery.");
    } catch {
      setNotice("Couldn’t take that photo. Try again or choose one from your gallery.");
    } finally {
      setBusy(false);
    }
  }

  async function choosePhoto() {
    setPicking(true);
    setReady(false);
    setNotice("");
    try {
      const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["images"], quality: 0.75 });
      if (!result.canceled && result.assets[0]?.uri) reviewPhoto(result.assets[0].uri);
    } catch {
      setNotice("Couldn’t open the gallery. Check your device permissions and try again.");
    } finally {
      setPicking(false);
    }
  }

  const showCamera = !!permission?.granted && focused && !cameraError && !picking;
  return (
    <PreviewPage title="Add Cooked Proof">
      <View style={styles.camera}>
        {showCamera ? (
          <CameraView ref={camera} style={StyleSheet.absoluteFill} facing="back" mode="picture"
            onCameraReady={() => setReady(true)} onMountError={() => {
              setCameraError(true);
              setReady(false);
              setNotice("The camera couldn’t start. Try again or choose a photo from your gallery.");
            }} />
        ) : (
          <Icon name="camera" color={colors.cream} size={36} />
        )}
        <View pointerEvents="none" style={styles.focusFrame} />
      </View>
      {showCamera ? (
        <View style={styles.captureControls}>
          <Pressable accessibilityRole="button" accessibilityLabel="Take photo"
            accessibilityState={{ disabled: !ready || busy }} disabled={!ready || busy}
            onPress={() => void capture()} style={[styles.shutter, (!ready || busy) && ui.faded]} />
          <Text style={ui.note}>{ready ? "Take a photo" : "Starting camera…"}</Text>
        </View>
      ) : (
        <Action label={cameraError ? "Retry camera" : "Enable camera"} disabled={picking || permission?.canAskAgain === false}
          onPress={() => void enableCamera()} />
      )}
      <Action label="Choose from gallery" kind="outline" disabled={busy || picking} onPress={() => void choosePhoto()} />
      {permission?.canAskAgain === false && !permission.granted && <Note>Enable camera access in device settings or choose a photo from your gallery.</Note>}
      {!!notice && <Text accessibilityRole="alert" style={[ui.body, ui.redText]}>{notice}</Text>}
      <Note>Use a photo of the dish you cooked. Photos stay in this preview session.</Note>
    </PreviewPage>
  );
}

export function PhotoScreen({ recipe }: { recipe: RecipeCase }) {
  const { photo } = usePreview();
  const uri = photo?.caseId === recipe.id ? photo.uri : undefined;

  return (
    <PreviewPage title="Review Photo">
      {uri ? (
        <>
          <ProofArt uri={uri} label="Photo selected for your cooked proof" />
          <Action label="Use photo" onPress={() => router.replace(previewRoute("review", recipe.id))} />
          <Action label="Retake or replace" kind="outline" onPress={() => router.replace(previewRoute("camera", recipe.id))} />
        </>
      ) : (
        <Panel>
          <Heading>Choose a photo first</Heading>
          <Action label="Open photo options" onPress={() => router.replace(previewRoute("camera", recipe.id))} />
        </Panel>
      )}
    </PreviewPage>
  );
}

export function ReviewScreen({ recipe }: { recipe: RecipeCase }) {
  const { photo, addProof, reviewDrafts, updateReviewDraft } = usePreview();
  const { taste, verdict } = reviewDrafts[recipe.id] ?? { taste: 0, verdict: "" };
  const [error, setError] = useState("");
  const uri = photo?.caseId === recipe.id ? photo.uri : undefined;

  function submit() {
    if (!uri || !taste || !verdict.trim()) {
      setError("Add a photo, pick a taste rating, and write a short verdict.");
      return;
    }
    addProof({ caseId: recipe.id, uri, taste, verdict: verdict.trim() });
    router.replace({
      pathname: "/preview/[screen]",
      params: { screen: "proof-status", caseId: recipe.id, fromReview: "1" },
    });
  }

  return (
    <PreviewPage title="Add Cooked Review" creamHeader>
      <Panel>
        <Badge>CASE #{recipe.number}</Badge>
        <Heading>{recipe.title}</Heading>
        {uri && <ProofArt uri={uri} label="Your cooked-result photo" />}
        <Action kind="outline" label={uri ? "Replace photo" : "Choose photo"}
          onPress={() => router.replace(previewRoute("camera", recipe.id))} />
      </Panel>
      <Panel>
        <Heading>Your Rating</Heading>
        <View style={ui.wrap}>
          {[1, 2, 3, 4, 5].map((rating) => (
            <Pressable key={rating} accessibilityRole="button"
              accessibilityLabel={`Rate taste ${rating} out of 5`}
              accessibilityState={{ selected: rating === taste }} style={styles.starButton}
              onPress={() => { updateReviewDraft(recipe.id, { taste: rating }); setError(""); }}>
              <Text aria-hidden style={[styles.star, rating <= taste && styles.starFilled]}>{rating <= taste ? "★" : "☆"}</Text>
            </Pressable>
          ))}
        </View>
        <Text style={ui.bold}>{taste ? `Taste: ${taste}/5` : "Choose a taste rating"}</Text>
      </Panel>
      <Panel>
        <Heading>Your Verdict</Heading>
        <Field accessibilityLabel="Your verdict" multiline placeholder="How did it turn out?"
          maxLength={200} value={verdict} onChangeText={(value) => { updateReviewDraft(recipe.id, { verdict: value }); setError(""); }} />
        <Note>{verdict.length}/200</Note>
      </Panel>
      {!!error && <Text accessibilityRole="alert" style={[ui.body, ui.redText]}>{error}</Text>}
      <Action label="Save local proof" onPress={submit} />
    </PreviewPage>
  );
}

const proofOptions = ["Pending", "Approved", "Rejected"] as const;

export function ProofStatusScreen({ recipe, fromReview }: { recipe: RecipeCase; fromReview: boolean }) {
  const { proofs, setProofStatus, updateReviewDraft } = usePreview();
  const proof = proofs.find((item) => item.caseId === recipe.id);
  const label = proof?.status === "approved" ? "Approved" : proof?.status === "rejected" ? "Rejected" : "Pending";
  const visible = proof?.status === "approved" && recipe.published;

  return (
    <PreviewPage title="Cooked Proof Status">
      {proof ? (
        <>
          <Panel>
            <Badge tone={label === "Approved" ? "green" : label === "Rejected" ? "red" : "mustard"}>{label.toUpperCase()} · SAMPLE</Badge>
            <Heading>{recipe.title}</Heading>
            <ProofArt uri={proof.uri} label="Your cooked photo in the local preview" />
            <Text style={ui.bold}>Taste {proof.taste}/5 · Crime {recipe.crime}/100</Text>
            <Body>{proof.verdict}</Body>
            <Note>{visible ? "Visibility: shown in this local case file." : "Visibility: private to your preview account."}</Note>
            {label === "Rejected" && (
              <>
                <Body>Sample reason: the dish is hard to identify in this photo.</Body>
                <Action label="Replace photo and resubmit" onPress={() => {
                  updateReviewDraft(recipe.id, { taste: proof.taste, verdict: proof.verdict });
                  router.replace(previewRoute("camera", recipe.id));
                }} />
              </>
            )}
          </Panel>
          <Panel>
            <Heading>Preview a moderation outcome</Heading>
            <Chips choices={proofOptions} value={label} onSelect={(value) => setProofStatus(recipe.id, value.toLowerCase() as ProofStatus)} />
            <Note>These controls change the state in this session.</Note>
          </Panel>
          <Action label="Try the clip layout" kind="outline" onPress={() => router.push(previewRoute("share", recipe.id))} />
          <Action label="Back to case" onPress={() => {
            if (fromReview && router.canGoBack()) {
              router.back();
            } else {
              router.replace(previewRoute("case", recipe.id));
            }
          }} />
        </>
      ) : (
        <Panel><Heading>No photo saved</Heading><Body>Add a cooked photo and review to see its status here.</Body></Panel>
      )}
    </PreviewPage>
  );
}

const styles = StyleSheet.create({
  camera: { borderRadius: 17, overflow: "hidden", backgroundColor: "#171914", aspectRatio: 1, alignItems: "center", justifyContent: "center" },
  focusFrame: { position: "absolute", inset: 24, borderRadius: 16, borderWidth: 1, borderColor: "#B9BBAE" },
  captureControls: { alignItems: "center", gap: 5 },
  shutter: { width: 64, height: 64, borderRadius: 32, borderWidth: 6, borderColor: "#B9BBAE", backgroundColor: colors.cream, marginTop: 10 },
  starButton: { minWidth: 44, minHeight: 48, alignItems: "center", justifyContent: "center" },
  star: { fontSize: 34, color: "#8D6B2D" },
  starFilled: { color: "#A55D0B" },
});
