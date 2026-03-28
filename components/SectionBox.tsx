export default function SectionBox({ title, tag, children, info }: {
  title: string; tag?: string; children: React.ReactNode; info?: string;
}) {
  return (
    <div className="rounded-xl overflow-hidden" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
      <div className="px-4 py-3 flex items-center justify-between" style={{ background: "#0a0e17", borderBottom: "1px solid #1b2540" }}>
        <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "#c4cde0" }}>{title}</span>
        {tag && <span className="font-mono text-xs" style={{ color: "#4e5f7d" }}>{tag}</span>}
      </div>
      {info && (
        <div className="px-4 py-2.5" style={{ background: "#06b6d411", borderBottom: "1px solid #06b6d422" }}>
          <p className="text-xs leading-relaxed" style={{ color: "#06b6d4" }}>{info}</p>
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
