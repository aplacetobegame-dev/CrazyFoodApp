import { createContext, useContext, useRef, useState, type ReactNode } from "react";
import type { StaffEntry, StaffItem } from "./moderation-data";

export type RecipeInput = {
  ingredients: { name: string; quantity?: string }[];
  exclusions: string[];
  servings: number;
  weirdness: number;
  maxMinutes?: number;
  equipment: string;
  cuisine: string;
  dietary: string;
};

export type RecipeCase = {
  id: string;
  number: string;
  title: string;
  description: string;
  art: "rice" | "mac";
  crime: number;
  regret: number;
  prep: number;
  cook: number;
  serves: number;
  ingredients: readonly string[];
  steps: readonly string[];
  votes: readonly [number, number];
  owned: boolean;
  author: string;
  published: boolean;
  request?: RecipeInput;
};

const rice: RecipeCase = {
  id: "pickle-rice", number: "0072", title: "Pickle-Maple Crispy Rice",
  description: "Leftover rice crisped in a pan with egg, dill pickles, and a touch of maple syrup.",
  art: "rice", crime: 72, regret: 38, prep: 10, cook: 15, serves: 2,
  ingredients: ["2 cups cooked rice", "1 large egg", "¼ cup chopped dill pickles", "1 tbsp maple syrup", "1 tbsp neutral oil"],
  steps: [
    "Mix the rice, egg, and half the chopped pickles in a bowl. Press into two firm patties.",
    "Heat the oil over medium heat. Cook the patties until golden on both sides and cooked through.",
    "Finish with maple syrup, the rest of the pickles, and fresh dill if you have it.",
  ],
  votes: [18, 7], owned: false, author: "Nora Chen", published: true,
};

const macaroni: RecipeCase = {
  id: "chocolate-mac", number: "0065", title: "Mac & Cheese with Chocolate",
  description: "Creamy cheddar macaroni with a dark chocolate drizzle and a pinch of chili.",
  art: "mac", crime: 61, regret: 45, prep: 5, cook: 20, serves: 2,
  ingredients: ["150 g elbow macaroni", "1 cup milk", "1 cup grated cheddar", "20 g dark chocolate", "Pinch of chili flakes"],
  steps: [
    "Boil the macaroni according to the package directions, then drain it.",
    "Warm the milk, stir in the cheddar until smooth, and fold in the macaroni.",
    "Melt the chocolate separately. Drizzle a little over each bowl and finish with chili flakes.",
  ],
  votes: [10, 8], owned: false, author: "Eli Rivera", published: true,
};

export const sampleRecipes = [rice, macaroni];

export type Destination = "TikTok" | "Instagram";
export type ProofStatus = "pending" | "approved" | "rejected";
export type Verdict = "guilty" | "acquitted";
export type Proof = { caseId: string; uri: string; taste: number; verdict: string; status: ProofStatus };
type Photo = Pick<Proof, "caseId" | "uri">;
type ReviewDraft = Pick<Proof, "taste" | "verdict">;

type PreviewData = {
  cases: RecipeCase[];
  votes: Partial<Record<string, Verdict>>;
  proofs: Proof[];
  photo: Photo | undefined;
  reviewDrafts: Partial<Record<string, ReviewDraft>>;
  updateReviewDraft: (caseId: string, updates: Partial<ReviewDraft>) => void;
  setPhoto: (photo: Photo) => void;
  addProof: (proof: Omit<Proof, "status">) => void;
  setProofStatus: (caseId: string, status: ProofStatus) => void;
  blockedAuthors: string[];
  setAuthorBlocked: (author: string, blocked: boolean) => void;
  connectedAccounts: Partial<Record<Destination, boolean>>;
  setAccountConnected: (destination: Destination, connected: boolean) => void;
  signedIn: boolean;
  signIn: () => void;
  signOut: () => void;
  deletePreviewAccount: () => void;
  shareCaptions: Partial<Record<string, string>>;
  saveShareCaption: (key: string, caption: string) => void;
  rewardKeys: string[];
  grantReward: (key: string) => void;
  moderation: Partial<Record<StaffItem, StaffEntry[]>>;
  addModerationDecision: (id: StaffItem, entry: StaffEntry) => void;
  makeDraft: (input: RecipeInput) => string;
  publishDraft: (id: string) => void;
  vote: (id: string, verdict: Verdict) => void;
};

const PreviewContext = createContext<PreviewData | null>(null);

export function PreviewProvider({ children }: { children: ReactNode }) {
  const nextCaseNumber = useRef(73);
  const [cases, setCases] = useState(sampleRecipes);
  const [votes, setVotes] = useState<PreviewData["votes"]>({});
  const [proofs, setProofs] = useState<Proof[]>([]);
  const [photo, setPhoto] = useState<Photo>();
  const [reviewDrafts, setReviewDrafts] = useState<PreviewData["reviewDrafts"]>({});

  const [blockedAuthors, setBlockedAuthors] = useState<string[]>([]);
  const [connectedAccounts, setConnectedAccounts] = useState<PreviewData["connectedAccounts"]>({});
  const [signedIn, setSignedIn] = useState(true);
  const [shareCaptions, setShareCaptions] = useState<PreviewData["shareCaptions"]>({});
  const [rewardKeys, setRewardKeys] = useState<string[]>([]);
  const [moderation, setModeration] = useState<PreviewData["moderation"]>({});

  function deletePreviewAccount() {
    setCases(sampleRecipes);
    setVotes({});
    setProofs([]);
    setPhoto(undefined);
    setReviewDrafts({});
    setBlockedAuthors([]);
    setConnectedAccounts({});
    setShareCaptions({});
    setRewardKeys([]);
    setModeration({});
    nextCaseNumber.current = 73;
    setSignedIn(false);
  }

  function makeDraft(input: RecipeInput) {
    const number = String(nextCaseNumber.current++).padStart(4, "0");
    const id = `draft-${number}`;
    // Reveal an existing recipe fixture independently of the request the user entered.
    setCases((current) => [{
      ...rice, id, number, request: input, owned: true, author: "Maya", published: false, votes: [0, 0],
    }, ...current]);
    return id;
  }

  return (
    <PreviewContext.Provider value={{
      cases, votes, proofs, photo, setPhoto, makeDraft, reviewDrafts,
      blockedAuthors, connectedAccounts, signedIn, shareCaptions, rewardKeys, moderation,
      saveShareCaption: (key, caption) => setShareCaptions((current) => ({ ...current, [key]: caption })),
      signIn: () => setSignedIn(true),
      signOut: () => setSignedIn(false),
      deletePreviewAccount,
      setAuthorBlocked: (author, blocked) => setBlockedAuthors((current) =>
        blocked ? [...new Set([...current, author])] : current.filter((name) => name !== author)),
      setAccountConnected: (destination, connected) => setConnectedAccounts((current) => ({
        ...current, [destination]: connected,
      })),
      grantReward: (key) => setRewardKeys((current) =>
        current.length >= 2 || current.includes(key) ? current : [...current, key]),
      addModerationDecision: (id, entry) => setModeration((current) => ({
        ...current, [id]: [...(current[id] ?? []), entry],
      })),
      setProofStatus: (caseId, status) => setProofs((current) => current.map((proof) =>
        proof.caseId === caseId ? { ...proof, status } : proof)),
      updateReviewDraft: (caseId, updates) => setReviewDrafts((current) => ({
        ...current,
        [caseId]: { taste: 0, verdict: "", ...current[caseId], ...updates },
      })),
      addProof: (proof) => {
        setProofs((current) => [{ ...proof, status: "pending" }, ...current.filter((item) => item.caseId !== proof.caseId)]);
        setPhoto(undefined);
        setReviewDrafts((current) => ({ ...current, [proof.caseId]: undefined }));
      },
      publishDraft: (id) => setCases((current) => current.map((recipe) =>
        recipe.id === id && recipe.owned ? { ...recipe, published: true } : recipe)),
      vote: (id, verdict) => setVotes((current) => ({ ...current, [id]: verdict })),
    }}>
      {children}
    </PreviewContext.Provider>
  );
}

export function usePreview() {
  const value = useContext(PreviewContext);
  if (!value) throw new Error("Preview screens require PreviewProvider");
  return value;
}
