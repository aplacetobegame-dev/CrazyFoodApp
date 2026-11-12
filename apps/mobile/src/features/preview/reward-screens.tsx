import { useCallback, useState } from "react";
import { router, useFocusEffect } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { useVideoPlayer, VideoView } from "expo-video";
import { colors } from "@/components/food-felonies-theme";
import { usePreview, type Destination, type RecipeCase } from "./preview-data";
import { FailureCard, PreviewDecision } from "./preview-dialogs";
import { openPreview, previewRoute } from "./preview-navigation";
import { Action, Badge, Body, Chips, Heading, Note, Panel, PreviewPage, ui } from "./preview-ui";

export function SampleClipScreen() {
  const player = useVideoPlayer(require("@/assets/video/food-felonies-sample.mp4"));
  useFocusEffect(useCallback(() => () => player.pause(), [player]));
  return (
    <PreviewPage title="Sample Clip" creamHeader>
      <View style={styles.videoFrame}>
        <VideoView player={player} nativeControls contentFit="contain" style={styles.video} />
      </View>
      <Panel>
        <Badge>OFFLINE PLAYBACK TEST</Badge>
        <Heading>Food Felonies clip</Heading>
        <Body>This bundled sample demonstrates playback and framing. Your cooked photo stays in its own clip layout.</Body>
      </Panel>
    </PreviewPage>
  );
}

export function AdScreen() {
  const { rewardKeys, grantReward } = usePreview();
  const [stage, setStage] = useState<"offer" | "verifying" | "awarded" | "no-reward">("offer");
  const [reason, setReason] = useState("");
  const nextAd = rewardKeys.includes("ad-1") ? "ad-2" : "ad-1";

  function verify(verified: boolean) {
    if (verified && rewardKeys.length < 2 && !rewardKeys.includes(nextAd)) {
      grantReward(nextAd);
      setStage("awarded");
    } else {
      setReason(verified ? "The sample daily earning limit has been reached." : "This sample completion did not verify.");
      setStage("no-reward");
    }
  }

  return (
    <PreviewPage title="Rewarded Ad">
      <Panel tone="mustard"><Badge>LOCAL REWARD PREVIEW</Badge><Heading>Watch an ad for 1 generation</Heading></Panel>
      {stage === "offer" && (
        <Panel>
          <Body>Try the verification flow for a completed ad and see what happens to the local allowance.</Body>
          <Action label="Simulate completed ad" onPress={() => setStage("verifying")} />
        </Panel>
      )}
      {stage === "verifying" && (
        <Panel>
          <Heading>Verifying reward…</Heading>
          <Note>Choose a sample verification result.</Note>
          <Action label="Preview verified completion" onPress={() => verify(true)} />
          <Action label="Preview unverified completion" kind="outline" onPress={() => verify(false)} />
        </Panel>
      )}
      {(stage === "awarded" || stage === "no-reward") && (
        <Panel>
          <Heading>{stage === "awarded" ? "1 sample generation added" : "No generation added"}</Heading>
          <Body>{stage === "awarded" ? "Your local allowance now includes the sample reward." : reason}</Body>
          <Action label="Back to allowance" onPress={() => router.canGoBack() ? router.back() : router.replace(previewRoute("allowance"))} />
          <Action label="Try another outcome" kind="outline" onPress={() => setStage("offer")} />
        </Panel>
      )}
    </PreviewPage>
  );
}

const visibilityOptions = ["Public", "Private"] as const;

export function PostingScreen({ recipe, destination }: { recipe?: RecipeCase; destination: Destination }) {
  const { connectedAccounts, proofs, rewardKeys, grantReward, shareCaptions } = usePreview();
  const [stage, setStage] = useState<"ready" | "publishing" | "processing" | "published" | "failed">("ready");
  const [visibility, setVisibility] = useState<typeof visibilityOptions[number]>("Public");
  const [reward, setReward] = useState("No sample credit issued.");
  const proof = proofs.find((item) => item.caseId === recipe?.id);
  const key = `social:${recipe?.id}`;

  function finish() {
    setStage("published");
    if (visibility !== "Public") {
      setReward("No credit · The sample post is private.");
    } else if (!recipe?.published || proof?.status !== "approved" || !connectedAccounts[destination]) {
      setReward("No credit · An approved cooked result, a public case, and a sample connected account are required.");
    } else if (rewardKeys.includes(key)) {
      setReward("No credit · This recipe already earned a sample credit.");
    } else if (rewardKeys.length >= 2) {
      setReward("No credit · The sample daily earning cap has been reached.");
    } else {
      grantReward(key);
      setReward("1 sample generation added.");
    }
  }

  return (
    <PreviewPage title="Publication Status">
      <Panel>
        <Badge>LOCAL PREVIEW</Badge>
        <Heading>{destination}</Heading>
        {stage === "ready" && (
          <>
            <Body>Publication status: not submitted.</Body>
            {recipe && <Note>{recipe.title}</Note>}
            {!!recipe && !!shareCaptions[`${recipe.id}:${destination}`] && <Body>{shareCaptions[`${recipe.id}:${destination}`]}</Body>}
            <Chips choices={visibilityOptions} value={visibility} onSelect={setVisibility} />
          </>
        )}
        <PreviewDecision showTrigger={stage === "ready"} trigger={`Review sample post to ${destination}`}
          title={`Confirm sample ${destination} post?`}
          message={`Visibility: ${visibility.toLowerCase()}. This test only changes the local publication state.`}
          success="Sample post submitted" onConfirm={() => setStage("publishing")} />
        {stage === "publishing" && (
          <>
            <Body>Publication status: publishing sample.</Body>
            <Action label="Preview provider processing" onPress={() => setStage("processing")} />
          </>
        )}
        {stage === "processing" && (
          <>
            <Body>Publication status: platform processing.</Body>
            <Action label="Preview verified publication" onPress={finish} />
            <Action label="Preview posting failure" kind="outline" onPress={() => setStage("failed")} />
          </>
        )}
        {stage === "published" && <Body>Publication status: published in this preview.</Body>}
      </Panel>
      {stage === "failed" && <FailureCard title="Publication failed" detail="Your photo and caption are still available for another attempt."
        onRetry={() => setStage("ready")} />}
      <Panel>
        <Heading>Generation reward</Heading>
        <Text style={ui.body}>{reward}</Text>
        <Note>Sample rewards are capped at two per session, with one social credit per recipe across destinations.</Note>
      </Panel>
      <Action label="View account connections" kind="outline" onPress={() => openPreview("connections")} />
    </PreviewPage>
  );
}

const styles = StyleSheet.create({
  videoFrame: { width: "88%", maxWidth: 330, alignSelf: "center", aspectRatio: 9 / 16, overflow: "hidden", borderRadius: 17, backgroundColor: colors.forestDeep },
  video: { width: "100%", height: "100%" },
});
