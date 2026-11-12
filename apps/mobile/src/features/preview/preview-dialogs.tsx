import { useState } from "react";
import { Modal, StyleSheet, Text, View } from "react-native";
import { colors } from "@/components/food-felonies-theme";
import type { RecipeCase } from "./preview-data";
import { usePreview } from "./preview-data";
import { openPreview } from "./preview-navigation";
import { Action, Badge, Body, Chips, Heading, Note, Panel, PreviewPage, ui } from "./preview-ui";

type Stage = "confirm" | "failed" | "done";

export function PreviewDecision({
  trigger, title, message, success, onConfirm, destructive = false, showTrigger = true,
}: {
  trigger: string;
  title: string;
  message: string;
  success: string;
  onConfirm: () => void;
  destructive?: boolean;
  showTrigger?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [stage, setStage] = useState<Stage>("confirm");
  const [outcome, setOutcome] = useState("");
  const dismiss = () => {
    setOpen(false);
  };
  const show = () => {
    setOutcome(success);
    setStage("confirm");
    setOpen(true);
  };
  const confirm = () => {
    setStage("done");
    onConfirm();
  };

  return (
    <>
      {showTrigger && <Action kind={destructive ? "outline" : "green"} label={trigger} onPress={show} />}
      <Modal visible={open} transparent animationType="fade" onRequestClose={dismiss}>
        <View style={styles.scrim} aria-hidden={!open} pointerEvents={open ? "auto" : "none"}>
          <View accessibilityViewIsModal style={styles.dialog}>
            <Badge>LOCAL PREVIEW</Badge>
            {stage === "done" ? (
              <>
                <Heading>{outcome}</Heading>
                <Note>This outcome applies to this preview session.</Note>
                <Action label="Done" onPress={dismiss} />
              </>
            ) : stage === "failed" ? (
              <>
                <Heading>Couldn’t complete this action</Heading>
                <Body>This sample failure leaves your previous state in place.</Body>
                <Action label="Try again" onPress={() => setStage("confirm")} />
                <Action kind="outline" label="Cancel" onPress={dismiss} />
              </>
            ) : (
              <>
                <Heading>{title}</Heading>
                <Body>{message}</Body>
                <Action kind={destructive ? "red" : "green"} label="Confirm" onPress={confirm} />
                <Action kind="outline" label="Cancel" onPress={dismiss} />
                <Action kind="outline" label="Preview a failure" onPress={() => setStage("failed")} />
              </>
            )}
          </View>
        </View>
      </Modal>
    </>
  );
}

const reportReasons = ["Spam", "Unsafe content", "Other"] as const;
export const sampleReviewer = "Sam Rivera";

export function ReportScreen({ recipe, cooked = false }: { recipe: RecipeCase; cooked?: boolean }) {
  const [reason, setReason] = useState<typeof reportReasons[number]>("Spam");
  const [submitted, setSubmitted] = useState(false);

  return (
    <PreviewPage title={cooked ? "Report Cooked Result" : "Report Case"} creamHeader>
      <Panel>
        <Badge>{cooked ? "COOKED REVIEW" : "RECIPE CASE"}</Badge>
        <Heading>{cooked ? `Cooked by ${sampleReviewer}` : recipe.title}</Heading>
        {cooked && <Note>Sample review for {recipe.title}</Note>}
        <Body>Choose the reason that best describes the concern.</Body>
        <Chips choices={reportReasons} value={reason} onSelect={(value) => { setReason(value); setSubmitted(false); }} />
        <PreviewDecision trigger="Submit sample report" title="Submit this report?"
          message={`Reason selected: ${reason}. This report stays in the local preview.`}
          success="Sample report recorded" onConfirm={() => setSubmitted(true)} />
        {submitted && <Text accessibilityLiveRegion="polite" style={ui.note}>Recorded reason: {reason}</Text>}
      </Panel>
      {(cooked || !recipe.owned) && (
        <Action kind="outline" label={cooked ? "Block reviewer" : "Block recipe author"}
          onPress={() => openPreview(cooked ? "block-reviewer" : "block", recipe.id)} />
      )}
    </PreviewPage>
  );
}

export function BlockScreen({ recipe, cooked = false }: { recipe: RecipeCase; cooked?: boolean }) {
  const author = cooked ? sampleReviewer : recipe.author;
  const { blockedAuthors, setAuthorBlocked } = usePreview();
  const blocked = blockedAuthors.includes(author);

  return (
    <PreviewPage title="Block User" creamHeader>
      <Panel>
        <Heading>{author}</Heading>
        <Body>Blocking hides this person’s recipes and reviews from your preview.</Body>
        {blocked && <Badge tone="red">BLOCKED IN PREVIEW</Badge>}
        <PreviewDecision trigger={blocked ? "Unblock user" : "Block user"}
          title={blocked ? `Unblock ${author}?` : `Block ${author}?`}
          message={blocked ? "Their sample content will appear again." : "Their sample content will be hidden. You can undo this in Account & Privacy."}
          success={blocked ? "User unblocked" : "User blocked"}
          destructive={!blocked} onConfirm={() => setAuthorBlocked(author, !blocked)} />
      </Panel>
    </PreviewPage>
  );
}

export function FailureCard({ title, detail, onRetry }: { title: string; detail: string; onRetry: () => void }) {
  return (
    <Panel tone="blush">
      <Badge tone="red">SAMPLE FAILURE</Badge>
      <Heading>{title}</Heading>
      <Body>{detail}</Body>
      <Action label="Try again" onPress={onRetry} />
    </Panel>
  );
}

const styles = StyleSheet.create({
  scrim: {
    flex: 1, justifyContent: "center", alignItems: "center", padding: 20,
    backgroundColor: "rgba(27, 23, 19, 0.47)",
  },
  dialog: {
    width: "100%", maxWidth: 410, gap: 11, padding: 18, borderRadius: 20,
    backgroundColor: colors.paper, borderWidth: 1, borderColor: colors.border,
  },
});
