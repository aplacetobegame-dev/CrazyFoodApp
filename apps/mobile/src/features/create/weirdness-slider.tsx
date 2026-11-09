import Slider from "@react-native-community/slider";
import { colors } from "@/components/food-felonies-theme";

export type WeirdnessSliderProps = {
  initialValue: number;
  value: number;
  onChange: (value: number) => void;
};

export function WeirdnessSlider({ initialValue, value, onChange }: WeirdnessSliderProps) {
  return (
    <Slider
      accessibilityLabel="Weirdness level"
      accessibilityHint="Ranges from Normal to Food Felony"
      accessibilityValue={{ min: 0, max: 100, now: value }}
      minimumValue={0}
      maximumValue={100}
      step={1}
      value={initialValue}
      minimumTrackTintColor={colors.red}
      maximumTrackTintColor={colors.track}
      thumbTintColor={colors.red}
      onValueChange={onChange}
      style={{ width: "100%", height: 34 }}
    />
  );
}
