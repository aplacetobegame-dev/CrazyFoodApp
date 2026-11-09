import { StatusBar } from "expo-status-bar";
import { useRef, useState, type ComponentRef } from "react";
import {
  Keyboard, KeyboardAvoidingView, Modal, Platform, Pressable,
  ScrollView, Text, TextInput, View, type LayoutChangeEvent,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors } from "@/components/food-felonies-theme";
import { FoodTabs, type FoodTab } from "@/components/food-tabs";
import type { RecipeInput } from "@/features/preview/preview-data";
import { ClipboardClip, GinghamCorner, Icon, StampMarks } from "./create-art";
import { styles } from "./create-recipe-styles";
import { WeirdnessSlider } from "./weirdness-slider";

type Ingredient = { name: string; quantity?: string };
type Dialog = { kind: "quantity"; name: string } | { kind: "unavailable" };

const previewIngredients: Ingredient[] = [
  { name: "Rice" }, { name: "Eggs" }, { name: "Dill Pickles" }, { name: "Maple Syrup" },
];

function namesWithInput(current: Ingredient[], input: string): Ingredient[] {
  const names = new Map(current.map((item) => [item.name.toLowerCase(), item]));
  for (const entry of input.split(",")) {
    const name = entry.trim();
    if (name && !names.has(name.toLowerCase())) {
      names.set(name.toLowerCase(), { name });
    }
  }
  return [...names.values()];
}

function IngredientField({
  excluded = false, items, input, onInput, onAdd, onRemove, onQuantity, error, onLayout,
}: {
  excluded?: boolean;
  items: Ingredient[];
  input: string;
  onInput: (input: string) => void;
  onAdd: () => void;
  onRemove: (name: string) => void;
  onQuantity?: (ingredient: Ingredient) => void;
  error?: string;
  onLayout?: (event: LayoutChangeEvent) => void;
}) {
  const label = excluded ? "Ingredients to exclude" : "Ingredients on hand";

  const inline = excluded && items.length === 1;
  const inputControl = (
    <View style={[styles.inputRow, inline && styles.inlineInput, error && styles.inputError]}>
      <TextInput
        accessibilityLabel={label}
        accessibilityHint="Separate multiple ingredients with commas"
        autoCapitalize="sentences"
        onChangeText={onInput}
        onSubmitEditing={onAdd}
        placeholder={excluded ? "e.g. peanuts" : "e.g. rice, eggs, dill pickles"}
        placeholderTextColor={colors.muted}
        returnKeyType="done"
        style={styles.addInput}
        value={input}
      />
      <Pressable accessibilityRole="button"
        accessibilityLabel={excluded ? "Add exclusions" : "Add ingredients"}
        accessibilityState={{ disabled: !input.trim() }}
        disabled={!input.trim()} onPress={onAdd} style={styles.addButton}>
        <Text style={[styles.bold, !input.trim() && styles.muted]}>Add</Text>
      </Pressable>
    </View>
  );
  const chips = items.length > 0 && (
    <View style={styles.chips}>
      {items.map((item) => (
        <View key={item.name} style={[styles.chip, excluded && styles.exclusionChip]}>
          {onQuantity ? (
            <Pressable accessibilityRole="button"
              accessibilityLabel={item.quantity ? `${item.name}, quantity ${item.quantity}` : item.name}
              accessibilityHint="Edit quantity"
              onPress={() => onQuantity(item)} style={styles.chipName}>
              <Text style={styles.chipText}>{item.quantity ? `${item.quantity} ${item.name}` : item.name}</Text>
            </Pressable>
          ) : (
            <View style={styles.chipName}><Text style={styles.chipText}>{item.name}</Text></View>
          )}
          <Pressable accessibilityRole="button" accessibilityLabel={`Remove ${item.name}`}
            onPress={() => onRemove(item.name)} style={styles.removeChip}>
            <Icon name="close" color={colors.ink} size={16} />
          </Pressable>
        </View>
      ))}
    </View>
  );

  return (
    <View onLayout={onLayout} style={styles.section}>
      <View style={styles.labelRow}>
        <Icon name={excluded ? "exclude" : "bowl"} color={excluded ? colors.red : colors.ink} />
        <Text accessibilityRole="header" style={styles.label}>
          {label}{!excluded && <Text style={styles.red}> *</Text>}
        </Text>
      </View>
      <View style={inline ? styles.inlineExclusion : styles.ingredientControls}>
        {inline && chips}
        {inputControl}
        {!inline && chips}
      </View>
      {error && <Text accessibilityRole="alert" style={[styles.helper, styles.red]}>{error}</Text>}
      {excluded && (
        <Text style={styles.helper}>We send exclusions with your recipe request.</Text>
      )}
    </View>
  );
}

export function CreateRecipeScreen({ preview = false, onBack, onSelectTab, onPreviewGenerate }: {
  preview?: boolean;
  onBack?: () => void;
  onSelectTab?: (tab: FoodTab) => void;
  onPreviewGenerate?: (request: RecipeInput) => void;
}) {
  const scroll = useRef<ComponentRef<typeof ScrollView>>(null);
  const fieldOffsets = useRef({ ingredients: 0, time: 0 });
  const [ingredients, setIngredients] = useState<Ingredient[]>(preview ? previewIngredients : []);
  const [exclusions, setExclusions] = useState<Ingredient[]>(preview ? [{ name: "Peanuts" }] : []);
  const [ingredientInput, setIngredientInput] = useState("");
  const [exclusionInput, setExclusionInput] = useState("");
  const [servings, setServings] = useState(2);
  const [maxMinutes, setMaxMinutes] = useState(preview ? "30" : "");
  const [equipment, setEquipment] = useState(preview ? "Stovetop" : "");
  const initialWeirdness = preview ? 72 : 50;
  const [weirdness, setWeirdness] = useState(initialWeirdness);
  const [optionsOpen, setOptionsOpen] = useState(false);
  const [cuisine, setCuisine] = useState("");
  const [dietary, setDietary] = useState("");
  const [ingredientError, setIngredientError] = useState<string>();
  const [timeError, setTimeError] = useState(false);
  const [dialog, setDialog] = useState<Dialog>();
  const [quantity, setQuantity] = useState("");

  function addIngredients() {
    setIngredients((current) => namesWithInput(current, ingredientInput));
    setIngredientInput("");
    setIngredientError(undefined);
  }

  function addExclusions() {
    setExclusions((current) => namesWithInput(current, exclusionInput));
    setExclusionInput("");
    setIngredientError(undefined);
  }

  function generate() {
    const included = namesWithInput(ingredients, ingredientInput);
    const excluded = namesWithInput(exclusions, exclusionInput);
    const excludedNames = new Set(excluded.map(({ name }) => name.toLowerCase()));
    const overlap = included.find(({ name }) => excludedNames.has(name.toLowerCase()));
    const hasInvalidTime = maxMinutes !== "" && Number(maxMinutes) < 1;

    setIngredients(included);
    setExclusions(excluded);
    setIngredientInput("");
    setExclusionInput("");
    setTimeError(hasInvalidTime);
    setIngredientError(
      included.length === 0 ? "Add at least one ingredient to continue."
        : overlap ? `Remove ${overlap.name} from one of the two lists.` : undefined,
    );
    Keyboard.dismiss();

    if (included.length === 0 || overlap || hasInvalidTime) {
      const { ingredients: ingredientsY, time } = fieldOffsets.current;
      const y = included.length === 0 || overlap ? ingredientsY : time;
      scroll.current?.scrollTo({ y, animated: true });
      return;
    }

    if (onPreviewGenerate) {
      onPreviewGenerate({
        ingredients: included,
        exclusions: excluded.map(({ name }) => name),
        servings,
        weirdness,
        maxMinutes: maxMinutes ? Number(maxMinutes) : undefined,
        equipment: equipment.trim(),
        cuisine: cuisine.trim(),
        dietary: dietary.trim(),
      });
      return;
    }

    // The generation endpoint and live daily balance are not implemented yet.
    setDialog({ kind: "unavailable" });
  }

  function saveQuantity() {
    if (dialog?.kind !== "quantity") {
      return;
    }
    setIngredients((current) => current.map((item) => item.name === dialog.name
      ? { ...item, quantity: quantity.trim() || undefined }
      : item));
    setDialog(undefined);
  }

  return (
    <SafeAreaView style={styles.safeTop} edges={["top", "left", "right"]}>
      <StatusBar style="light" />
      <KeyboardAvoidingView style={styles.keyboard} behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <View style={styles.frame}>
          <View style={styles.header}>
            {onBack && (
              <Pressable accessibilityRole="button" accessibilityLabel="Go back"
                onPress={onBack} style={styles.back}>
                <Icon name="back" color={colors.cream} size={24} />
              </Pressable>
            )}
            <Text accessibilityRole="header" style={styles.pageTitle}>Create a Recipe</Text>
          </View>
          <ScrollView ref={scroll} style={styles.scroll} contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled">
            <View style={styles.corner}><GinghamCorner /></View>
            <View style={styles.board}>
              <View style={styles.paper}>
                <View style={styles.hero}>
                  <View style={styles.stamp} accessible accessibilityLabel="File a Food Felony">
                    <Text aria-hidden style={[styles.stampText, styles.stampTop]}>FILE A</Text>
                    <Text aria-hidden style={[styles.stampText, styles.stampBottom]}>FOOD FELONY</Text>
                    <View style={styles.stampMarks}><StampMarks /></View>
                  </View>
                  <Text style={styles.intro}>Turn the ingredients you have into a delicious (and possibly criminal) recipe.</Text>
                  <View style={styles.allowanceRow}>
                    <View style={styles.allowance}>
                      <Text style={styles.allowanceText}>3 free daily · Up to 2 earned</Text>
                    </View>
                    {preview && (
                      <Text accessibilityLabel="Design preview with sample ingredients" style={styles.previewLabel}>
                        Design preview
                      </Text>
                    )}
                  </View>
                </View>

                <IngredientField items={ingredients} input={ingredientInput}
                  onInput={setIngredientInput} onAdd={addIngredients}
                  onRemove={(name) => {
                    setIngredients((current) => current.filter((item) => item.name !== name));
                    setIngredientError(undefined);
                  }}
                  onQuantity={(item) => {
                    setQuantity(item.quantity ?? "");
                    setDialog({ kind: "quantity", name: item.name });
                  }}
                  error={ingredientError}
                  onLayout={({ nativeEvent }) => { fieldOffsets.current.ingredients = nativeEvent.layout.y; }} />
                <IngredientField excluded items={exclusions} input={exclusionInput}
                  onInput={setExclusionInput} onAdd={addExclusions}
                  onRemove={(name) => {
                    setExclusions((current) => current.filter((item) => item.name !== name));
                    setIngredientError(undefined);
                  }} />

                <View style={[styles.section, styles.preferences]}
                  onLayout={({ nativeEvent }) => { fieldOffsets.current.time = nativeEvent.layout.y; }}>
                  <View style={styles.preference}>
                    <View style={styles.preferenceLabel}>
                      <Icon name="people" color={colors.ink} size={16} />
                      <Text style={styles.smallBold}>Servings</Text>
                    </View>
                    <View style={styles.stepper}>
                      <Pressable accessibilityRole="button" accessibilityLabel="Decrease servings"
                        accessibilityState={{ disabled: servings === 1 }} disabled={servings === 1}
                        onPress={() => setServings((value) => Math.max(1, value - 1))} style={styles.step}>
                        <Text style={[styles.stepText, servings === 1 && styles.muted]}>−</Text>
                      </Pressable>
                      <Text accessibilityLabel={`${servings} servings`} accessibilityLiveRegion="polite"
                        style={styles.bold}>{servings}</Text>
                      <Pressable accessibilityRole="button" accessibilityLabel="Increase servings"
                        onPress={() => setServings((value) => value + 1)} style={styles.step}>
                        <Text style={styles.stepText}>+</Text>
                      </Pressable>
                    </View>
                  </View>
                  <View style={styles.preference}>
                    <View style={styles.preferenceLabel}>
                      <Icon name="clock" color={colors.ink} size={16} />
                      <Text style={styles.smallBold}>Max time</Text>
                    </View>
                    <View style={[styles.minuteControl, timeError && styles.inputError]}>
                      <TextInput accessibilityLabel="Maximum time in minutes"
                        keyboardType="number-pad" onChangeText={(value) => {
                          setMaxMinutes(value.replace(/\D/g, ""));
                          setTimeError(false);
                        }}
                        maxLength={4} placeholder="Any" placeholderTextColor={colors.muted}
                        style={styles.minuteInput} value={maxMinutes} />
                      {!!maxMinutes && <Text style={styles.helper}>min</Text>}
                    </View>
                    {timeError && <Text accessibilityRole="alert" style={[styles.helper, styles.red]}>Use 1 min or more.</Text>}
                  </View>
                  <View style={styles.preference}>
                    <View style={styles.preferenceLabel}>
                      <Icon name="pan" color={colors.ink} size={16} />
                      <Text style={styles.smallBold}>Equipment</Text>
                    </View>
                    <TextInput accessibilityLabel="Equipment" onChangeText={setEquipment}
                      placeholder="Any" placeholderTextColor={colors.muted}
                      style={[styles.field, styles.equipment]} value={equipment} />
                  </View>
                </View>

                <View style={styles.section}>
                  <View style={styles.labelRow}>
                    <Icon name="flask" color={colors.ink} />
                    <Text accessibilityRole="header" style={[styles.label, styles.grow]}>Weirdness Level</Text>
                    <Text style={styles.score}><Text style={styles.scoreNumber}>{weirdness}</Text> / 100</Text>
                  </View>
                  <WeirdnessSlider initialValue={initialWeirdness} value={weirdness} onChange={setWeirdness} />
                  <View style={styles.rangeLabels}>
                    <Text style={styles.smallBold}>Normal</Text>
                    <Text style={styles.smallBold}>Food Felony</Text>
                  </View>
                </View>

                <View style={styles.optionsSection}>
                  <Pressable accessibilityRole="button" accessibilityState={{ expanded: optionsOpen }}
                    onPress={() => setOptionsOpen((open) => !open)} style={styles.optionsButton}>
                    <Icon name="options" color={colors.ink} />
                    <Text style={[styles.label, styles.grow]}>More Options <Text style={styles.optionsHint}>(cuisine, dietary)</Text></Text>
                    <Icon name={optionsOpen ? "up" : "down"} color={colors.ink} size={19} />
                  </Pressable>
                  {optionsOpen && (
                    <View style={styles.optionsFields}
                      onLayout={() => scroll.current?.scrollToEnd({ animated: true })}>
                      <Text style={styles.smallBold}>Cuisine</Text>
                      <TextInput accessibilityLabel="Cuisine" onChangeText={setCuisine}
                        placeholder="e.g. Korean" placeholderTextColor={colors.muted}
                        style={styles.field} value={cuisine} />
                      <Text style={styles.smallBold}>Dietary preferences</Text>
                      <TextInput accessibilityLabel="Dietary preferences" onChangeText={setDietary}
                        placeholder="e.g. vegetarian" placeholderTextColor={colors.muted}
                        style={styles.field} value={dietary} />
                    </View>
                  )}
                </View>
              </View>
              <View style={styles.clip}><ClipboardClip /></View>
            </View>
          </ScrollView>

          <SafeAreaView edges={["bottom"]} style={styles.footer}>
            <Pressable accessibilityRole="button" onPress={generate}
              style={({ pressed }) => [styles.generate, pressed && styles.generatePressed]}>
              <Text style={styles.generateText}>Generate Recipe</Text>
              <Icon name="spark" color={colors.cream} size={22} />
            </Pressable>
            <FoodTabs active="create" onSelect={onSelectTab} />
          </SafeAreaView>
        </View>
      </KeyboardAvoidingView>

      <Modal animationType="fade" transparent visible={!!dialog} onRequestClose={() => setDialog(undefined)}>
        <KeyboardAvoidingView style={styles.scrim} behavior={Platform.OS === "ios" ? "padding" : undefined}>
          <View style={styles.dialog} accessibilityViewIsModal>
            {dialog?.kind === "quantity" ? (
              <>
                <Text accessibilityRole="header" style={styles.dialogTitle}>Quantity for {dialog.name}</Text>
                <TextInput autoFocus accessibilityLabel="Ingredient quantity" onChangeText={setQuantity}
                  onSubmitEditing={saveQuantity} placeholder="Optional, e.g. 1 cup" placeholderTextColor={colors.muted}
                  returnKeyType="done" style={styles.field} value={quantity} />
                <View style={styles.dialogActions}>
                  <Pressable accessibilityRole="button" onPress={() => setDialog(undefined)} style={styles.dialogCancel}>
                    <Text style={styles.bold}>Cancel</Text>
                  </Pressable>
                  <Pressable accessibilityRole="button" onPress={saveQuantity} style={styles.dialogButton}>
                    <Text style={styles.dialogButtonText}>Save quantity</Text>
                  </Pressable>
                </View>
              </>
            ) : (
              <>
                <Text accessibilityRole="header" style={styles.dialogTitle}>Generation unavailable</Text>
                <Text style={styles.dialogBody}>
                  {preview
                    ? "Recipe generation is offline in this preview. You can keep editing your inputs."
                    : "Recipe generation and the live allowance are still being connected. Your inputs are still here."}
                </Text>
                <Pressable accessibilityRole="button" onPress={() => setDialog(undefined)} style={styles.dialogButton}>
                  <Text style={styles.dialogButtonText}>Back to recipe</Text>
                </Pressable>
              </>
            )}
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}
