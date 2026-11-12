import { useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { colors } from "@/components/food-felonies-theme";
import { Icon } from "@/features/create/create-art";
import { usePreview, type Destination, type RecipeCase } from "./preview-data";
import { openPreview, previewRoute } from "./preview-navigation";
import { PreviewDecision } from "./preview-dialogs";
import { Action, Badge, Body, ChefMark, Chips, Field, Heading, Note, Panel, PreviewPage, ProofArt, Row, ui } from "./preview-ui";

export function WelcomeScreen() {
  const { signIn } = usePreview();
  return (
    <PreviewPage title="Welcome" creamHeader>
      <View style={styles.welcome}>
        <ChefMark />
        <Text style={styles.brand}>Food <Text style={ui.redText}>Felonies</Text></Text>
        <Badge>THE CULINARY CASE FILES</Badge>
        <Text style={styles.tagline}>Make it. Cook it. Show the evidence.</Text>
      </View>
      <Panel>
        <Heading>Welcome to the scene</Heading>
        <Body>Turn the food you already have into a recipe worth investigating.</Body>
        <Action label="Explore the preview" onPress={() => { signIn(); router.replace(previewRoute("discover")); }} />
        <Note>Local preview · No account required</Note>
      </Panel>
    </PreviewPage>
  );
}

export function ProfileScreen() {
  const { cases, proofs, signedIn, signOut } = usePreview();
  return (
    <PreviewPage title="Profile" activeTab="profile">
      <Panel>
        <View style={ui.rowLine}>
          <View style={styles.avatar}><Icon name="person" color={colors.forestDeep} size={32} /></View>
          <View style={ui.flex}><Heading>{signedIn ? "Maya" : "Guest"}</Heading><Badge tone="green">{signedIn ? "PREVIEW ACCOUNT" : "SIGNED OUT IN PREVIEW"}</Badge></View>
        </View>
        <View style={ui.rowLine}>
          <View style={ui.flex}><Text style={styles.number}>{cases.filter((recipe) => recipe.owned).length}</Text><Note>My recipes</Note></View>
          <View style={ui.flex}><Text style={styles.number}>{proofs.length}</Text><Note>Cooked results</Note></View>
        </View>
      </Panel>
      <Panel>
        <Row title="Daily Allowance" detail="Free and earned generations" icon="spark" onPress={() => openPreview("allowance")} />
        <Row title="Connected Accounts" detail="TikTok and Instagram" icon="people" onPress={() => openPreview("connections")} />
        <Row title="Account & Privacy" icon="lock" onPress={() => openPreview("privacy")} />
        <Row title="Help & Feedback" icon="options" onPress={() => openPreview("help")} />
        <Row title="Staff moderation preview" detail="Open the sample queue" icon="folder"
          onPress={() => router.push({ pathname: "/staff/[item]", params: { item: "queue" } })} />
        <Row title="Sample clip playback" icon="camera" onPress={() => openPreview("sample-clip")} />
        <Row title="Welcome screen" detail="Explore the entry design" icon="compass" onPress={() => openPreview("welcome")} />
        <PreviewDecision showTrigger={signedIn} trigger="Sign out" title="Sign out of this preview account?"
          message="This switches Profile to the guest state. Your preview drafts stay in this session."
          success="Signed out in preview" onConfirm={signOut} />
      </Panel>
    </PreviewPage>
  );
}

export function AllowanceScreen() {
  const { rewardKeys } = usePreview();
  return (
    <PreviewPage title="Daily Allowance" creamHeader>
      <Panel tone="mustard">
        <View style={ui.rowLine}>
          <Icon name="spark" color={colors.red} size={40} />
          <View style={ui.flex}><Heading>Today’s allowance</Heading><Note>Daily reset at 00:00 UTC</Note></View>
        </View>
        <Text style={styles.number}>3 free · {rewardKeys.length} earned</Text>
        <View style={ui.wrap}>{[0, 1, 2, 3, 4].map((slot) => <View key={slot} style={[styles.slot, slot < 3 + rewardKeys.length && styles.slotFree]} />)}</View>
        <Note>Example balance · Local preview requests use no credits.</Note>
      </Panel>
      <Panel>
        <Heading>Earn up to 2 extra</Heading>
        <Body>Verified rewards can add up to two generations per UTC day, for five total.</Body>
        <Row title="Watch a rewarded ad" detail="Review the offer" icon="spark" onPress={() => openPreview("ad")} />
        <Row title="Share a cooked result" detail="Requires an eligible verified public post" icon="share" onPress={() => openPreview("share")} />
      </Panel>
    </PreviewPage>
  );
}

const destinations = ["TikTok", "Instagram"] as const;

export function ShareScreen({ recipe }: { recipe?: RecipeCase }) {
  const { cases, proofs } = usePreview();
  const [proofId, setProofId] = useState(recipe?.id ?? proofs[0]?.caseId);
  const [destination, setDestination] = useState<Destination>("TikTok");
  const selected = proofs.find((proof) => proof.caseId === proofId);

  return (
    <PreviewPage title="Share Cooked Result" creamHeader>
      <Panel>
        <Heading>Choose a cooked photo</Heading>
        {proofs.map((proof) => (
          <Row key={proof.caseId} icon="camera"
            title={cases.find((item) => item.id === proof.caseId)?.title ?? "Cooked result"}
            detail={proof.caseId === proofId ? "Selected · Local photo" : "Local photo"}
            onPress={() => setProofId(proof.caseId)} />
        ))}
        {selected ? <ProofArt uri={selected.uri} label="Selected local cooked photo" /> : (
          <Body>Add a cooked photo from a recipe to try the clip layout.</Body>
        )}
      </Panel>
      <Panel>
        <Heading>Choose a destination</Heading>
        <Chips choices={destinations} value={destination} onSelect={setDestination} />
        <Note>{destination === "Instagram" ? "Reward eligibility requires a professional account and a verified public post." : "Reward eligibility requires a verified public post."}</Note>
      </Panel>
      <Action label="Preview clip layout" disabled={!selected} onPress={() => {
        if (selected) router.push({
          pathname: "/preview/[screen]",
          params: { screen: "clip", caseId: selected.caseId, destination },
        });
      }} />
      <Note>Your local photo is available for layout testing. Live posting requires your own approved cooked result and a connected account.</Note>
    </PreviewPage>
  );
}

export function ClipScreen({ recipe, destination }: { recipe: RecipeCase; destination: Destination }) {
  const { proofs, saveShareCaption } = usePreview();
  const proof = proofs.find((item) => item.caseId === recipe.id);
  const [caption, setCaption] = useState(`I cooked ${recipe.title}. What’s your verdict?`);

  return (
    <PreviewPage title="Clip Preview" creamHeader>
      {proof ? (
        <>
          <View style={styles.clip}>
            <ProofArt uri={proof.uri} label="Local cooked photo used in the clip layout" />
            <Text style={[ui.heading, ui.lightInk]}>{recipe.title}</Text>
            <View style={ui.wrap}>
              <Badge tone="red">Crime {recipe.crime}/100</Badge><Badge>Taste {proof.taste}/5</Badge>
            </View>
            <Text numberOfLines={4} style={[ui.body, ui.lightInk]}>{proof.verdict}</Text>
          </View>
          <Note>9:16 cooked photo layout</Note>
          <Action label="Play bundled sample clip" kind="outline" onPress={() => openPreview("sample-clip")} />
          <Panel>
            <Heading>Share to {destination}</Heading>
            <Field accessibilityLabel="Caption" multiline value={caption} onChangeText={setCaption} maxLength={2200} />
            <Note>Your photo and caption stay local to this session.</Note>
            <Action label="Review posting requirements" onPress={() => {
              saveShareCaption(`${recipe.id}:${destination}`, caption);
              router.push({
                pathname: "/preview/[screen]",
                params: { screen: "posting", caseId: recipe.id, destination },
              });
            }} />
          </Panel>
        </>
      ) : (
        <Panel><Heading>No local photo selected</Heading><Body>Add a cooked result before previewing a clip.</Body></Panel>
      )}
    </PreviewPage>
  );
}

export function ConnectionsScreen() {
  const { connectedAccounts, setAccountConnected } = usePreview();
  const [destination, setDestination] = useState<Destination>("TikTok");
  const connected = !!connectedAccounts[destination];
  return (
    <PreviewPage title="Connected Accounts" creamHeader>
      <Panel>
        <Heading>Manage destinations</Heading>
        <Chips choices={destinations} value={destination} onSelect={setDestination} />
        <Badge tone={connected ? "green" : "red"}>{connected ? "SAMPLE ACCOUNT CONNECTED" : "DISCONNECTED IN PREVIEW"}</Badge>
        <Body>Connecting lets you choose an account for a later share. You confirm each post separately.</Body>
        <Note>{destination === "Instagram" ? "Eligible posting requires an Instagram Creator or Business account." : "Public visibility must be verified for rewards."}</Note>
        <PreviewDecision trigger={connected ? `Disconnect ${destination}` : `Connect sample ${destination}`}
          title={connected ? `Disconnect ${destination}?` : `Connect sample ${destination} account?`}
          message={connected ? "Remove this sample connection from the current session." : "This adds a local example connection for the posting flow."}
          success={connected ? "Sample account disconnected" : "Sample account connected"}
          destructive={connected} onConfirm={() => setAccountConnected(destination, !connected)} />
      </Panel>
    </PreviewPage>
  );
}

export function PrivacyScreen({ deletion = false }: { deletion?: boolean }) {
  const { blockedAuthors, setAuthorBlocked, deletePreviewAccount } = usePreview();
  return (
    <PreviewPage title={deletion ? "Delete Account" : "Account & Privacy"} creamHeader>
      <Panel>
        <Heading>{deletion ? "Review account deletion" : "Your data and visibility"}</Heading>
        <Body>{deletion ? "Try the account deletion confirmation using this session’s sample data." : "Drafts and unapproved cooked photos are private. Published recipes and approved public evidence have separate visibility."}</Body>
        {deletion ? (
          <PreviewDecision trigger="Delete preview account" title="Delete this preview account?"
            message="This clears the drafts, reviews, votes, and settings in this preview session."
            success="Preview account cleared" destructive onConfirm={deletePreviewAccount} />
        ) : (
          <Row title="Review account deletion" icon="lock" onPress={() => openPreview("delete")} />
        )}
      </Panel>
      {!deletion && (
        <Panel>
          <Heading>Blocked accounts</Heading>
          {blockedAuthors.length === 0 && <Note>No accounts are blocked in this session.</Note>}
          {blockedAuthors.map((author) => (
            <Row key={author} title={`Unblock ${author}`} detail="Restore sample content" icon="person"
              onPress={() => setAuthorBlocked(author, false)} />
          ))}
        </Panel>
      )}
    </PreviewPage>
  );
}

export function HelpScreen() {
  return (
    <PreviewPage title="Help & Feedback" creamHeader>
      <Panel>
        <Heading>Using the preview</Heading>
        <Body>Search sample cases, try the Create form, or attach a photo of what you cooked to see the proof and sharing layouts.</Body>
        <Note>Preview changes reset when you reload the app.</Note>
      </Panel>
      <Panel><Heading>Report a case</Heading><Body>Open the menu in a public case file to review the reporting options.</Body></Panel>
    </PreviewPage>
  );
}

const styles = StyleSheet.create({
  welcome: { alignItems: "center", paddingVertical: 20, gap: 10 },
  brand: { ...ui.title, fontSize: 39, lineHeight: 45, textAlign: "center" },
  tagline: { ...ui.heading, color: colors.forestDeep, textAlign: "center" },
  avatar: { width: 62, height: 62, borderRadius: 31, alignItems: "center", justifyContent: "center", backgroundColor: colors.forestTint },
  number: { fontFamily: "Bricolage", fontSize: 30, color: colors.forestDeep },
  slot: { width: 24, height: 24, borderRadius: 12, backgroundColor: "#DDCCA7" },
  slotFree: { backgroundColor: colors.forest },
  clip: { width: "87%", maxWidth: 330, alignSelf: "center", aspectRatio: 9 / 16, gap: 10, padding: 13, borderRadius: 20, backgroundColor: "#20251D" },
});
