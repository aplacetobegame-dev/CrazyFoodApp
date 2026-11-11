import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import { Action, Body, FoodPage, Heading, Panel } from "@/features/preview/preview-ui";
import { backend } from "@/lib/backend";

type Queue = Awaited<ReturnType<typeof backend.queue>>;

export default function ModerationRoute() {
  const [queue, setQueue] = useState<Queue>({ cooked: [], reports: [] });
  const [error, setError] = useState<string>();

  const load = useCallback(async () => {
    setQueue(await backend.queue());
  }, []);

  useFocusEffect(useCallback(() => {
    let active = true;
    void load().catch((caught: unknown) => {
      if (active) setError(caught instanceof Error ? caught.message : "The queue is unavailable.");
    });
    return () => {
      active = false;
    };
  }, [load]));

  async function decide(id: string, decision: "approve" | "reject" | "takedown") {
    await backend.decide(id, decision, "");
    await load();
  }

  return (
    <FoodPage title="Moderation" onBack={() => router.back()}>
      {!!error && <Body>{error}</Body>}
      <Heading>Cooked photos</Heading>
      {queue.cooked.length === 0 && <Panel><Body>No photos are waiting.</Body></Panel>}
      {queue.cooked.map((item) => (
        <Panel key={item.id}>
          <Heading>{item.title}</Heading>
          <Body>Taste {item.taste}/5 · {item.verdict}</Body>
          <Body>{item.photoReady ? "Photo checked" : "Still checking the file"}</Body>
          {!!item.note && <Body>{item.note}</Body>}
          <Action label="Approve" disabled={!item.photoReady} onPress={() => void decide(item.id, "approve")} />
          <Action label="Reject" kind="outline" onPress={() => void decide(item.id, "reject")} />
          <Action label="Takedown" kind="red" onPress={() => void decide(item.id, "takedown")} />
        </Panel>
      ))}
      <Heading>Reports</Heading>
      {queue.reports.length === 0 && <Panel><Body>No open reports.</Body></Panel>}
      {queue.reports.map((report) => (
        <Panel key={report.id}>
          <Heading>{report.targetType}</Heading>
          <Body>{report.reason}</Body>
        </Panel>
      ))}
    </FoodPage>
  );
}
