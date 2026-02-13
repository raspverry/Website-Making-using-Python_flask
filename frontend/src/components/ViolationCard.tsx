import type { Violation } from '@/types';

interface ViolationCardProps {
  violation: Violation;
}

export function ViolationCard({ violation }: ViolationCardProps) {
  const severityColors: Record<string, string> = {
    critical: 'bg-red-50 text-red-700 border-red-200',
    serious: 'bg-orange-50 text-orange-700 border-orange-200',
    moderate: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    minor: 'bg-gray-50 text-gray-700 border-gray-200',
  };

  return (
    <div className={`rounded-lg border p-4 ${severityColors[violation.severity] || severityColors.minor}`}>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-medium">{violation.rule_name}</h3>
          <p className="text-sm mt-1 opacity-80">{violation.description}</p>
        </div>
        <span className="text-xs font-semibold uppercase px-2 py-0.5 rounded-full bg-white/50" aria-label={`Severity: ${violation.severity}`}>{violation.severity}</span>
      </div>
      {violation.wcag_criteria && (
        <p className="mt-2 text-xs font-medium opacity-70">WCAG {violation.wcag_criteria}</p>
      )}
      {violation.element_html && (
        <pre className="mt-3 text-xs bg-white/50 rounded p-2 overflow-x-auto">{violation.element_html}</pre>
      )}
      {violation.fix_suggestion && (
        <details className="mt-2">
          <summary className="text-xs font-medium cursor-pointer">View fix suggestion</summary>
          <p className="mt-1 text-sm bg-white/50 rounded p-2 whitespace-pre-line">{violation.fix_suggestion}</p>
        </details>
      )}
      {violation.page_url && <p className="mt-2 text-xs opacity-60 truncate">{violation.page_url}</p>}
    </div>
  );
}
