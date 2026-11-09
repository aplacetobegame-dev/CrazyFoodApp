import { colors } from "@/components/food-felonies-theme";
import type { WeirdnessSliderProps } from "./weirdness-slider";

export function WeirdnessSlider({ value, onChange }: WeirdnessSliderProps) {
  return (
    <input
      aria-label="Weirdness level"
      type="range"
      min={0}
      max={100}
      step={1}
      value={value}
      onChange={(event) => onChange(event.currentTarget.valueAsNumber)}
      style={{ width: "100%", minHeight: 34, margin: 0, accentColor: colors.red }}
    />
  );
}
