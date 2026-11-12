import { useLocalSearchParams } from "expo-router";
import { sampleRecipes, usePreview } from "@/features/preview/preview-data";
import { CaseScreen, CasesScreen, DiscoverScreen, GenerationScreen, PublishScreen, SearchScreen } from "@/features/preview/recipe-screens";
import { CameraScreen, PhotoScreen, ProofStatusScreen, ReviewScreen } from "@/features/preview/proof-screens";
import {
  AllowanceScreen, ClipScreen, ConnectionsScreen, HelpScreen,
  PrivacyScreen, ProfileScreen, ShareScreen, WelcomeScreen,
} from "@/features/preview/account-screens";
import { AdScreen, PostingScreen, SampleClipScreen } from "@/features/preview/reward-screens";
import { BlockScreen, ReportScreen, sampleReviewer } from "@/features/preview/preview-dialogs";
import { ShareCardScreen } from "@/features/preview/public-recipe";
import { Action, Body, Heading, Panel, PreviewPage } from "@/features/preview/preview-ui";

const screens = {
  discover: DiscoverScreen,
  search: SearchScreen,
  cases: CasesScreen,
  profile: ProfileScreen,
  allowance: AllowanceScreen,
  ad: AdScreen,
  "sample-clip": SampleClipScreen,
  connections: ConnectionsScreen,
  privacy: PrivacyScreen,
  help: HelpScreen,
  welcome: WelcomeScreen,
};

const recipeScreens = {
  case: CaseScreen,
  generate: GenerationScreen,
  publish: PublishScreen,
  camera: CameraScreen,
  photo: PhotoScreen,
  review: ReviewScreen,
};

const accountScreens = new Set(["camera", "photo", "review", "proof-status", "clip", "share", "posting", "generate", "publish"]);

export default function PreviewRoute() {
  const { screen, caseId, destination, fromReview } = useLocalSearchParams<{ screen: string; caseId?: string; destination?: string; fromReview?: string }>();
  const { cases, blockedAuthors, signedIn, signIn } = usePreview();

  if (!signedIn && accountScreens.has(screen)) {
    return (
      <PreviewPage title="Preview Account">
        <Panel>
          <Heading>Return to the sample account</Heading>
          <Body>This screen contains your local account or media actions.</Body>
          <Action label="Return to preview account" onPress={signIn} />
        </Panel>
      </PreviewPage>
    );
  }

  if (Object.hasOwn(screens, screen)) {
    const Screen = screens[screen as keyof typeof screens];
    return <Screen />;
  }

  const recipe = cases.find((item) => item.id === caseId);
  const available = recipe && (signedIn || recipe.published) && !blockedAuthors.includes(recipe.author) ? recipe : undefined;
  const reportable = available?.published ? available : undefined;
  const cookedSample = reportable?.id === "pickle-rice" && !blockedAuthors.includes(sampleReviewer) ? reportable : undefined;
  const provider = destination === "Instagram" ? "Instagram" : "TikTok";
  if (screen === "share") return <ShareScreen recipe={available} />;
  if (available && screen === "posting") return <PostingScreen recipe={available} destination={provider} />;
  if (screen === "delete") return <PrivacyScreen deletion />;
  if (reportable && screen === "report") return <ReportScreen recipe={reportable} />;
  if (cookedSample && screen === "proof-report") return <ReportScreen recipe={cookedSample} cooked />;
  if (recipe?.published && !recipe.owned && screen === "block") return <BlockScreen recipe={recipe} />;
  if (reportable?.id === "pickle-rice" && screen === "block-reviewer") return <BlockScreen recipe={reportable} cooked />;
  if (reportable && screen === "share-card" && sampleRecipes.some((item) => item.id === reportable.id)) {
    return <ShareCardScreen recipe={reportable} />;
  }
  if (available && screen === "proof-status") return <ProofStatusScreen recipe={available} fromReview={fromReview === "1"} />;
  if (available && screen === "clip") return <ClipScreen recipe={available} destination={provider} />;

  const ownerScreen = screen === "generate" || screen === "publish";
  if (available && (!ownerScreen || available.owned) && Object.hasOwn(recipeScreens, screen)) {
    const Screen = recipeScreens[screen as keyof typeof recipeScreens];
    return <Screen key={available.id} recipe={available} />;
  }

  return (
    <PreviewPage title="Case Unavailable">
      <Panel><Heading>Couldn’t find that case</Heading><Body>Local cases and photos are available for the current preview session.</Body></Panel>
    </PreviewPage>
  );
}
