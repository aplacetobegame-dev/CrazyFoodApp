import { Redirect, router, useLocalSearchParams } from "expo-router";
import type { GenerateMetadataFunction } from "expo-router/server";
import { useState } from "react";
import { Text, View } from "react-native";
import { isUiPreview } from "@/lib/app-mode";
import { moderationSamples, type StaffDecision } from "@/features/preview/moderation-data";
import { sampleRecipes, usePreview } from "@/features/preview/preview-data";
import { PreviewDecision } from "@/features/preview/preview-dialogs";
import { Badge, Body, Chips, ConceptArt, Field, Heading, Note, Panel, PreviewPage, Row, ui } from "@/features/preview/preview-ui";

const filters = ["All", "Pending", "Reviewed"] as const;
const decisions = ["Approve", "Reject", "Takedown"] as const;

export const generateMetadata: GenerateMetadataFunction = () => ({ robots: "noindex, nofollow" });

export default function StaffPreviewRoute() {
  return isUiPreview ? <StaffPreviewContent /> : <Redirect href="/" />;
}

function StaffPreviewContent() {
  const { item } = useLocalSearchParams<{ item: string }>();
  const { moderation } = usePreview();
  const [filter, setFilter] = useState<typeof filters[number]>("All");
  const entry = moderationSamples.find((sample) => sample.id === item);
  const queue = moderationSamples.filter((sample) => filter === "All"
    || (filter === "Reviewed" ? !!moderation[sample.id]?.length : !moderation[sample.id]?.length));

  return (
    <PreviewPage title={entry ? "Review Item" : "Moderation Queue"}>
      <Panel tone="mustard"><Badge>STAFF WORKSPACE · LOCAL SAMPLES</Badge><Note>Staff actions affect this preview queue.</Note></Panel>
      {entry ? <StaffReview key={entry.id} entry={entry} /> : (
        <>
          <Chips choices={filters} value={filter} onSelect={setFilter} />
          <Panel>
            {queue.length === 0 && <Body>No matching items.</Body>}
            {queue.map((sample) => (
              <Row key={sample.id} icon="folder" title={sample.title}
                detail={`${sample.type} · ${moderation[sample.id]?.at(-1)?.decision ?? "Pending"}`}
                onPress={() => router.push({ pathname: "/staff/[item]", params: { item: sample.id } })} />
            ))}
          </Panel>
        </>
      )}
    </PreviewPage>
  );
}

function StaffReview({ entry }: { entry: typeof moderationSamples[number] }) {
  const { moderation, addModerationDecision } = usePreview();
  const [decision, setDecision] = useState<StaffDecision>("Approve");
  const [note, setNote] = useState("");
  const history = moderation[entry.id] ?? [];

  return (
    <>
      <Panel>
        <View style={ui.wrap}><Badge>{entry.type}</Badge><Badge tone="green">{history.at(-1)?.decision ?? "Pending"}</Badge></View>
        <Heading>{entry.title}</Heading>
        <Body>{entry.detail}</Body>
        {entry.id === "recipe" && <ConceptArt recipe={sampleRecipes[0]} />}
      </Panel>
      <Panel>
        <Heading>Decision</Heading>
        <Chips choices={decisions} value={decision} onSelect={setDecision} />
        <Field accessibilityLabel="Moderation note" placeholder="Add a note for the sample history" value={note} onChangeText={setNote} multiline />
        <PreviewDecision trigger={`Review ${decision.toLowerCase()} decision`} title={`Confirm ${decision.toLowerCase()}?`}
          message={`Record this decision in the local history for “${entry.title}”.`}
          success="Sample decision recorded" destructive={decision !== "Approve"}
          onConfirm={() => { addModerationDecision(entry.id, { decision, note: note.trim() }); setNote(""); }} />
      </Panel>
      <Panel>
        <Heading>Decision history</Heading>
        {history.length === 0 && <Note>No decisions yet.</Note>}
        {history.map((item, index) => (
          <View key={index} style={ui.rowLine}>
            <Badge tone={item.decision === "Approve" ? "green" : "red"}>{item.decision}</Badge>
            <Text style={[ui.note, ui.flex]}>{item.note || "Sample decision recorded."}</Text>
          </View>
        ))}
      </Panel>
    </>
  );
}
