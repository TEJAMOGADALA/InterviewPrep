import { cn } from '@/lib/utils';

/**
 * Filter row for the Knowledge Base tree.
 *
 * Filters are pure client-side; they don't refetch anything. The parent
 * owns the `active` state and calls `onToggle(key)` to add/remove filters.
 *
 * Groups:
 *   - status: completed / incomplete / revision_due / bookmarked / favorite
 *   - difficulty: easy / medium / hard
 *   - company: <company-id list from the roadmap tree>
 */
const STATUS_FILTERS = [
  { key: 'completed',     label: 'Completed' },
  { key: 'incomplete',    label: 'Incomplete' },
  { key: 'revision_due',  label: 'Revision Due' },
  { key: 'bookmarked',    label: 'Bookmarked' },
  { key: 'favorite',      label: 'Favorite' },
];

const DIFFICULTY_FILTERS = [
  { key: 'easy',   label: 'Easy' },
  { key: 'medium', label: 'Medium' },
  { key: 'hard',   label: 'Hard' },
];

const COMPANY_LABEL = {
  google: 'Google', microsoft: 'Microsoft', atlassian: 'Atlassian', uber: 'Uber',
  adobe: 'Adobe', linkedin: 'LinkedIn', stripe: 'Stripe', salesforce: 'Salesforce',
  oracle: 'Oracle', phonepe: 'PhonePe', flipkart: 'Flipkart', paypal: 'PayPal',
  goldman_sachs: 'Goldman Sachs', zoho: 'Zoho',
};

function Chip({ active, onClick, testId, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      data-testid={testId}
      aria-pressed={active}
      className={cn(
        'inline-flex items-center gap-1 px-2.5 py-1 rounded-full border text-[11px] font-mono uppercase tracking-wider transition-colors',
        active
          ? 'bg-primary/15 border-primary/40 text-primary'
          : 'bg-white/[0.03] border-white/[0.08] text-muted-foreground hover:text-foreground hover:border-white/20',
      )}
    >
      {children}
    </button>
  );
}

export function FilterChips({ active = new Set(), companies = [], onToggle, onClear }) {
  const hasAny = active.size > 0;
  return (
    <div className="flex flex-wrap items-center gap-2" data-testid="filter-chips">
      <div className="flex flex-wrap gap-1.5" data-testid="filter-chips-status">
        {STATUS_FILTERS.map((f) => (
          <Chip
            key={f.key}
            active={active.has(`status:${f.key}`)}
            onClick={() => onToggle(`status:${f.key}`)}
            testId={`filter-status-${f.key}`}
          >
            {f.label}
          </Chip>
        ))}
      </div>
      <div className="h-4 w-px bg-white/[0.08]" />
      <div className="flex flex-wrap gap-1.5" data-testid="filter-chips-difficulty">
        {DIFFICULTY_FILTERS.map((f) => (
          <Chip
            key={f.key}
            active={active.has(`difficulty:${f.key}`)}
            onClick={() => onToggle(`difficulty:${f.key}`)}
            testId={`filter-difficulty-${f.key}`}
          >
            {f.label}
          </Chip>
        ))}
      </div>
      {companies.length > 0 && (
        <>
          <div className="h-4 w-px bg-white/[0.08]" />
          <div className="flex flex-wrap gap-1.5" data-testid="filter-chips-company">
            {companies.map((cid) => (
              <Chip
                key={cid}
                active={active.has(`company:${cid}`)}
                onClick={() => onToggle(`company:${cid}`)}
                testId={`filter-company-${cid}`}
              >
                {COMPANY_LABEL[cid] || cid}
              </Chip>
            ))}
          </div>
        </>
      )}
      {hasAny && (
        <button
          type="button"
          onClick={onClear}
          data-testid="filter-chips-clear"
          className="ml-auto text-[11px] text-muted-foreground hover:text-foreground"
        >
          Clear all
        </button>
      )}
    </div>
  );
}
