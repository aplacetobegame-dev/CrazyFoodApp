import { Pressable, StyleSheet, Text, View } from "react-native";
import { Icon, type CreateIconName } from "@/features/create/create-art";
import { colors } from "./food-felonies-theme";

const tabs = [
  { id: "discover", label: "Discover", icon: "compass" },
  { id: "create", label: "Create", icon: "plus" },
  { id: "cases", label: "My Cases", icon: "folder" },
  { id: "profile", label: "Profile", icon: "person" },
] as const satisfies readonly { id: string; label: string; icon: CreateIconName }[];

export type FoodTab = typeof tabs[number]["id"];

export function FoodTabs({ active, onSelect }: { active: FoodTab; onSelect?: (tab: FoodTab) => void }) {
  return (
    <View role="tablist" style={styles.tabs}>
      {tabs.map(({ id, label, icon }) => {
        const selected = id === active;
        return (
          <Pressable key={id} accessibilityRole="tab" aria-selected={selected}
            accessibilityState={{ selected, disabled: !selected && !onSelect }}
            disabled={selected || !onSelect} onPress={() => onSelect?.(id)}
            style={({ pressed }) => [styles.tab, (selected || pressed) && styles.active]}>
            <Icon name={icon} color={selected ? colors.forestDeep : colors.muted} size={23} />
            <Text style={[styles.label, selected && styles.activeLabel]}>{label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  tabs: { flexDirection: "row", gap: 4 },
  tab: {
    flex: 1, minHeight: 54, paddingVertical: 5, paddingHorizontal: 3,
    justifyContent: "center", alignItems: "center", gap: 3,
  },
  active: { backgroundColor: colors.forestTint, borderRadius: 18 },
  label: { fontFamily: "DMSansBold", fontSize: 12, color: colors.muted, textAlign: "center" },
  activeLabel: { color: colors.forestDeep },
});
