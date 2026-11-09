import { BricolageGrotesque_700Bold } from "@expo-google-fonts/bricolage-grotesque/700Bold";
import { DMSans_400Regular } from "@expo-google-fonts/dm-sans/400Regular";
import { DMSans_700Bold } from "@expo-google-fonts/dm-sans/700Bold";
import { useFonts } from "expo-font";

export function useFoodFonts() {
  const [loaded, error] = useFonts({
    Bricolage: BricolageGrotesque_700Bold,
    DMSans: DMSans_400Regular,
    DMSansBold: DMSans_700Bold,
  });
  return loaded || Boolean(error);
}
