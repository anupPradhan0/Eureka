/**
 * A single repo statistic. Renders nothing when the value is unavailable
 * (null/undefined) so the UI only shows stats GitHub actually provided.
 */
export function StatBadge({
  label,
  value,
}: {
  label: string;
  value: number | null | undefined;
}) {
  if (value === null || value === undefined) return null;

  return (
    <div className="stat">
      <span className="stat__value">{value.toLocaleString()}</span>
      <span className="stat__label">{label}</span>
    </div>
  );
}
