import { Image } from "expo-image";
import { StatusBar } from "expo-status-bar";
import type { ReactNode } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View, type ScrollViewProps, type TextInputProps } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import Svg, { Path } from "react-native-svg";
import { colors } from "@/components/food-felonies-theme";
import { FoodTabs, type FoodTab } from "@/components/food-tabs";
import { Icon, type CreateIconName } from "@/features/create/create-art";
import { backFromPreview, selectPreviewTab } from "./preview-navigation";
import type { RecipeCase } from "./preview-data";

type FoodPageProps = {
  title: string;
  onBack?: () => void;
  footer?: ReactNode;
  children: ReactNode;
  trailing?: ReactNode;
  scrollProps?: ScrollViewProps & { ref?: React.Ref<React.ComponentRef<typeof ScrollView>> };
  creamHeader?: boolean;
};

export function FoodPage({ title, children, trailing, scrollProps, creamHeader: light = false, onBack, footer }: FoodPageProps) {
  return (
    <SafeAreaView edges={["top", "left", "right"]} style={[ui.shell, light && ui.lightShell]}>
      <StatusBar style={light ? "dark" : "light"} />
      <View style={ui.frame}>
        <View style={[ui.header, light && ui.lightHeader]}>
          {onBack ? (
            <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={onBack} style={ui.side}>
              <Icon name="back" color={light ? colors.ink : colors.cream} size={24} />
            </Pressable>
          ) : <View style={ui.side} />}
          <Text accessibilityRole="header" style={[ui.headerTitle, light && ui.ink]}>{title}</Text>
          <View style={ui.side}>{trailing}</View>
        </View>
        <ScrollView style={ui.scroll} contentContainerStyle={ui.content} automaticallyAdjustKeyboardInsets keyboardShouldPersistTaps="handled" {...scrollProps}>
          {children}
        </ScrollView>
        {footer}
      </View>
    </SafeAreaView>
  );
}

export function PreviewPage({ activeTab, creamHeader, ...props }: Omit<FoodPageProps, "onBack" | "footer"> & { activeTab?: FoodTab }) {
  return (
    <FoodPage {...props} creamHeader={creamHeader || !!activeTab} onBack={activeTab ? undefined : backFromPreview}
      footer={(
        <SafeAreaView edges={["bottom"]} style={activeTab ? ui.footer : undefined}>
          {activeTab && <FoodTabs active={activeTab} onSelect={selectPreviewTab} />}
        </SafeAreaView>
      )} />
  );
}

export function Action({ label, onPress, kind = "green", disabled = false }: {
  label: string;
  onPress?: () => void;
  kind?: "green" | "red" | "outline";
  disabled?: boolean;
}) {
  const inactive = disabled || !onPress;
  return (
    <Pressable accessibilityRole="button" accessibilityState={{ disabled: inactive }} disabled={inactive}
      onPress={onPress} style={({ pressed }) => [
        ui.action, kind === "red" && ui.redAction, kind === "outline" && ui.outlineAction,
        (pressed || inactive) && ui.faded,
      ]}>
      <Text style={[ui.actionText, kind === "outline" && ui.ink]}>{label}</Text>
    </Pressable>
  );
}

export function Panel({ children, tone = "paper" }: {
  children: ReactNode;
  tone?: "paper" | "forest" | "mustard" | "blush";
}) {
  return <View style={[ui.panel, tone === "forest" && ui.forest, tone === "mustard" && ui.mustard, tone === "blush" && ui.blush]}>{children}</View>;
}

export function Badge({ children, tone = "mustard" }: {
  children: ReactNode;
  tone?: "mustard" | "green" | "red";
}) {
  return <Text style={[ui.badge, tone === "green" && ui.greenBadge, tone === "red" && ui.redBadge]}>{children}</Text>;
}

export function Heading({ children }: { children: ReactNode }) {
  return <Text accessibilityRole="header" style={ui.heading}>{children}</Text>;
}

export function Body({ children }: { children: ReactNode }) {
  return <Text style={ui.body}>{children}</Text>;
}

export function Note({ children }: { children: ReactNode }) {
  return <Text style={ui.note}>{children}</Text>;
}

export function Field(props: TextInputProps) {
  return <TextInput placeholderTextColor={colors.muted} {...props} style={[ui.field, props.multiline && ui.multiline, props.style]} />;
}

export function Chips<T extends string>({ choices, value, onSelect }: {
  choices: readonly T[];
  value: T;
  onSelect: (value: T) => void;
}) {
  return (
    <View style={ui.chips}>
      {choices.map((choice) => (
        <Pressable key={choice} accessibilityRole="button" accessibilityState={{ selected: value === choice }}
          onPress={() => onSelect(choice)} style={[ui.chip, value === choice && ui.chipActive]}>
          <Text style={[ui.chipText, value === choice && ui.lightInk]}>{choice}</Text>
        </Pressable>
      ))}
    </View>
  );
}

export function Row({ title, detail, icon, onPress }: {
  title: string;
  detail?: string;
  icon: CreateIconName;
  onPress: () => void;
}) {
  return (
    <Pressable accessibilityRole="button" onPress={onPress} style={({ pressed }) => [ui.row, pressed && ui.faded]}>
      <View style={ui.rowIcon}><Icon name={icon} color={colors.forestDeep} size={20} /></View>
      <View style={ui.flex}>
        <Text style={ui.bold}>{title}</Text>
        {detail && <Note>{detail}</Note>}
      </View>
      <View style={ui.chevron}><Icon name="down" color={colors.muted} size={18} /></View>
    </Pressable>
  );
}

export function conceptSource(recipe: Pick<RecipeCase, "art">) {
  return recipe.art === "mac"
    ? require("@/assets/images/food-felonies/chocolate-mac.jpg")
    : require("@/assets/images/food-felonies/pickle-maple-rice.jpg");
}

export function ConceptArt({ recipe, square = false }: { recipe: RecipeCase; square?: boolean }) {
  const source = conceptSource(recipe);
  return <Image source={source} accessible accessibilityLabel={`AI concept for ${recipe.title}`}
    contentFit="cover" style={[ui.image, square && ui.square]} />;
}

export function ProofArt({ uri, label }: { uri: string; label: string }) {
  return <Image source={{ uri }} accessible accessibilityLabel={label} contentFit="cover" style={[ui.image, ui.square]} />;
}

export function ChefMark() {
  return (
    <View aria-hidden style={ui.mark}>
      <Svg width={76} height={68} viewBox="0 0 76 68">
        <Path d="M19 42C1 44 1 20 15 17 19 5 35 5 42 13 53 5 67 12 68 24 71 33 66 40 59 41L57 49 21 51Z"
          fill="#FFF9EF" stroke="#0B3829" strokeWidth={3.2} strokeLinejoin="round" />
        <Path d="M17 48 34 44 38 47 43 45 61 42 60 52 55 57 47 58 41 51 36 53 31 61 23 62 18 56Z"
          fill="#0B3829" stroke="#F5BA47" strokeWidth={2.5} strokeLinejoin="round" />
        <Path d="m22 52 8-3m17 1 8-3" stroke="#FFF9EF" strokeWidth={1.8} strokeLinecap="round" />
      </Svg>
    </View>
  );
}

export const ui = StyleSheet.create({
  shell: { flex: 1, backgroundColor: colors.forestDeep },
  lightShell: { backgroundColor: colors.canvas },
  frame: { flex: 1, width: "100%", maxWidth: 560, alignSelf: "center", backgroundColor: colors.canvas },
  header: {
    minHeight: 62, flexDirection: "row", alignItems: "center",
    paddingHorizontal: 10, paddingVertical: 6, backgroundColor: colors.forestDeep,
  },
  lightHeader: { backgroundColor: colors.canvas },
  headerTitle: { flex: 1, fontFamily: "Bricolage", fontSize: 25, color: colors.cream, textAlign: "center" },
  side: { width: 48, minHeight: 48, alignItems: "center", justifyContent: "center" },
  ink: { color: colors.ink },
  lightInk: { color: colors.cream },
  scroll: { flex: 1 },
  content: { paddingHorizontal: 16, paddingTop: 12, paddingBottom: 22, gap: 14 },
  footer: { paddingHorizontal: 12, paddingVertical: 5, borderTopWidth: 1, borderTopColor: colors.border },
  flex: { flex: 1, minWidth: 0 },
  rowLine: { flexDirection: "row", alignItems: "center", gap: 10 },
  wrap: { flexDirection: "row", flexWrap: "wrap", alignItems: "center", gap: 7 },
  panel: {
    padding: 15, gap: 9, borderRadius: 17, backgroundColor: colors.paper,
    borderWidth: 1, borderColor: colors.border, boxShadow: "0px 2px 5px rgba(73, 43, 14, 0.10)",
  },
  forest: { backgroundColor: colors.forestDeep, borderColor: colors.forestDeep },
  mustard: { backgroundColor: "#F9E5AE" },
  blush: { backgroundColor: colors.blush },
  title: { fontFamily: "Bricolage", fontSize: 35, lineHeight: 39, color: colors.forestDeep },
  heading: { fontFamily: "Bricolage", fontSize: 23, lineHeight: 27, color: colors.ink },
  body: { fontFamily: "DMSans", fontSize: 16, lineHeight: 22, color: colors.ink },
  bold: { fontFamily: "DMSansBold", fontSize: 16, color: colors.ink },
  note: { fontFamily: "DMSans", fontSize: 13, lineHeight: 18, color: colors.muted },
  redText: { color: colors.red },
  badge: {
    alignSelf: "flex-start", overflow: "hidden", borderRadius: 6, paddingHorizontal: 9,
    paddingVertical: 5, fontFamily: "DMSansBold", fontSize: 12, color: colors.ink, backgroundColor: "#F9E5AE",
  },
  greenBadge: { backgroundColor: colors.forestTint, color: colors.forestDeep },
  redBadge: { backgroundColor: colors.blush, color: colors.red },
  image: { width: "100%", aspectRatio: 1.58, borderRadius: 13, backgroundColor: colors.border },
  square: { aspectRatio: 1 },
  action: { minHeight: 48, padding: 10, borderRadius: 13, alignItems: "center", justifyContent: "center", backgroundColor: colors.forest },
  redAction: { backgroundColor: colors.red },
  outlineAction: { backgroundColor: colors.cream, borderWidth: 1, borderColor: colors.controlBorder },
  actionText: { fontFamily: "DMSansBold", fontSize: 16, color: colors.cream, textAlign: "center" },
  faded: { opacity: 0.63 },
  field: {
    minHeight: 48, paddingHorizontal: 11, paddingVertical: 9, borderRadius: 12, borderWidth: 1,
    borderColor: colors.controlBorder, backgroundColor: colors.cream, fontFamily: "DMSans", fontSize: 16, color: colors.ink,
  },
  multiline: { minHeight: 105, textAlignVertical: "top" },
  chips: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  chip: { minHeight: 44, paddingHorizontal: 13, paddingVertical: 7, borderRadius: 22, justifyContent: "center", backgroundColor: "#F0E4D2" },
  chipActive: { backgroundColor: colors.forestDeep },
  chipText: { fontFamily: "DMSansBold", fontSize: 14, color: colors.ink },
  row: { flexDirection: "row", alignItems: "center", gap: 10, minHeight: 56, paddingVertical: 4 },
  rowIcon: { width: 38, height: 38, alignItems: "center", justifyContent: "center", backgroundColor: colors.forestTint, borderRadius: 11 },
  chevron: { transform: [{ rotate: "-90deg" }] },
  mark: { width: 76, height: 68 },
});
