export type Dashboard = {
  counts: { applications: number; versions: number; analyses: number; findings: number; pending_findings: number; critical_findings: number; high_findings: number };
  analyses: { id: string; application_name: string; package_name: string; version_name?: string; state: string; created_at: string; finished_at?: string; finding_count: number }[];
  findings: { id: string; title: string; severity: string; priority: string; review_state: string; category: string; application_name: string; created_at: string }[];
};
