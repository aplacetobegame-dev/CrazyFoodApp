import { View } from "react-native";
import Svg, { Circle, G, Path, Rect } from "react-native-svg";

const paths = {
  back: "M20 12H4m7 7-7-7 7-7",
  bowl: "M3 12h18c0 4.5-3.6 8-8 8h-2c-4.4 0-8-3.5-8-8Zm3 0 2-4 3 2m0 2 2-6 4 2 2 4M8 22h8",
  exclude: "M5 5l14 14M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z",
  people: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-3.9M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7-7.9a4 4 0 0 1 0 7.8",
  clock: "M12 6v6l4 2m6-2a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z",
  pan: "M3 12h13a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Zm13 0 5-5M7 8V6m4 2V6",
  flask: "M9 3h6m-5 0v7l-5 8a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-8V3m-6 13h8",
  options: "M3 6h4m4 0h10M3 12h10m4 0h4M3 18h4m4 0h10M7 4v4m6 2v4m-6 2v4",
  down: "m6 9 6 6 6-6",
  up: "m6 15 6-6 6 6",
  plus: "M12 8v8m-4-4h8m6 0a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z",
  compass: "m16 8-2 6-6 2 2-6 6-2Zm6 4a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z",
  folder: "M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z",
  person: "M4 21v-2a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v2ZM16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z",
  close: "m6 6 12 12M18 6 6 18",
  camera: "M3 8h4l2-3h6l2 3h4v12H3Zm13 6a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z",
  search: "M16 16l5 5m-3-10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z",
  share: "M12 15V3m-4 4 4-4 4 4M5 12v8h14v-8",
  lock: "M7 10V7a5 5 0 0 1 10 0v3M5 10h14v11H5Zm7 5v2",
  spark: "M12 2c0 6-3 9-9 10 6 1 9 4 9 10 0-6 3-9 9-10-6-1-9-4-9-10Z",
} as const;

export type CreateIconName = keyof typeof paths;

export function Icon({ name, color, size = 22 }: {
  name: CreateIconName;
  color: string;
  size?: number;
}) {
  return (
    <View aria-hidden pointerEvents="none">
      <Svg width={size} height={size} viewBox="0 0 24 24">
        <Path d={paths[name]} fill="none" stroke={color} strokeWidth={1.75}
          strokeLinecap="round" strokeLinejoin="round" />
      </Svg>
    </View>
  );
}

export function ClipboardClip() {
  return (
    <View aria-hidden pointerEvents="none">
      <Svg width={78} height={46} viewBox="0 0 78 46">
        <G transform="rotate(-7 39 29)">
          <Path d="M8 38h62v5H8z" fill="#282D22" />
          <Path d="M8 38v-7a6 6 0 0 1 6-6h13v-9a12 12 0 0 1 24 0v9h13a6 6 0 0 1 6 6v7Z"
            fill="#B4AA8E" stroke="#D6CAB0" strokeWidth={1.4} />
          <Circle cx={39} cy={15} r={5.5} fill="#133D2D" />
          <Path d="M13 34h52" stroke="#DCD0B4" strokeWidth={1.4} strokeLinecap="round" />
        </G>
      </Svg>
    </View>
  );
}

export function GinghamCorner() {
  return (
    <View aria-hidden pointerEvents="none">
      <Svg width={104} height={104} viewBox="0 0 104 104">
        <G transform="rotate(45 70 45)">
          <Rect x={39} y={0} width={80} height={80} fill="#FAE6CB" />
          <Path d="M47 0v80m32-80v80m32-80v80M39 8h80M39 40h80M39 72h80"
            stroke="#C54239" strokeWidth={16} opacity={0.62} />
          <Path d="M39 8h16m16 0h16m16 0h16M39 40h16m16 0h16m16 0h16M39 72h16m16 0h16m16 0h16"
            stroke="#AA2B26" strokeWidth={16} opacity={0.7} />
        </G>
      </Svg>
    </View>
  );
}

export function StampMarks() {
  return (
    <View aria-hidden pointerEvents="none">
      <Svg width={34} height={38} viewBox="0 0 34 38">
        <Path d="m5 13 7-9m1 17 16-8M15 29l14 3" stroke="#AD2925"
          strokeWidth={4} strokeLinecap="round" />
      </Svg>
    </View>
  );
}
