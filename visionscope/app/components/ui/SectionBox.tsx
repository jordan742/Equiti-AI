interface SectionBoxProps {
  title: string;
  tag?: string;
  children: React.ReactNode;
  className?: string;
  info?: string;
}

export default function SectionBox({ title, tag, children, className = "", info }: SectionBoxProps) {
  return (
    <div className={`rounded-lg overflow-hidden ${className}`}
      style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="flex items-center justify-between px-4 py-3"
        style={{ background: "#0c1220", borderBottom: "1px solid #1e2d4a" }}>
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold uppercase tracking-widest" style={{ color: "#8899bb" }}>
            {title}
          </span>
          {tag && (
            <span className="font-mono text-xs px-2 py-0.5 rounded uppercase"
              style={{ background: "rgba(46,108,246,0.15)", color: "#2e6cf6", border: "1px solid rgba(46,108,246,0.3)" }}>
              {tag}
            </span>
          )}
        </div>
        {info && <span className="text-xs" style={{ color: "#4a5a7a" }}>{info}</span>}
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}
