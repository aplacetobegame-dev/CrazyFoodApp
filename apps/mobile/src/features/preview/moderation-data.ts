export type StaffDecision = "Approve" | "Reject" | "Takedown";

export const moderationSamples = [
  { id: "recipe", title: "Pickle-Maple Crispy Rice", type: "Recipe", detail: "Review the recipe text and AI concept label before public visibility." },
  { id: "proof", title: "Cooked result from Sam", type: "Cooked proof", detail: "Sample photo metadata and review text. The original photo is withheld in this fixture." },
  { id: "report", title: "Report on a cooked review", type: "Report", detail: "Reason: Unsafe content. Review the reported verdict and record a decision." },
] as const;

export type StaffItem = typeof moderationSamples[number]["id"];
export type StaffEntry = { decision: StaffDecision; note: string };
