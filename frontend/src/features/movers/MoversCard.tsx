import { useSignalsStore } from "../../store/useSignalsStore";
import type { PriceVolumeEntry } from "../../types/priceVolume";
import { MoverRow } from "./MoverRow";

type MoversVariant = "gainers" | "losers" | "volume";

type MoversCardProps = {
  title: string;
  variant: MoversVariant;
};

function getSortedEntries(
  entries: PriceVolumeEntry[],
  variant: MoversVariant,
): PriceVolumeEntry[] {
  if (variant === "gainers") {
    return entries
      .filter((e) => e.price_delta_pct > 0)
      .sort((a, b) => b.price_delta_pct - a.price_delta_pct);
  }

  if (variant === "losers") {
    return entries
      .filter((e) => e.price_delta_pct < 0)
      .sort((a, b) => a.price_delta_pct - b.price_delta_pct);
  }

  return entries
    .filter((e) => e.volume_delta_pct !== 0)
    .sort((a, b) => b.volume_delta_pct - a.volume_delta_pct);
}

function formatValue(
  entry: PriceVolumeEntry,
  variant: MoversVariant,
): { text: string; className: string } {
  if (variant === "gainers") {
    return { text: `+${entry.price_delta_pct}%`, className: "pos" };
  }

  if (variant === "losers") {
    return { text: `${entry.price_delta_pct}%`, className: "neg" };
  }

  return { text: `${entry.volume_delta_pct}%`, className: "vol-pct" };
}

export function MoversCard({ title, variant }: MoversCardProps) {
  const priceVolume = useSignalsStore((s) => s.priceVolume);

  const entries = priceVolume ? getSortedEntries(priceVolume, variant) : [];

  return (
    <div className="card movers-card">
      <div className="card-header">{title}</div>
      <div className="mover-list">
        {priceVolume === null ? (
          <div className="corr-loading">Ожидание данных...</div>
        ) : (
          entries.map((entry, i) => {
            const { text, className } = formatValue(entry, variant);
            return (
              <MoverRow
                index={i}
                symbol={entry.symbol}
                value={text}
                valueClassName={className}
              />
            );
          })
        )}
      </div>
    </div>
  );
}
