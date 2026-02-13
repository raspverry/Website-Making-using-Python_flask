import type { Violation } from '@/types';

const severityConfig: Record<string, { bg: string; badge: string; border: string }> = {
  critical: { bg: 'bg-red-50', badge: 'bg-red-100 text-red-700', border: 'border-red-200' },
  serious: { bg: 'bg-orange-50', badge: 'bg-orange-100 text-orange-700', border: 'border-orange-200' },
  moderate: { bg: 'bg-yellow-50', badge: 'bg-yellow-100 text-yellow-700', border: 'border-yellow-200' },
  minor: { bg: 'bg-gray-50', badge: 'bg-gray-100 text-gray-600', border: 'border-gray-200' },
};

export function ViolationCard({ violation }: { violation: Violation }) {
  const config = severityConfig[violation.severity] || severityConfig.minor;

  return (
    <div className={`rounded-xl border ${config.border} ${config.bg} p-5 transition-colors hover:shadow-sm`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-gray-900">{violation.rule_name}</h3>
          <p className="text-sm text-gray-600 mt-1 leading-relaxed">{violation.description}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {violation.wcag_criteria && (
            <span className="text-xs font-mono text-gray-400 bg-white px-2 py-0.5 rounded border border-gray-200">
              {violation.wcag_criteria}
            </span>
          )}
          <span
            className={`text-xs font-semibold uppercase px-2.5 py-1 rounded-lg ${config.badge}`}
            aria-label={`Severity: ${violation.severity}`}
          >
            {violation.severity}
          </span>
        </div>
      </div>

      {violation.element_html && (
        <pre className="mt-3 text-xs font-mono bg-white/70 border border-gray-200/50 rounded-lg p-3 overflow-x-auto max-h-24 text-gray-700">
          {violation.element_html}
        </pre>
      )}

      {violation.fix_suggestion && (
        <details className="mt-3 group">
          <summary className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 cursor-pointer hover:text-blue-700 transition-colors">
            <svg className="w-3.5 h-3.5 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            View fix suggestion
          </summary>
          <div className="mt-2 text-sm bg-white/70 border border-green-200/50 rounded-lg p-3 text-gray-700 whitespace-pre-line leading-relaxed">
            {violation.fix_suggestion}
          </div>
        </details>
      )}

      {violation.page_url && (
        <p className="mt-3 text-xs text-gray-400 truncate">
          <span className="font-medium">Page:</span> {violation.page_url}
        </p>
      )}
    </div>
  );
}
