import { useEffect, useRef, useState, type ComponentRef } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { colors } from "@/components/food-felonies-theme";
import { ClipboardClip, Icon, StampMarks } from "@/features/create/create-art";
import { sampleRecipes, usePreview, type RecipeCase } from "./preview-data";
import { openPreview, previewRoute } from "./preview-navigation";
import { Action, Badge, Body, ChefMark, Chips, ConceptArt, Field, Heading, Note, Panel, PreviewPage, ProofArt, Row, ui } from "./preview-ui";
import { router } from "expo-router";
import { FailureCard, sampleReviewer } from "./preview-dialogs";

function RecipeCard({ recipe, compact = false }: { recipe: RecipeCase; compact?: boolean }) {
  const { votes } = usePreview();
  const vote = votes[recipe.id];
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={recipe.title} onPress={() => openPreview("case", recipe.id)}
      style={({ pressed }) => [ui.panel, compact && ui.rowLine, pressed && ui.faded]}>
      <View style={compact ? styles.thumbnail : undefined}>
        <ConceptArt recipe={recipe} square={compact} />
        {!compact && <View style={styles.imageBadge}><Badge>CASE #{recipe.number}</Badge></View>}
      </View>
      <View style={compact ? ui.flex : styles.summary}>
        <Text style={compact ? ui.bold : ui.heading}>{recipe.title}</Text>
        {compact ? (
          <View style={ui.wrap}>
            {recipe.owned && <Badge tone={recipe.published ? "green" : "red"}>{recipe.published ? "Public in preview" : "Private draft"}</Badge>}
            <Note>Crime {recipe.crime}/100</Note>
          </View>
        ) : (
          <>
            <Body>{recipe.description}</Body>
            <View style={ui.wrap}>
              <Badge tone="red">Crime {recipe.crime}/100</Badge>
              <Text style={[ui.bold, ui.redText]}>{recipe.votes[0] + Number(vote === "guilty")} Guilty</Text>
              <Text style={styles.acquitted}>{recipe.votes[1] + Number(vote === "acquitted")} Acquitted</Text>
            </View>
          </>
        )}
      </View>
    </Pressable>
  );
}

const sorts = ["Trending", "Newest", "Most Voted"] as const;

export function DiscoverScreen() {
  const { cases, votes, blockedAuthors } = usePreview();
  const [sort, setSort] = useState<typeof sorts[number]>("Trending");

  useEffect(() => {
    router.prefetch("/create");
  }, []);
  const publicCases = cases.filter((recipe) => recipe.published && !blockedAuthors.includes(recipe.author));
  const totalVotes = (recipe: RecipeCase) => recipe.votes[0] + recipe.votes[1] + Number(!!votes[recipe.id]);
  if (sort === "Newest") publicCases.sort((a, b) => Number(b.number) - Number(a.number));
  if (sort === "Most Voted") publicCases.sort((a, b) => totalVotes(b) - totalVotes(a));

  return (
    <PreviewPage title="Discover" activeTab="discover">
      <View style={styles.brand}>
        <ChefMark />
        <View style={ui.flex}>
          <Text style={styles.food}>Food <Text style={ui.redText}>Felonies</Text></Text>
          <Badge>MAKE IT. COOK IT. SHOW THE EVIDENCE.</Badge>
        </View>
      </View>
      <Pressable accessibilityRole="button" accessibilityLabel="Search recipes" onPress={() => openPreview("search")} style={styles.search}>
        <Icon name="search" color={colors.forestDeep} size={21} />
        <Text style={ui.body}>Search recipes or ingredients</Text>
      </Pressable>
      <Chips choices={sorts} value={sort} onSelect={setSort} />
      {publicCases.map((recipe) => <RecipeCard key={recipe.id} recipe={recipe} />)}
      <Note>Design preview · Sample cases and local votes</Note>
    </PreviewPage>
  );
}

const searchFilters = ["All", "Crime 70+", "Under 30 min"] as const;

export function SearchScreen() {
  const { cases, blockedAuthors } = usePreview();
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<typeof searchFilters[number]>("All");
  const words = query.toLowerCase().trim().split(/\s+/);
  const matches = cases.filter((recipe) => {
    if (!recipe.published || blockedAuthors.includes(recipe.author)) return false;
    if (filter === "Crime 70+" && recipe.crime < 70) return false;
    if (filter === "Under 30 min" && recipe.prep + recipe.cook >= 30) return false;
    const searchable = [recipe.title, recipe.description, ...recipe.ingredients].join(" ").toLowerCase();
    return words.every((word) => searchable.includes(word));
  });

  return (
    <PreviewPage title="Search Recipes" creamHeader>
      <Field accessibilityLabel="Search recipes" placeholder="Try rice, pickles, or cheddar" value={query}
        onChangeText={setQuery} autoCapitalize="none" returnKeyType="search" />
      <Chips choices={searchFilters} value={filter} onSelect={setFilter} />
      <Heading>{matches.length} {matches.length === 1 ? "case" : "cases"} found</Heading>
      {matches.map((recipe) => <RecipeCard key={recipe.id} recipe={recipe} compact />)}
      {!matches.length && <Panel><Heading>No cases found</Heading><Body>Try a different ingredient or clear your filter.</Body></Panel>}
    </PreviewPage>
  );
}

const caseFilters = ["All", "Drafts", "Public", "Cooked"] as const;

export function CasesScreen() {
  const { cases, proofs, signedIn, signIn } = usePreview();
  const [filter, setFilter] = useState<typeof caseFilters[number]>("All");
  const recipes = filter === "Cooked" ? [] : cases.filter((recipe) => recipe.owned
    && (filter === "All" || (filter === "Public" ? recipe.published : !recipe.published)));
  const cooked = filter === "All" || filter === "Cooked" ? proofs : [];

  if (!signedIn) {
    return (
      <PreviewPage title="My Cases" activeTab="cases">
        <Panel>
          <Heading>My Cases is private</Heading>
          <Body>Return to the sample account to see your local drafts and cooked results.</Body>
          <Action label="Return to preview account" onPress={signIn} />
        </Panel>
      </PreviewPage>
    );
  }

  return (
    <PreviewPage title="My Cases" activeTab="cases">
      <View style={styles.intro}>
        <Badge>YOUR CASE CABINET</Badge>
        <Text style={ui.title}>The evidence is yours.</Text>
        <Body>Pick up a draft or see the cooked results you’ve added in this session.</Body>
      </View>
      <Chips choices={caseFilters} value={filter} onSelect={setFilter} />
      {recipes.map((recipe) => <RecipeCard key={recipe.id} recipe={recipe} compact />)}
      {cooked.map((proof) => (
        <Panel key={proof.caseId}>
          <Row title={cases.find((recipe) => recipe.id === proof.caseId)?.title ?? "Cooked result"}
            detail={`Local proof · ${proof.status}`} icon="camera"
            onPress={() => openPreview("proof-status", proof.caseId)} />
        </Panel>
      ))}
      {!recipes.length && !cooked.length && (
        <Panel>
          <Heading>{filter === "Cooked" ? "No cooked results yet" : "No cases here yet"}</Heading>
          <Body>{filter === "Cooked" ? "Open a recipe and add a photo of what you made." : "File your first Food Felony from the Create tab."}</Body>
          <Action label={filter === "Cooked" ? "Explore recipes" : "Create a recipe"}
            onPress={() => filter === "Cooked" ? router.replace(previewRoute("discover")) : router.replace("/create")} />
        </Panel>
      )}
    </PreviewPage>
  );
}

function Metric({ label, value, tone }: { label: string; value: number; tone: "blush" | "mustard" }) {
  return (
    <View style={ui.flex}>
      <Panel tone={tone}>
        <Text style={ui.bold}>{label}</Text>
        <Text style={styles.metric}>{value}<Text style={ui.note}> /100</Text></Text>
      </Panel>
    </View>
  );
}

export function CaseScreen({ recipe }: { recipe: RecipeCase }) {
  const scroll = useRef<ComponentRef<typeof ScrollView>>(null);
  const sections = useRef({ recipe: 0, community: 0 });
  const { votes, vote, proofs, blockedAuthors, signedIn } = usePreview();
  const currentVote = votes[recipe.id];
  const ownProof = proofs.find((proof) => proof.caseId === recipe.id
    && (signedIn || (recipe.published && proof.status === "approved")));
  const publishedSample = recipe.published && sampleRecipes.some((item) => item.id === recipe.id);
  const sampleReview = recipe.id === "pickle-rice" && !blockedAuthors.includes(sampleReviewer);

  return (
    <PreviewPage title={recipe.published ? "Recipe Case File" : "Private Case File"}
      scrollProps={{ ref: scroll }}
      trailing={recipe.published && (
        <Pressable accessibilityRole="button" accessibilityLabel="Report case" onPress={() => openPreview("report", recipe.id)}
          style={ui.side}><Icon name="options" color={colors.cream} /></Pressable>
      )}>
      <Panel>
        <View style={ui.wrap}>
          <Badge>CASE FILE #{recipe.number}</Badge>
          <Badge tone={recipe.published ? "green" : "red"}>{recipe.published ? "PUBLIC SAMPLE" : "PRIVATE DRAFT"}</Badge>
        </View>
        <Text accessibilityRole="header" style={ui.title}>{recipe.title}</Text>
        <Body>{recipe.description}</Body>
        <ConceptArt recipe={recipe} square />
        <Note>AI-generated concept image · Case by {recipe.author}</Note>
        {publishedSample && <Action kind="outline" label="Share case preview" onPress={() => openPreview("share-card", recipe.id)} />}
      </Panel>
      {recipe.request && (
        <Panel>
          <Badge>REQUEST PREVIEW</Badge>
          <Body>{recipe.request.ingredients.map(({ name, quantity }) => quantity ? `${quantity} ${name}` : name).join(", ")}</Body>
          <Note>
            {recipe.request.servings} servings · Weirdness {recipe.request.weirdness}/100
            {recipe.request.maxMinutes ? ` · Up to ${recipe.request.maxMinutes} min` : ""}
          </Note>
          {!!recipe.request.exclusions.length && <Note>Exclusions: {recipe.request.exclusions.join(", ")}</Note>}
          <Note>This sample recipe illustrates the case file layout. It was prepared independently of your request.</Note>
        </Panel>
      )}
      <View style={ui.rowLine}>
        <Metric label="Crime Level" value={recipe.crime} tone="blush" />
        <Metric label="Regret Potential" value={recipe.regret} tone="mustard" />
      </View>
      <Panel><Text style={ui.bold}>Prep {recipe.prep} min  ·  Cook {recipe.cook} min  ·  Serves {recipe.serves}</Text></Panel>
      {recipe.published && (
        <View style={ui.rowLine}>
          <View style={ui.flex}><Action kind="outline" label="The Recipe" onPress={() => scroll.current?.scrollTo({ y: sections.current.recipe, animated: true })} /></View>
          <View style={ui.flex}><Action kind="outline" label="Community" onPress={() => scroll.current?.scrollTo({ y: sections.current.community, animated: true })} /></View>
        </View>
      )}
      <View style={styles.summary} onLayout={({ nativeEvent }) => { sections.current.recipe = nativeEvent.layout.y; }}>
        <Panel>
          <Heading>Ingredients</Heading>
          {recipe.ingredients.map((ingredient) => <Body key={ingredient}>• {ingredient}</Body>)}
        </Panel>
        <Panel>
          <Heading>Instructions</Heading>
          {recipe.steps.map((step, index) => (
            <View key={step} style={styles.step}>
              <Badge tone="green">{index + 1}</Badge>
              <View style={ui.flex}><Body>{step}</Body></View>
            </View>
          ))}
        </Panel>
      </View>
      <Action label="I cooked it — add proof" onPress={() => openPreview("camera", recipe.id)} />
      {recipe.owned && !recipe.published && <Action label="Publish case…" kind="outline" onPress={() => openPreview("publish", recipe.id)} />}
      <View style={styles.summary} onLayout={({ nativeEvent }) => { sections.current.community = nativeEvent.layout.y; }}>
        <Heading>Cooked Results</Heading>
        {ownProof ? (
          <Panel>
            <Badge tone={ownProof.status === "approved" && recipe.published ? "green" : "mustard"}>{signedIn ? "YOUR LOCAL PROOF" : "APPROVED SAMPLE PROOF"}</Badge>
            <ProofArt uri={ownProof.uri} label="Your local cooked-result photo" />
            <Text style={ui.bold}>Taste {ownProof.taste}/5 · Crime {recipe.crime}/100</Text>
            <Body>{ownProof.verdict}</Body>
            <Note>{ownProof.status === "approved" && recipe.published ? "Approved · Visible in this local case" : `Private preview · ${ownProof.status}`}</Note>
            {signedIn && <Action label="View proof status" kind="outline" onPress={() => openPreview("proof-status", recipe.id)} />}
          </Panel>
        ) : (
          <Panel><Heading>No cooked proof yet</Heading><Body>Made it? Add a photo of your dish and tell us how it tasted.</Body></Panel>
        )}
        {recipe.published && (
          <>
            {sampleReview && (
              <Panel>
                <Badge>REPORTING FIXTURE</Badge>
                <Heading>Cooked by {sampleReviewer}</Heading>
                <Note>Example review with the photo withheld for this preview.</Note>
                <Action label="Report cooked result" kind="outline" onPress={() => openPreview("proof-report", recipe.id)} />
              </Panel>
            )}
            <Heading>Community Verdict</Heading>
            <View style={ui.rowLine}>
              <View style={ui.flex}><Action kind={currentVote === "guilty" ? "red" : "outline"}
                label={`Guilty · ${recipe.votes[0] + Number(currentVote === "guilty")}`} onPress={() => vote(recipe.id, "guilty")} /></View>
              <View style={ui.flex}><Action kind={currentVote === "acquitted" ? "green" : "outline"}
                label={`Acquitted · ${recipe.votes[1] + Number(currentVote === "acquitted")}`} onPress={() => vote(recipe.id, "acquitted")} /></View>
            </View>
            <Note>Your verdict applies only to this preview session.</Note>
          </>
        )}
      </View>
    </PreviewPage>
  );
}

export function GenerationScreen({ recipe }: { recipe: RecipeCase }) {
  const [failed, setFailed] = useState(false);

  return (
    <PreviewPage title="Generating Recipe">
      <Panel tone="forest">
        <View style={styles.generation}><ChefMark /><Text style={[ui.heading, ui.lightInk]}>On the case</Text></View>
      </Panel>
      {failed ? (
        <FailureCard title="Generation failed" detail="Your request is preserved for a retry. In the connected flow, a failed generation returns the reserved slot."
          onRetry={() => setFailed(false)} />
      ) : (
        <Panel>
          <Badge>LOCAL PREVIEW</Badge>
          <Heading>Recipe request ready</Heading>
          <Body>Your form passed validation. Reveal a sample case file to test the rest of the flow.</Body>
          <Action label="Reveal sample case" onPress={() => router.replace(previewRoute("case", recipe.id))} />
          <Action label="Preview a generation failure" kind="outline" onPress={() => setFailed(true)} />
        </Panel>
      )}
    </PreviewPage>
  );
}

export function PublishScreen({ recipe }: { recipe: RecipeCase }) {
  const { publishDraft } = usePreview();
  const [failed, setFailed] = useState(false);
  return (
    <PreviewPage title="Publish Case">
      {failed ? (
        <FailureCard title="Couldn’t publish this case" detail="Your recipe is still a private draft. You can review it and try again."
          onRetry={() => setFailed(false)} />
      ) : (
        <Panel>
          <View style={ui.rowLine}><ClipboardClip /><StampMarks /></View>
          <Badge tone="red">{recipe.published ? "PUBLISHED IN PREVIEW" : "PRIVATE DRAFT"}</Badge>
          <Heading>{recipe.published ? "Case filed" : "Publish this recipe?"}</Heading>
          <Body>{recipe.title}</Body>
          <Note>{recipe.published ? "This case is now visible in your local Discover feed." : "Publishing in this preview adds the sample recipe to your local Discover feed. Approved proof can appear in the local case. Pending and rejected proof stay private."}</Note>
          {!recipe.published && <Action label="Publish in preview" onPress={() => publishDraft(recipe.id)} />}
          {!recipe.published && <Action label="Preview a publish failure" kind="outline" onPress={() => setFailed(true)} />}
          <Action kind="outline" label={recipe.published ? "View public sample" : "Keep private"} onPress={() => router.back()} />
        </Panel>
      )}
    </PreviewPage>
  );
}

const styles = StyleSheet.create({
  brand: { flexDirection: "row", alignItems: "center", gap: 5, paddingBottom: 4 },
  food: { fontFamily: "Bricolage", color: colors.forestDeep, fontSize: 35, lineHeight: 39, marginBottom: 5 },
  search: { ...ui.rowLine, borderWidth: 1, borderColor: colors.border, borderRadius: 14, minHeight: 50, paddingHorizontal: 12, backgroundColor: colors.paper },
  thumbnail: { width: 72 },
  imageBadge: { position: "absolute", top: 8, left: 8, transform: [{ rotate: "-5deg" }] },
  summary: { gap: 8 },
  acquitted: { ...ui.bold, color: colors.forestDeep },
  intro: { gap: 7 },
  metric: { fontFamily: "Bricolage", fontSize: 29, color: colors.ink },
  step: { flexDirection: "row", alignItems: "flex-start", gap: 9 },
  generation: { alignItems: "center", paddingVertical: 34, gap: 15 },
});
