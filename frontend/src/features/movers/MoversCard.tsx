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
      .filter((e) => e.priceDeltaPct > 0)
      .sort((a, b) => b.priceDeltaPct - a.priceDeltaPct);
  }

  if (variant === "losers") {
    return entries
      .filter((e) => e.priceDeltaPct < 0)
      .sort((a, b) => a.priceDeltaPct - b.priceDeltaPct);
  }

  return entries
    .filter((e) => e.volumeDeltaPct !== 0)
    .sort((a, b) => b.volumeDeltaPct - a.volumeDeltaPct);
}

function formatValue(
  entry: PriceVolumeEntry,
  variant: MoversVariant,
): { text: string; className: string } {
  if (variant === "gainers") {
    return { text: `+${entry.priceDeltaPct}%`, className: "pos" };
  }

  if (variant === "losers") {
    return { text: `${entry.priceDeltaPct}%`, className: "neg" };
  }

  return { text: `${entry.volumeDeltaPct}%`, className: "vol-pct" };
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
                key={entry.symbol}
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
