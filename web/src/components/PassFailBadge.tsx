interface PassFailBadgeProps {
  passed: boolean;
  margin?: number;
}

export default function PassFailBadge({ passed, margin }: PassFailBadgeProps) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide"
      style={{
        backgroundColor: passed
          ? "rgba(19, 136, 8, 0.1)"
          : "rgba(220, 38, 38, 0.1)",
        color: passed ? "var(--green)" : "#DC2626",
        border: `1px solid ${passed ? "rgba(19, 136, 8, 0.2)" : "rgba(220, 38, 38, 0.2)"}`,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: passed ? "var(--green)" : "#DC2626" }}
      />
      {passed ? "Pass" : "Fail"}
      {margin !== undefined && (
        <span className="font-normal" style={{ opacity: 0.7 }}>
          ({margin > 0 ? "+" : ""}
          {margin.toFixed(1)})
        </span>
      )}
    </span>
  );
}
