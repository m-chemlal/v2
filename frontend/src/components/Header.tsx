interface HeaderProps {
  title: string;
  version: string;
}

export function Header({ title, version }: HeaderProps) {
  return (
    <header className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-3xl font-semibold">{title}</h1>
        <p className="text-sm text-gray-400">Autonomous & Explainable SOC Prototype</p>
      </div>
      <div className="px-3 py-1 rounded-full bg-accent/20 text-accent text-sm font-medium">
        v{version}
      </div>
    </header>
  );
}
