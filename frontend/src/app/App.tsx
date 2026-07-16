import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import {
  LayoutDashboard, BookOpen, BarChart2, Bell, Calendar,
  Settings, Github, ChevronRight, Eye, EyeOff,
  FileText, FileImage, FileArchive, File, LogOut, Trash2,
  AlertTriangle, X, Menu, ExternalLink, Download, User,
  Sun, Moon, Monitor, RefreshCw, WifiOff, Search, ChevronDown,
  Lock, HelpCircle, MessageSquare, Cpu, Copy, Check,
  Link, Layers, ArrowUpDown, FileDown
} from "lucide-react";

// ─── Config ───────────────────────────────────────────────────────────────────

const API_BASE: string = (() => {
  const env = (import.meta as Record<string, any>).env?.VITE_API_BASE_URL;
  return typeof env === "string" && env.length > 0 ? env.replace(/\/$/, "") : window.location.origin;
})();

const SESSION_KEY    = "mydy_session";
const KEYS_KEY       = "mydy_keys";
const DISPLAY_KEY    = "mydy_display_name";
const THEME_KEY      = "mydy_theme";
const SESSION_EXPIRED = "mydy:session-expired";

// ─── Session helpers ──────────────────────────────────────────────────────────

interface SessionData { user_id: string; session_token: string; session_key: string; }
interface KeysData    { web_service_key: string; features_service_key: string; service_key: string; }

function getSession(): SessionData | null {
  try { return JSON.parse(localStorage.getItem(SESSION_KEY) ?? "null"); } catch { return null; }
}
function getKeys(): KeysData | null {
  try { return JSON.parse(localStorage.getItem(KEYS_KEY) ?? "null"); } catch { return null; }
}
function getDisplayName(): string {
  try { return localStorage.getItem(DISPLAY_KEY) ?? ""; } catch { return ""; }
}
function isAuthenticated(): boolean {
  const s = getSession(); const k = getKeys();
  return !!(s?.user_id && s?.session_token && s?.session_key && k?.features_service_key);
}
function clearAll() {
  const theme = localStorage.getItem(THEME_KEY);
  localStorage.clear();
  if (theme) localStorage.setItem(THEME_KEY, theme);
}

// ─── API client ───────────────────────────────────────────────────────────────
// X-User-Id replaces ?user_id query param for all authenticated endpoints.

function needsApiKey(path: string): boolean {
  if (!path.startsWith("/v1/")) return false;
  if (path.startsWith("/v1/user/keys")) return false;
  if (path.startsWith("/v1/auth/logout")) return false;
  return true;
}

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const session = getSession(); const keys = getKeys();
  const headers: Record<string, string> = { ...(options.headers as Record<string, string> ?? {}) };
  if (session) {
    headers["Authorization"] = `Bearer ${session.session_token}`;
    headers["X-User-Id"]     = session.user_id;
  }
  if (needsApiKey(path) && keys) headers["X-API-Key"] = keys.features_service_key;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401 || res.status === 403) {
    clearAll();
    window.dispatchEvent(new CustomEvent(SESSION_EXPIRED));
  }
  return res;
}

async function extractError(res: Response): Promise<string> {
  try {
    const j = await res.json();
    return j.detail ?? j.message ?? j.error ?? `Request failed (${res.status})`;
  } catch { return `Request failed (${res.status})`; }
}

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await apiFetch(path);
  if (!res.ok) throw new Error(await extractError(res));
  return res.json();
}

// ─── Auth API ─────────────────────────────────────────────────────────────────

async function apiLogin(username: string, password: string): Promise<SessionData> {
  const res = await fetch(
    `${API_BASE}/v1/auth/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    { method: "POST" }
  );
  if (!res.ok) throw new Error(await extractError(res));
  return res.json();
}

async function apiFetchKeys(session_token: string, session_key: string): Promise<KeysData> {
  const res = await fetch(
    `${API_BASE}/v1/user/keys?session_key=${encodeURIComponent(session_key)}`,
    { headers: { Authorization: `Bearer ${session_token}` } }
  );
  if (!res.ok) throw new Error(await extractError(res));
  return res.json();
}

async function performLogout(): Promise<void> {
  const session = getSession();
  if (session) {
    try { await apiFetch(`/v1/auth/logout?session_key=${encodeURIComponent(session.session_key)}`); } catch {}
  }
  clearAll();
}

async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
    return res.ok;
  } catch { return false; }
}

// ─── Resource URL helpers ─────────────────────────────────────────────────────

function buildResourceUrl(rawUrl: string, forceDownload: boolean): string {
  if (!rawUrl || rawUrl === "#") return "#";
  const keys = getKeys();
  try {
    const u = new URL(rawUrl);
    if (keys?.web_service_key) u.searchParams.set("token", keys.web_service_key);
    u.searchParams.set("forcedownload", forceDownload ? "1" : "0");
    return u.toString();
  } catch { return rawUrl; }
}

// ─── Types ───────────────────────────────────────────────────────────────────

type View = "login" | "dashboard" | "courses" | "courseDetail" | "attendance" | "announcements" | "calendar" | "profile" | "settings";
type Theme = "light" | "dark" | "system";
type ModuleCategory = "file" | "url" | "page" | "quiz";
type DocFileType = "pdf" | "docx" | "pptx" | "office" | "img" | "zip" | "other";

interface ApiCourse       { [k: string]: unknown; }
interface ApiDoc          { [k: string]: unknown; }
interface ApiModule       { [k: string]: unknown; }
interface ApiWeek         { [k: string]: unknown; }
interface ApiAttendance   { [k: string]: unknown; }
interface ApiAnnouncement { [k: string]: unknown; }
interface ApiCalendarEvent{ [k: string]: unknown; }

interface FlatModule {
  weekTitle: string;
  weekOrder: number;
  moduleId: string;
  moduleTitle: string;
  moduleType: string;
  moduleCategory: ModuleCategory;
  primaryDoc: ApiDoc | null;
  allDocs: ApiDoc[];
}

interface ViewerState {
  open: boolean;
  url: string;
  downloadUrl: string;
  title: string;
  fileType: DocFileType;
}

// ─── Accessor helpers ─────────────────────────────────────────────────────────

function courseId(c: ApiCourse): string  { return String(c.id ?? c.course_id ?? ""); }
function courseName(c: ApiCourse): string { return String(c.sub_title ?? c.course_name ?? c.subject_name ?? ""); }
function courseCode(c: ApiCourse): string { return String(c.sub_code ?? c.subject_code ?? c.course_code ?? ""); }
function courseTeacher(c: ApiCourse): string | undefined {
  const v = c.instructor_name ?? c.teacher_name; return v != null ? String(v) : undefined;
}
function courseSemTitle(c: ApiCourse): string | undefined {
  const v = c.sem_title ?? c.semester; return v != null ? String(v) : undefined;
}
function courseSemPeriod(c: ApiCourse): string | undefined {
  const v = c.sem_period; return v != null ? String(v) : undefined;
}

function weekId(w: ApiWeek): string    { return String(w.week_id ?? w.id ?? Math.random()); }
function weekLabel(w: ApiWeek): string { return String(w.week_title ?? w.week_label ?? w.label ?? `Week ${w.week_number ?? ""}`.trim()); }
function weekModules(w: ApiWeek): ApiModule[] { return (w.modules as ApiModule[]) ?? []; }

function moduleId(m: ApiModule): string    { return String(m.module_id ?? m.id ?? Math.random()); }
function moduleTitle(m: ApiModule): string { return String(m.module_title ?? m.title ?? "Module"); }
function moduleType(m: ApiModule): string  { return String(m.module_type ?? "resource"); }
function moduleDocs(m: ApiModule): ApiDoc[] { return (m.docs as ApiDoc[]) ?? (m.documents as ApiDoc[]) ?? []; }

function classifyModule(type: string): ModuleCategory {
  const t = type.toLowerCase();
  if (t === "url" || t === "link") return "url";
  if (t === "quiz") return "quiz";
  if (t === "page" || t === "lesson") return "page";
  return "file";
}

function docId(d: ApiDoc): string    { return String(d.doc_id ?? d.id ?? Math.random()); }
function docTitle(d: ApiDoc): string { return String(d.doc_title ?? d.title ?? ""); }
function docFileType(d: ApiDoc): DocFileType {
  const raw = docTitle(d);
  const ext = raw.split(".").pop()?.toLowerCase() ?? String(d.doc_type ?? "").toLowerCase();
  if (ext === "pdf")  return "pdf";
  if (["docx", "doc"].includes(ext)) return "docx";
  if (["pptx", "ppt"].includes(ext)) return "pptx";
  if (["xlsx", "xls"].includes(ext)) return "office";
  if (["png", "jpg", "jpeg", "gif"].includes(ext)) return "img";
  if (["zip", "rar"].includes(ext)) return "zip";
  return "other";
}
function docSize(d: ApiDoc): string {
  const s = d.doc_size ?? d.size ?? d.file_size;
  if (typeof s === "number") {
    if (s > 1024 * 1024) return `${(s / (1024 * 1024)).toFixed(1)} MB`;
    if (s > 1024) return `${Math.round(s / 1024)} KB`;
    return `${s} B`;
  }
  return s != null ? String(s) : "";
}
function docTeacher(d: ApiDoc): string { return String(d.teacher_name ?? d.teacher ?? ""); }
function docDate(d: ApiDoc): string {
  const ts = d.modified_at ?? d.created_at ?? d.date;
  if (typeof ts === "number") return formatUnix(ts);
  return ts != null ? String(ts) : "";
}
function docTimestamp(d: ApiDoc): number {
  const ts = d.modified_at ?? d.created_at;
  return typeof ts === "number" ? ts : 0;
}
function docUrl(d: ApiDoc): string { return String(d.doc_url ?? d.url ?? "#"); }

function attCode(a: ApiAttendance): string  { return String(a.classcode ?? a.subject_code ?? ""); }
function attTotal(a: ApiAttendance): number { return Number(a.totalclass ?? a.total_classes ?? 0); }
function attPresent(a: ApiAttendance): number { return Number(a.total_present ?? a.attended_classes ?? 0); }
function attAbsent(a: ApiAttendance): number  { return Number(a.total_absent ?? a.absent_classes ?? 0); }
function attPct(a: ApiAttendance): number {
  if (typeof a.presentage === "number") return Math.round(a.presentage);
  const t = attTotal(a); if (!t) return 0;
  return Math.round((attPresent(a) / t) * 100);
}

function annId(a: ApiAnnouncement): string     { return String(a.id ?? a.announcement_id ?? Math.random()); }
function annTitle(a: ApiAnnouncement): string  { return String(a.title ?? a.subject ?? "Announcement"); }
function annAuthor(a: ApiAnnouncement): string { return String(a.author ?? a.author_name ?? ""); }
function annDate(a: ApiAnnouncement): string {
  const v = a.created_at ?? a.date;
  if (typeof v === "number") return formatUnix(v);
  return v != null ? String(v) : "";
}
function annBodyText(a: ApiAnnouncement): string {
  return stripHTML(String(a.message ?? a.body ?? a.content ?? ""));
}

function evId(e: ApiCalendarEvent): string    { return String(e.id ?? e.event_id ?? Math.random()); }
function evTitle(e: ApiCalendarEvent): string { return String(e.event_title ?? e.title ?? "Event"); }
function evDate(e: ApiCalendarEvent): string {
  const v = e.date ?? e.event_date;
  if (typeof v === "number") return formatUnix(v);
  return v != null ? String(v) : "";
}
function evTimestamp(e: ApiCalendarEvent): number {
  const v = e.date ?? e.event_date;
  return typeof v === "number" ? v : 0;
}
function evType(e: ApiCalendarEvent): "exam" | "holiday" | "event" | "deadline" {
  const t = String(e.type ?? e.event_type ?? "").toLowerCase();
  if (t.includes("exam") || t.includes("test")) return "exam";
  if (t.includes("holiday") || t.includes("break")) return "holiday";
  if (t.includes("deadline") || t.includes("submission")) return "deadline";
  return "event";
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function formatUnix(ts: number): string {
  return new Date(ts * 1000).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function stripHTML(html: string): string {
  return html
    .replace(/<br\s*\/?>/gi, "\n").replace(/<\/p>/gi, "\n").replace(/<\/div>/gi, "\n")
    .replace(/<\/li>/gi, "\n").replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, "\n\n").trim();
}

function flattenCourseWeeks(weeks: ApiWeek[]): FlatModule[] {
  return weeks.flatMap((week, wi) =>
    weekModules(week).map(mod => {
      const docs = moduleDocs(mod);
      const mt = moduleType(mod);
      return {
        weekTitle: weekLabel(week),
        weekOrder: wi,
        moduleId: moduleId(mod),
        moduleTitle: moduleTitle(mod),
        moduleType: mt,
        moduleCategory: classifyModule(mt),
        primaryDoc: docs[0] ?? null,
        allDocs: docs,
      } satisfies FlatModule;
    })
  );
}

const GITHUB_URL      = "https://github.com/viraj-sh/mydylms-client";
const GITHUB_LABEL    = "github.com/viraj-sh/mydylms-client";
const UNICLARE_WEB    = "https://uniclare-client.netlify.app";
const UNICLARE_GITHUB = "https://github.com/viraj-sh/uniclare-client";

const MCP_TOOLS = [
  "get_user_profile", "get_user_profile_detailed", "get_current_semester_courses",
  "get_enrolled_courses", "get_course_docs", "get_calendar_events",
  "get_all_announcements", "fetch_latest_annoucements", "get_attendance",
];

function eventTypeColor(type: ReturnType<typeof evType>) {
  if (type === "exam")     return "bg-[#9f1c33] text-white";
  if (type === "holiday")  return "bg-emerald-600 text-white";
  if (type === "deadline") return "bg-amber-500 text-white";
  return "bg-[#217a94] text-white";
}
function eventTypeLabel(type: ReturnType<typeof evType>) {
  if (type === "exam")     return "Exam";
  if (type === "holiday")  return "Holiday";
  if (type === "deadline") return "Deadline";
  return "Event";
}

function moduleTypeIcon(type: string) {
  const t = type.toLowerCase();
  const cls = "w-3.5 h-3.5";
  if (t === "quiz")                       return <HelpCircle className={cls} />;
  if (t === "url" || t === "link")        return <Link className={cls} />;
  if (t === "page" || t === "lesson")     return <FileText className={cls} />;
  if (t === "presentation")               return <Layers className={cls} />;
  if (t === "forum")                      return <MessageSquare className={cls} />;
  if (t === "assignment")                 return <FileDown className={cls} />;
  return <File className={cls} />;
}

function moduleTypeBadge(type: string): string {
  const t = type.toLowerCase();
  if (t === "quiz")         return "bg-orange-100 text-orange-700 dark:bg-orange-950/30 dark:text-orange-400";
  if (t === "url" || t === "link") return "bg-[#217a94]/10 text-[#217a94] dark:text-[#3a9ab8]";
  if (t === "page" || t === "lesson") return "bg-purple-100 text-purple-700 dark:bg-purple-950/30 dark:text-purple-400";
  if (t === "presentation") return "bg-blue-100 text-blue-700 dark:bg-blue-950/30 dark:text-blue-400";
  if (["dyquestion", "questionpaper"].includes(t)) return "bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400";
  return "bg-muted text-muted-foreground";
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "dark") root.classList.add("dark");
  else if (theme === "light") root.classList.remove("dark");
  else window.matchMedia("(prefers-color-scheme: dark)").matches
    ? root.classList.add("dark") : root.classList.remove("dark");
}

function docIconEl(ft: DocFileType) {
  const cls = "w-4 h-4 shrink-0";
  if (ft === "pdf")           return <FileText className={cls} />;
  if (ft === "img")           return <FileImage className={cls} />;
  if (ft === "zip")           return <FileArchive className={cls} />;
  if (ft === "docx")          return <FileText className={cls} />;
  if (ft === "pptx")          return <Layers className={cls} />;
  if (ft === "office")        return <FileText className={cls} />;
  return <File className={cls} />;
}

// ─── Health hook ──────────────────────────────────────────────────────────────

function useHealth() {
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      if (cancelled) return;
      const ok = await checkHealth();
      if (cancelled) return;
      setHealthy(ok);
      timerRef.current = setTimeout(run, ok ? 90_000 : 30_000);
    }
    run();
    const onVisible = () => {
      if (document.hidden) return;
      if (timerRef.current) clearTimeout(timerRef.current);
      run();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, []);

  return healthy;
}

// ─── Async state hook ─────────────────────────────────────────────────────────

type AsyncState<T> = { status: "loading" | "success" | "error"; data: T | null; error: string | null };

function useAsync<T>(fetcher: () => Promise<T>, deps: React.DependencyList): [AsyncState<T>, () => void] {
  const [state, setState] = useState<AsyncState<T>>({ status: "loading", data: null, error: null });
  const retryCount = useRef(0);
  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading", data: null, error: null });
    fetcher()
      .then(data => { if (!cancelled) setState({ status: "success", data, error: null }); })
      .catch(err  => { if (!cancelled) setState({ status: "error", data: null, error: String(err?.message ?? err) }); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, retryCount.current]);
  const retry = useCallback(() => { retryCount.current += 1; setState({ status: "loading", data: null, error: null }); }, []);
  return [state, retry];
}

// ─── Primitive Components ─────────────────────────────────────────────────────

function Spinner({ size = "sm" }: { size?: "sm" | "md" }) {
  const s = size === "sm" ? "w-4 h-4" : "w-6 h-6";
  return (
    <svg className={`${s} animate-spin`} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}
function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 py-3 px-4">
      <div className="h-4 w-20 bg-muted rounded animate-pulse" />
      <div className="h-4 flex-1 bg-muted rounded animate-pulse" />
      <div className="h-4 w-14 bg-muted rounded animate-pulse" />
    </div>
  );
}
function SkeletonCard() {
  return (
    <div className="bg-card border border-border rounded p-4 space-y-2">
      <div className="h-3 w-16 bg-muted rounded animate-pulse" />
      <div className="h-4 w-full bg-muted rounded animate-pulse" />
      <div className="h-3 w-28 bg-muted rounded animate-pulse" />
    </div>
  );
}
function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 py-10 text-center px-4">
      <AlertTriangle className="w-6 h-6 text-muted-foreground" />
      <p className="text-sm text-muted-foreground max-w-xs">{message}</p>
      {onRetry && <button onClick={onRetry} className="flex items-center gap-1.5 text-xs text-primary hover:underline"><RefreshCw className="w-3.5 h-3.5" /> Retry</button>}
    </div>
  );
}
function EmptyState({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center gap-2 py-10 text-center px-4">
      <File className="w-6 h-6 text-muted-foreground" />
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "destructive"; size?: "default" | "sm"; loading?: boolean;
}
function Button({ variant = "primary", size = "default", loading, disabled, children, className = "", ...props }: ButtonProps) {
  const base = "inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--ring)] disabled:opacity-50 disabled:cursor-not-allowed rounded";
  const variants: Record<string, string> = {
    primary: "bg-primary text-primary-foreground hover:bg-[#82152c] active:bg-[#6e1125]",
    secondary: "bg-secondary text-secondary-foreground border border-border hover:bg-muted",
    ghost: "text-muted-foreground hover:bg-muted hover:text-foreground",
    destructive: "bg-destructive text-destructive-foreground hover:opacity-90",
  };
  const sizes: Record<string, string> = { default: "px-4 py-2 text-sm", sm: "px-3 py-1.5 text-xs" };
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} disabled={disabled || loading} {...props}>
      {loading && <Spinner size="sm" />}{children}
    </button>
  );
}
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> { label?: string; error?: string; }
function Input({ label, error, className = "", id, ...props }: InputProps) {
  return (
    <div className="space-y-1">
      {label && <label htmlFor={id} className="block text-sm font-medium text-foreground">{label}</label>}
      <input id={id} className={`w-full px-3 py-2 text-sm rounded border bg-input-background border-border text-foreground placeholder:text-muted-foreground focus:outline focus:outline-2 focus:outline-offset-1 focus:outline-[var(--ring)] transition-all duration-150 ${error ? "border-destructive" : ""} ${className}`} {...props} />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
function PasswordInput({ label, error, id, ...props }: InputProps) {
  const [show, setShow] = useState(false);
  return (
    <div className="space-y-1">
      {label && <label htmlFor={id} className="block text-sm font-medium text-foreground">{label}</label>}
      <div className="relative">
        <input id={id} type={show ? "text" : "password"} className={`w-full px-3 py-2 pr-10 text-sm rounded border bg-input-background border-border text-foreground placeholder:text-muted-foreground focus:outline focus:outline-2 focus:outline-offset-1 focus:outline-[var(--ring)] transition-all duration-150 ${error ? "border-destructive" : ""}`} {...props} />
        <button type="button" onClick={() => setShow(s => !s)} className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1">
          {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

// ─── Attendance Ring ──────────────────────────────────────────────────────────

function AttendanceRing({ pct, size = 44 }: { pct: number; size?: number }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const fill = Math.min(pct / 100, 1) * circ;
  const color = pct < 75 ? "#c9243f" : pct < 85 ? "#eb8f00" : "#22863a";
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--muted)" strokeWidth="6" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="6"
        strokeDasharray={`${fill} ${circ - fill}`} strokeLinecap="round" />
    </svg>
  );
}

// ─── Confirm Modal ────────────────────────────────────────────────────────────

function ConfirmModal({ open, title, body, confirmLabel, destructive, onConfirm, onCancel }: {
  open: boolean; title: string; body: string; confirmLabel: string;
  destructive?: boolean; onConfirm: () => void; onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onCancel}>
      <div className="bg-popover border border-border rounded-lg shadow-xl w-full max-w-sm mx-4 p-6" onClick={e => e.stopPropagation()}>
        <h3 className="text-base font-semibold text-foreground mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground mb-6">{body}</p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" size="sm" onClick={onCancel}>Cancel</Button>
          <Button variant={destructive ? "destructive" : "primary"} size="sm" onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}

// ─── Document Viewer ──────────────────────────────────────────────────────────

function DocumentViewer({ state, onClose }: { state: ViewerState; onClose: () => void }) {
  const [loading, setLoading] = useState(true);

  const isPdf = state.fileType === "pdf";

  useEffect(() => {
    if (state.open) {
      setLoading(true);
    }
  }, [state.open, state.url]);

  if (!state.open) return null;

  const gDocsUrl = `https://docs.google.com/gview?url=${encodeURIComponent(state.url)}&embedded=true`;

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-background">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border bg-background shrink-0">
        <p className="text-sm font-medium text-foreground flex-1 truncate">{state.title}</p>
        {isPdf && (
          <Button variant="ghost" size="sm" onClick={() => window.open(state.url, "_blank", "noopener,noreferrer")}>
            <ExternalLink className="w-3.5 h-3.5" /> Open externally
          </Button>
        )}
        <a href={state.downloadUrl} download className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-secondary text-secondary-foreground border border-border rounded hover:bg-muted transition-colors">
          <Download className="w-3.5 h-3.5" /> Download
        </a>
        <button onClick={onClose} className="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors" aria-label="Close">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden relative bg-muted/20">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center gap-2 text-muted-foreground bg-background/50 z-10">
            <Spinner size="md" /><span className="text-sm">Loading document…</span>
          </div>
        )}
        <iframe
          src={gDocsUrl}
          className="w-full h-full border-0"
          title={state.title}
          onLoad={() => setLoading(false)}
        />
      </div>
    </div>
  );
}

// ─── MCP Popover ─────────────────────────────────────────────────────────────

function MCPPopover({ onClose }: { onClose: () => void }) {
  const [copied, setCopied] = useState(false);
  const session = getSession();
  const keys    = getKeys();

  const fullConfig = {
    servers: {
      "mydylms-mcp": {
        type: "http",
        url: `${API_BASE}/mcp`,
        headers: {
          Authorization: `Bearer ${session?.session_token ?? ""}`,
          "x-api-key":   keys?.features_service_key ?? "",
          "x-user-id":   session?.user_id ?? "",
        },
      },
    },
  };

  const maskedConfig = {
    servers: {
      "mydylms-mcp": {
        type: "http",
        url: `${API_BASE}/mcp`,
        headers: {
          Authorization: "Bearer ••••••••",
          "x-api-key":   "••••••••",
          "x-user-id":   "••••••••",
        },
      },
    },
  };

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(JSON.stringify(fullConfig, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard unavailable */ }
  }

  return (
    <>
      {/* backdrop — click to close */}
      <div className="fixed inset-0 z-30" onClick={onClose} />

      <div className="fixed bottom-4 right-4 z-40 w-[420px] max-w-[calc(100vw-2rem)] max-h-[80vh] overflow-y-auto bg-popover border border-border rounded-lg shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">MCP Configuration</span>
          </div>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded hover:bg-muted">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Config block */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Config</p>
              <button onClick={handleCopy}
                className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded border border-border bg-secondary hover:bg-muted transition-colors">
                {copied ? <><Check className="w-3.5 h-3.5 text-emerald-500" /> Copied</> : <><Copy className="w-3.5 h-3.5" /> Copy Configuration</>}
              </button>
            </div>
            <pre className="text-[11px] font-mono bg-muted rounded p-3 overflow-x-auto text-foreground leading-relaxed whitespace-pre-wrap break-all">
              {JSON.stringify(maskedConfig, null, 2)}
            </pre>
            <p className="text-[10px] text-muted-foreground mt-1.5">Sensitive values are masked. Use Copy Configuration to get the full populated config.</p>
          </div>

          {/* Tools list */}
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Available Tools</p>
            <div className="space-y-1">
              {MCP_TOOLS.map(tool => (
                <div key={tool} className="flex items-center gap-2 px-3 py-1.5 rounded bg-muted/50">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                  <span className="text-xs font-mono text-foreground">{tool}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// ─── Login Screen ─────────────────────────────────────────────────────────────

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<"signin" | "session">("signin");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [formError, setFormError] = useState("");
  const healthy = useHealth();
  const backendDown = healthy === false;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (backendDown) return;
    setEmailError(""); setPasswordError(""); setFormError("");
    let valid = true;
    if (!email.trim())             { setEmailError("Email is required."); valid = false; }
    else if (!email.includes("@")) { setEmailError("Enter a valid email address."); valid = false; }
    if (!password)                 { setPasswordError("Password is required."); valid = false; }
    if (!valid) return;

    setLoading(true); setLoadingStep("signin");
    try {
      const session = await apiLogin(email.trim(), password);
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
      setLoadingStep("session");
      const keys = await apiFetchKeys(session.session_token, session.session_key);
      localStorage.setItem(KEYS_KEY, JSON.stringify(keys));

      try {
        const profile = await fetch(`${API_BASE}/v1/user/profile`, {
          headers: {
            Authorization: `Bearer ${session.session_token}`,
            "X-API-Key": keys.features_service_key,
            "X-User-Id": session.user_id,
          }
        }).then(r => r.ok ? r.json() : null);
        const name = profile?.user_name
          ?? (profile?.firstname && profile?.lastname ? `${profile.firstname} ${profile.lastname}` : null)
          ?? profile?.firstname ?? email.trim();
        localStorage.setItem(DISPLAY_KEY, String(name));
      } catch { localStorage.setItem(DISPLAY_KEY, email.trim()); }

      onLogin();
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Sign in failed. Please try again.");
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-block w-2 h-6 bg-primary rounded-sm" />
            <span className="text-lg font-semibold tracking-tight text-foreground">mydylms</span>
          </div>
          <p className="text-sm text-muted-foreground ml-4">Sign in to access your LMS dashboard</p>
        </div>

        {backendDown && (
          <div className="mb-4 flex items-center gap-2.5 px-3 py-2.5 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded text-sm text-amber-700 dark:text-amber-400">
            <WifiOff className="w-4 h-4 shrink-0" /><span>Backend is currently unreachable. Sign-in is unavailable.</span>
          </div>
        )}
        {healthy === null && (
          <div className="mb-4 flex items-center gap-2.5 px-3 py-2.5 bg-muted border border-border rounded text-sm text-muted-foreground">
            <Spinner size="sm" /><span>Checking connection…</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <Input id="email" label="University email" type="email" placeholder="student@dypatil.edu"
            value={email} onChange={e => setEmail(e.target.value)} error={emailError}
            disabled={loading || backendDown} autoComplete="email" autoFocus />
          <PasswordInput id="password" label="Password" placeholder="••••••••"
            value={password} onChange={e => setPassword(e.target.value)} error={passwordError}
            disabled={loading || backendDown} autoComplete="current-password" />
          {formError && <p className="text-sm text-destructive bg-destructive/8 border border-destructive/20 rounded px-3 py-2">{formError}</p>}
          <Button type="submit" className="w-full" loading={loading} disabled={loading || backendDown || healthy === null}>
            {loading ? (loadingStep === "signin" ? "Signing in…" : "Preparing your session…") : "Sign in"}
          </Button>
        </form>

        <div className="mt-6 pt-5 border-t border-border">
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors">
            <Github className="w-4 h-4 shrink-0" /><span>{GITHUB_LABEL}</span>
          </a>
        </div>
      </div>
    </div>
  );
}

// ─── App Shell ────────────────────────────────────────────────────────────────

const NAV_ITEMS: { id: View; label: string; icon: React.FC<{ className?: string }> }[] = [
  { id: "dashboard",     label: "Dashboard",     icon: LayoutDashboard },
  { id: "courses",       label: "Courses",       icon: BookOpen },
  { id: "attendance",    label: "Attendance",    icon: BarChart2 },
  { id: "announcements", label: "Announcements", icon: Bell },
  { id: "calendar",      label: "Calendar",      icon: Calendar },
  { id: "profile",       label: "Profile",       icon: User },
  { id: "settings",      label: "Settings",      icon: Settings },
];

const PAGE_TITLES: Partial<Record<View, string>> = {
  dashboard: "Dashboard", courses: "Courses", courseDetail: "Course Material",
  attendance: "Attendance", announcements: "Announcements",
  calendar: "Calendar", profile: "Profile", settings: "Settings",
};

function AppShell({ view, onNavigate, onLogout, children }: {
  view: View; onNavigate: (v: View) => void; onLogout: () => void; children: React.ReactNode;
}) {
  const healthy = useHealth();
  const [healthDismissed, setHealthDismissed] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [mcpOpen, setMcpOpen] = useState(false);
  const displayName = getDisplayName();

  useEffect(() => { if (healthy === false) setHealthDismissed(false); }, [healthy]);
  const degraded = healthy === false;
  const navActive = (id: View) => view === id || (view === "courseDetail" && id === "courses");

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-52 shrink-0 bg-sidebar border-r border-sidebar-border h-full">
        <div className="px-4 py-4 border-b border-sidebar-border">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-5 bg-primary rounded-sm" />
            <span className="text-sm font-semibold tracking-tight text-foreground">mydylms</span>
          </div>
        </div>
        <nav className="flex-1 py-2 overflow-y-auto">
          {NAV_ITEMS.map(item => (
            <button key={item.id} onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all duration-150 ${navActive(item.id) ? "text-primary font-medium bg-primary/8 border-r-2 border-primary" : "text-muted-foreground hover:text-foreground hover:bg-sidebar-accent"}`}>
              <item.icon className="w-4 h-4 shrink-0" />{item.label}
            </button>
          ))}
          {/* MCP — opens popover, not a page */}
          <button onClick={() => setMcpOpen(o => !o)}
            className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all duration-150 ${mcpOpen ? "text-primary font-medium bg-primary/8" : "text-muted-foreground hover:text-foreground hover:bg-sidebar-accent"}`}>
            <Cpu className="w-4 h-4 shrink-0" />MCP
          </button>
        </nav>
        <div className="px-4 py-3 border-t border-sidebar-border flex items-center gap-3">
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors" aria-label="GitHub">
            <Github className="w-4 h-4" />
          </a>
          <button onClick={onLogout} className="ml-auto text-muted-foreground hover:text-foreground transition-colors" aria-label="Sign out">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Mobile drawer */}
      {drawerOpen && (
        <div className="md:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/40" onClick={() => setDrawerOpen(false)} />
          <aside className="absolute left-0 top-0 bottom-0 w-56 bg-sidebar border-r border-sidebar-border flex flex-col">
            <div className="flex items-center justify-between px-4 py-4 border-b border-sidebar-border">
              <div className="flex items-center gap-2">
                <span className="inline-block w-1.5 h-5 bg-primary rounded-sm" />
                <span className="text-sm font-semibold tracking-tight text-foreground">mydylms</span>
              </div>
              <button onClick={() => setDrawerOpen(false)} className="text-muted-foreground hover:text-foreground"><X className="w-4 h-4" /></button>
            </div>
            <nav className="flex-1 py-2 overflow-y-auto">
              {NAV_ITEMS.map(item => (
                <button key={item.id} onClick={() => { onNavigate(item.id); setDrawerOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all duration-150 ${navActive(item.id) ? "text-primary font-medium bg-primary/8" : "text-muted-foreground hover:text-foreground hover:bg-sidebar-accent"}`}>
                  <item.icon className="w-4 h-4 shrink-0" />{item.label}
                </button>
              ))}
              <button onClick={() => { setMcpOpen(o => !o); setDrawerOpen(false); }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-muted-foreground hover:text-foreground hover:bg-sidebar-accent transition-all duration-150">
                <Cpu className="w-4 h-4 shrink-0" />MCP
              </button>
            </nav>
            {/* Mobile drawer footer: display name + GitHub + logout */}
            <div className="px-4 py-3 border-t border-sidebar-border flex items-center gap-2">
              {displayName && <span className="text-xs text-muted-foreground truncate flex-1">{displayName}</span>}
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors shrink-0" aria-label="GitHub">
                <Github className="w-4 h-4" />
              </a>
              <button onClick={() => { setDrawerOpen(false); onLogout(); }}
                className="text-muted-foreground hover:text-foreground transition-colors shrink-0" aria-label="Sign out">
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </aside>
        </div>
      )}

      <div className="flex flex-col flex-1 min-w-0 h-full">
        {/* Top bar */}
        <header className="flex items-center gap-3 px-4 md:px-6 py-3 border-b border-border bg-background shrink-0">
          <button className="md:hidden text-muted-foreground hover:text-foreground mr-1" onClick={() => setDrawerOpen(true)}>
            <Menu className="w-5 h-5" />
          </button>
          <h1 className="text-sm font-semibold text-foreground flex-1">{PAGE_TITLES[view] ?? "mydylms"}</h1>

          {/* Health dot */}
          <div className="relative group">
            <span className={`block w-2 h-2 rounded-full cursor-default transition-colors ${healthy === null ? "bg-muted-foreground/40" : healthy ? "bg-emerald-500" : "bg-amber-500"}`} />
            <div className="pointer-events-none absolute right-0 top-5 hidden group-hover:block z-50 bg-popover border border-border rounded px-2.5 py-1.5 text-xs text-foreground whitespace-nowrap shadow-md">
              {healthy === null ? "Checking connection…" : healthy ? "Backend connected" : "Backend unavailable"}
            </div>
          </div>

          {degraded && !healthDismissed && (
            <div className="flex items-center gap-2 px-2.5 py-1 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded text-xs text-amber-700 dark:text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              <span className="hidden sm:inline">LMS may be unreachable</span>
              <button onClick={() => setHealthDismissed(true)} className="hover:opacity-70 ml-0.5"><X className="w-3.5 h-3.5" /></button>
            </div>
          )}

          {/* Desktop: show name */}
          <div className="hidden md:flex items-center gap-1.5 text-muted-foreground text-xs">
            {displayName && <span className="max-w-[160px] truncate">{displayName}</span>}
          </div>

          {/* Mobile: logout button in top nav */}
          <button onClick={onLogout}
            className="md:hidden text-muted-foreground hover:text-foreground transition-colors p-1" aria-label="Sign out">
            <LogOut className="w-4 h-4" />
          </button>
        </header>

        <main className="flex-1 overflow-y-auto">{children}</main>

        {/* Mobile bottom nav (first 5 items, no profile/settings) */}
        <nav className="md:hidden flex border-t border-border bg-background shrink-0">
          {NAV_ITEMS.slice(0, 5).map(item => (
            <button key={item.id} onClick={() => onNavigate(item.id)}
              className={`flex-1 flex flex-col items-center gap-0.5 py-2 text-xs transition-colors ${navActive(item.id) ? "text-primary" : "text-muted-foreground"}`}>
              <item.icon className="w-5 h-5" />
              <span className="text-[10px]">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* MCP Popover */}
      {mcpOpen && <MCPPopover onClose={() => setMcpOpen(false)} />}
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

function DashboardView({ onNavigateCourse }: { onNavigateCourse: (id: string) => void }) {
  const [courses, retryCourses] = useAsync<ApiCourse[]>(() => fetchJSON(`/v1/content/current-course`), []);
  const [attendance, retryAtt]  = useAsync<ApiAttendance[]>(() => fetchJSON(`/v1/attendance`), []);
  const [calendar, retryCal]    = useAsync<ApiCalendarEvent[]>(() => fetchJSON(`/v1/calendar`), []);

  const overallPct = useMemo(() => {
    const data = attendance.data;
    if (!data?.length) return null;
    return Math.round(data.reduce((sum, a) => sum + attPct(a), 0) / data.length);
  }, [attendance.data]);

  return (
    <div className="px-4 md:px-6 py-6 max-w-4xl mx-auto space-y-8">
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Current Semester</h2>
        {courses.status === "loading" && <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">{[1,2,3].map(i=><SkeletonCard key={i}/>)}</div>}
        {courses.status === "error"   && <ErrorState message={courses.error!} onRetry={retryCourses} />}
        {courses.status === "success" && (!courses.data?.length
          ? <EmptyState label="No courses found for current semester." />
          : <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {courses.data.map(c => (
                <button key={courseId(c)} onClick={() => onNavigateCourse(courseId(c))}
                  className="text-left bg-card border border-border rounded p-4 hover:border-primary/40 transition-all duration-150 group">
                  <span className="text-xs font-mono text-primary font-medium">{courseCode(c)}</span>
                  <p className="text-sm font-medium text-foreground mt-1 line-clamp-2 group-hover:text-primary transition-colors">{courseName(c)}</p>
                  {courseTeacher(c) && <p className="text-xs text-muted-foreground mt-1 truncate">{courseTeacher(c)}</p>}
                </button>
              ))}
            </div>
        )}
      </section>

      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Attendance</h2>
        {attendance.status === "loading" && <SkeletonRow />}
        {attendance.status === "error"   && <ErrorState message={attendance.error!} onRetry={retryAtt} />}
        {attendance.status === "success" && (overallPct === null || !attendance.data?.length
          ? <EmptyState label="No attendance data available." />
          : <div className="bg-card border border-border rounded p-4 flex gap-5 items-center">
              <div className="shrink-0 flex flex-col items-center gap-1">
                <div className="relative">
                  <AttendanceRing pct={overallPct} size={72} />
                  <span className={`absolute inset-0 flex items-center justify-center text-sm font-semibold font-mono tabular-nums ${overallPct < 75 ? "text-[#c9243f]" : overallPct < 85 ? "text-amber-600" : "text-emerald-600"}`}>{overallPct}%</span>
                </div>
                <span className="text-[10px] text-muted-foreground">Overall</span>
              </div>
              <div className="flex-1 min-w-0 grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1">
                {attendance.data.map((a, i) => {
                  const pct = attPct(a);
                  return (
                    <div key={i} className="flex items-center justify-between gap-2 py-0.5">
                      <span className="text-xs text-muted-foreground font-mono truncate">{attCode(a)}</span>
                      <span className={`text-xs font-semibold tabular-nums font-mono shrink-0 ${pct < 75 ? "text-[#c9243f]" : pct < 85 ? "text-amber-600" : "text-emerald-600"}`}>{pct}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
        )}
      </section>

      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Upcoming Events</h2>
        {calendar.status === "loading" && <div className="border border-border rounded divide-y divide-border">{[1,2,3].map(i=><SkeletonRow key={i}/>)}</div>}
        {calendar.status === "error"   && <ErrorState message={calendar.error!} onRetry={retryCal} />}
        {calendar.status === "success" && (!calendar.data?.length
          ? <EmptyState label="No upcoming events." />
          : <div className="space-y-2">
              {[...calendar.data].sort((a,b)=>evTimestamp(a)-evTimestamp(b)).slice(0,5).map(ev => (
                <div key={evId(ev)} className="flex items-center gap-3">
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full shrink-0 ${eventTypeColor(evType(ev))}`}>{evType(ev).toUpperCase()}</span>
                  <span className="text-sm text-foreground flex-1 truncate">{evTitle(ev)}</span>
                  <span className="text-xs text-muted-foreground shrink-0 font-mono tabular-nums">{evDate(ev)}</span>
                </div>
              ))}
            </div>
        )}
      </section>
    </div>
  );
}

// ─── Courses ──────────────────────────────────────────────────────────────────

function CoursesView({ onSelectCourse }: { onSelectCourse: (id: string) => void }) {
  const [showAll, setShowAll] = useState(false);
  const [search, setSearch]   = useState("");

  const [current, retryCurrent] = useAsync<ApiCourse[]>(() => fetchJSON(`/v1/content/current-course`), []);
  const [all,     retryAll]     = useAsync<ApiCourse[]>(() => fetchJSON(`/v1/content/course`), []);

  const active = showAll ? all : current;
  const retry  = showAll ? retryAll : retryCurrent;

  const displayed = useMemo(() => {
    let list = active.data ?? [];
    if (showAll) list = [...list].reverse();
    if (showAll && search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(c => courseName(c).toLowerCase().includes(q));
    }
    return list;
  }, [active.data, showAll, search]);

  return (
    <div className="px-4 md:px-6 py-6 max-w-4xl mx-auto">
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="flex rounded border border-border overflow-hidden text-xs">
          <button onClick={() => { setShowAll(false); setSearch(""); }}
            className={`px-3 py-1.5 transition-colors ${!showAll ? "bg-primary text-primary-foreground" : "bg-card text-muted-foreground hover:text-foreground"}`}>Current sem</button>
          <button onClick={() => setShowAll(true)}
            className={`px-3 py-1.5 transition-colors ${showAll ? "bg-primary text-primary-foreground" : "bg-card text-muted-foreground hover:text-foreground"}`}>All semesters</button>
        </div>
        {showAll && (
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
            <input type="text" placeholder="Search courses…" value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded border border-border bg-input-background text-foreground placeholder:text-muted-foreground focus:outline focus:outline-2 focus:outline-offset-1 focus:outline-[var(--ring)]" />
          </div>
        )}
      </div>
      {active.status === "loading" && <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">{[1,2,3,4].map(i=><SkeletonCard key={i}/>)}</div>}
      {active.status === "error"   && <ErrorState message={active.error!} onRetry={retry} />}
      {active.status === "success" && (!displayed.length
        ? <EmptyState label={search ? "No courses match your search." : showAll ? "No courses found." : "No courses for current semester."} />
        : <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {displayed.map(c => (
              <button key={courseId(c)} onClick={() => onSelectCourse(courseId(c))}
                className="text-left bg-card border border-border rounded p-4 hover:border-primary/40 transition-all duration-150 group">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <span className="text-xs font-mono text-primary font-medium">{courseCode(c)}</span>
                  {!showAll && <span className="text-[10px] font-medium px-1.5 py-0.5 bg-primary/10 text-primary rounded-full shrink-0">Current</span>}
                </div>
                <p className="text-sm font-medium text-foreground line-clamp-2 group-hover:text-primary transition-colors">{courseName(c)}</p>
                {courseTeacher(c) && <p className="text-xs text-muted-foreground mt-1 truncate">{courseTeacher(c)}</p>}
                {courseSemTitle(c) && <p className="text-xs text-muted-foreground mt-0.5 truncate">{courseSemTitle(c)}{courseSemPeriod(c) ? ` — ${courseSemPeriod(c)}` : ""}</p>}
                <div className="mt-3 flex items-center gap-1 text-xs text-muted-foreground group-hover:text-primary transition-colors">
                  <span>View material</span><ChevronRight className="w-3 h-3" />
                </div>
              </button>
            ))}
          </div>
      )}
    </div>
  );
}

// ─── Course Detail ────────────────────────────────────────────────────────────

function CourseDetailView({ courseId: cId, onBack }: { courseId: string; onBack: () => void }) {
  const [weeks, retryWeeks] = useAsync<ApiWeek[]>(() => fetchJSON(`/v1/content/course/${encodeURIComponent(cId)}`), [cId]);
  const [search,     setSearch]     = useState("");
  const [weekFilter, setWeekFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [sort,       setSort]       = useState<"newest" | "oldest">("newest");
  const [viewer,     setViewer]     = useState<ViewerState>({ open: false, url: "", downloadUrl: "", title: "", fileType: "other" });
  const [downloading, setDownloading] = useState(false);

  const flat = useMemo(() => weeks.data ? flattenCourseWeeks(weeks.data) : [], [weeks.data]);

  // Week chips — All, then latest→oldest
  const weekOrder = useMemo(() => {
    const seen = new Set<string>();
    const ordered: string[] = [];
    [...flat].sort((a, b) => b.weekOrder - a.weekOrder).forEach(f => {
      if (!seen.has(f.weekTitle)) { seen.add(f.weekTitle); ordered.push(f.weekTitle); }
    });
    return ordered;
  }, [flat]);

  const typeOptions = useMemo(() => [...new Set(flat.map(f => f.moduleType).filter(Boolean))], [flat]);

  const displayed = useMemo(() => {
    let list = [...flat];
    // Default: newest modified first
    list.sort((a, b) => {
      const ta = a.primaryDoc ? docTimestamp(a.primaryDoc) : 0;
      const tb = b.primaryDoc ? docTimestamp(b.primaryDoc) : 0;
      const byTs = sort === "newest" ? tb - ta : ta - tb;
      return byTs !== 0 ? byTs : (sort === "newest" ? b.weekOrder - a.weekOrder : a.weekOrder - b.weekOrder);
    });
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(f => f.moduleTitle.toLowerCase().includes(q) || (f.primaryDoc ? docTitle(f.primaryDoc).toLowerCase().includes(q) : false));
    }
    if (weekFilter !== "all") list = list.filter(f => f.weekTitle === weekFilter);
    if (typeFilter !== "all") list = list.filter(f => f.moduleType === typeFilter);
    return list;
  }, [flat, search, weekFilter, typeFilter, sort]);

  async function bulkDownload() {
    setDownloading(true);
    for (const fm of displayed) {
      if (!fm.primaryDoc) continue;
      const url = buildResourceUrl(docUrl(fm.primaryDoc), true);
      if (url === "#") continue;
      const a = document.createElement("a");
      a.href = url; a.download = fm.moduleTitle; a.click();
      await new Promise(r => setTimeout(r, 600));
    }
    setDownloading(false);
  }

  function openViewer(fm: FlatModule) {
    const doc = fm.primaryDoc;
    if (!doc) return;
    const rawUrl = docUrl(doc);
    const ft = docFileType(doc);
    const viewUrl = buildResourceUrl(rawUrl, false);
    const dlUrl   = buildResourceUrl(rawUrl, true);
    setViewer({ open: true, url: viewUrl, downloadUrl: dlUrl, title: fm.moduleTitle, fileType: ft });
  }

  const chipBase    = "shrink-0 text-xs px-3 py-1.5 rounded-full border transition-colors cursor-pointer whitespace-nowrap";
  const chipActive  = "bg-primary text-primary-foreground border-primary";
  const chipInactive= "bg-card text-muted-foreground border-border hover:border-primary/40 hover:text-foreground";

  return (
    <>
      <DocumentViewer state={viewer} onClose={() => setViewer(v => ({ ...v, open: false }))} />

      <div className="flex flex-col h-full">
        {/* Sticky toolbar */}
        <div className="sticky top-0 z-10 bg-background border-b border-border">
          {/* Row 1: back + search + sort */}
          <div className="flex items-center gap-2 px-4 md:px-6 py-2.5">
            <button onClick={onBack} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors shrink-0">
              <ChevronRight className="w-3.5 h-3.5 rotate-180" /> Back
            </button>
            <div className="w-px h-4 bg-border mx-0.5 hidden sm:block" />
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
              <input type="text" placeholder="Search documents…" value={search} onChange={e => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded border border-border bg-input-background text-foreground placeholder:text-muted-foreground focus:outline focus:outline-2 focus:outline-offset-1 focus:outline-[var(--ring)]" />
            </div>
            {/* Sort — full select on desktop, icon button on mobile */}
            <div className="hidden sm:block relative">
              <select value={sort} onChange={e => setSort(e.target.value as "newest" | "oldest")}
                className="text-xs pl-2.5 pr-6 py-1.5 rounded border border-border bg-input-background text-foreground appearance-none focus:outline focus:outline-2 focus:outline-[var(--ring)] cursor-pointer">
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
              </select>
              <ChevronDown className="absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
            </div>
            <button className="sm:hidden p-1.5 rounded border border-border text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setSort(s => s === "newest" ? "oldest" : "newest")} title={sort === "newest" ? "Newest first" : "Oldest first"}>
              <ArrowUpDown className="w-3.5 h-3.5" />
            </button>
            {/* Bulk download */}
            <button onClick={bulkDownload} disabled={downloading || !displayed.some(f => f.primaryDoc)}
              className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded border border-border bg-card hover:bg-muted transition-colors disabled:opacity-40 shrink-0">
              {downloading ? <Spinner size="sm" /> : <FileDown className="w-3.5 h-3.5" />}
              <span className="hidden sm:inline">{downloading ? "Downloading…" : "Download filtered"}</span>
            </button>
          </div>
          {/* Row 2: week chips */}
          {weekOrder.length > 0 && (
            <div className="flex gap-2 px-4 md:px-6 pb-2 overflow-x-auto [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
              <button onClick={() => setWeekFilter("all")} className={`${chipBase} ${weekFilter === "all" ? chipActive : chipInactive}`}>All</button>
              {weekOrder.map(w => (
                <button key={w} onClick={() => setWeekFilter(w)} className={`${chipBase} ${weekFilter === w ? chipActive : chipInactive}`}>{w}</button>
              ))}
            </div>
          )}
          {/* Row 3: type chips */}
          {typeOptions.length > 0 && (
            <div className="flex gap-2 px-4 md:px-6 pb-2.5 overflow-x-auto [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
              <button onClick={() => setTypeFilter("all")} className={`${chipBase} ${typeFilter === "all" ? chipActive : chipInactive}`}>
                <span className="flex items-center gap-1.5"><File className="w-3.5 h-3.5" />All</span>
              </button>
              {typeOptions.map(t => (
                <button key={t} onClick={() => setTypeFilter(t)} className={`${chipBase} ${typeFilter === t ? chipActive : chipInactive}`}>
                  <span className="flex items-center gap-1.5">{moduleTypeIcon(t)}{t}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 max-w-5xl mx-auto w-full">
          {weeks.status === "loading" && (
            <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
              {[1,2,3,4,5,6].map(i => <SkeletonCard key={i} />)}
            </div>
          )}
          {weeks.status === "error" && <ErrorState message={weeks.error!} onRetry={retryWeeks} />}
          {weeks.status === "success" && (!displayed.length
            ? <EmptyState label={flat.length ? "No results match your filters." : "No course material available."} />
            : <>
                {/* Desktop: grid cards */}
                <div className="hidden sm:grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
                  {displayed.map(fm => <DocCard key={fm.moduleId} fm={fm} onView={() => openViewer(fm)} />)}
                </div>
                {/* Mobile: compact rows */}
                <div className="sm:hidden divide-y divide-border border border-border rounded overflow-hidden">
                  {displayed.map(fm => <DocRow key={fm.moduleId} fm={fm} onView={() => openViewer(fm)} />)}
                </div>
              </>
          )}
        </div>
      </div>
    </>
  );
}

// ─── Document Card (desktop) ──────────────────────────────────────────────────

function DocCard({ fm, onView }: { fm: FlatModule; onView: () => void }) {
  const doc = fm.primaryDoc;
  const cat = fm.moduleCategory;
  const ft  = doc ? docFileType(doc) : "other";
  const rawUrl = doc ? docUrl(doc) : "#";
  const viewUrl = buildResourceUrl(rawUrl, false);
  const dlUrl   = buildResourceUrl(rawUrl, true);

  const isFile  = cat === "file";
  const isUrl   = cat === "url";
  const isLms   = cat === "quiz" || cat === "page";
  const lmsUrl  = rawUrl;

  const canView     = isFile && ft !== "office";
  const canDownload = isFile;
  const filename    = doc ? docTitle(doc) : "";
  const teacher     = doc ? docTeacher(doc) : "";
  const dateStr     = doc ? docDate(doc) : "";
  const sizeStr     = doc ? docSize(doc) : "";

  function handleClick() {
    if (canView) { onView(); return; }
    if (isUrl || isLms) window.open(lmsUrl, "_blank", "noopener,noreferrer");
  }

  const clickable = canView || isUrl || isLms;

  return (
    <div
      onClick={clickable ? handleClick : undefined}
      className={`relative bg-card border border-border rounded p-4 flex flex-col gap-3 group transition-all duration-150 ${clickable ? "cursor-pointer hover:border-primary/50" : ""}`}
    >
      {/* Hover tooltip */}
      {(filename || teacher) && (
        <div className="pointer-events-none absolute bottom-full left-0 mb-1.5 z-20 hidden group-hover:block bg-popover border border-border rounded px-3 py-2 shadow-lg max-w-[220px]">
          {filename && <p className="text-xs text-foreground font-medium break-all">{filename}</p>}
          {teacher  && <p className="text-xs text-muted-foreground mt-0.5">{teacher}</p>}
        </div>
      )}

      {/* Top: type icon + week tag */}
      <div className="flex items-center justify-between gap-2">
        <span className={`p-1.5 rounded ${moduleTypeBadge(fm.moduleType)}`}>{moduleTypeIcon(fm.moduleType)}</span>
        <span className="text-[10px] px-2 py-0.5 bg-muted text-muted-foreground rounded-full truncate max-w-[130px]">{fm.weekTitle}</span>
      </div>

      {/* Middle: title */}
      <div className="flex-1">
        <p className="text-sm font-medium text-foreground line-clamp-2 leading-snug">{fm.moduleTitle}</p>
        {fm.moduleType && <span className={`inline-block mt-1.5 text-[10px] px-1.5 py-0.5 rounded-full ${moduleTypeBadge(fm.moduleType)}`}>{fm.moduleType}</span>}
      </div>

      {/* Metadata */}
      {(dateStr || sizeStr) && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono tabular-nums">
          {dateStr && <span className="truncate">{dateStr}</span>}
          {sizeStr && <span className="shrink-0">{sizeStr}</span>}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-1.5" onClick={e => e.stopPropagation()}>
        {(isUrl || isLms) && (
          <a href={lmsUrl} target="_blank" rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-1.5 rounded border border-border bg-secondary hover:bg-muted transition-colors">
            <ExternalLink className="w-3.5 h-3.5" /> Open
          </a>
        )}
        {canView && (
          <button onClick={onView}
            className="flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-1.5 rounded border border-border bg-secondary hover:bg-muted transition-colors">
            <Eye className="w-3.5 h-3.5" /> View
          </button>
        )}
        {canDownload && (
          <a href={dlUrl} download onClick={e => e.stopPropagation()}
            className={`flex items-center justify-center gap-1.5 text-xs font-medium py-1.5 rounded border border-border bg-secondary hover:bg-muted transition-colors ${canView ? "px-2.5" : "flex-1"}`}>
            <Download className="w-3.5 h-3.5" />{!canView && "Download"}
          </a>
        )}
      </div>
    </div>
  );
}

// ─── Document Row (mobile) ────────────────────────────────────────────────────

function DocRow({ fm, onView }: { fm: FlatModule; onView: () => void }) {
  const doc = fm.primaryDoc;
  const cat = fm.moduleCategory;
  const ft  = doc ? docFileType(doc) : "other";
  const rawUrl = doc ? docUrl(doc) : "#";
  const viewUrl = buildResourceUrl(rawUrl, false);
  const dlUrl   = buildResourceUrl(rawUrl, true);

  const isFile  = cat === "file";
  const isUrl   = cat === "url";
  const isLms   = cat === "quiz" || cat === "page";
  const lmsUrl  = rawUrl;
  const canView     = isFile && ft !== "office";
  const canDownload = isFile;

  const dateStr = doc ? docDate(doc) : "";
  const sizeStr = doc ? docSize(doc) : "";
  const meta    = [dateStr, sizeStr, fm.weekTitle].filter(Boolean).join(" · ");

  function handleClick() {
    if (canView)        { onView(); return; }
    if (isUrl || isLms) window.open(lmsUrl, "_blank", "noopener,noreferrer");
  }

  return (
    <div onClick={handleClick}
      className={`flex items-center gap-3 px-4 bg-card group min-h-[56px] py-2 ${(canView || isUrl || isLms) ? "cursor-pointer hover:bg-muted/30 transition-colors" : ""}`}>
      <span className={`shrink-0 ${moduleTypeBadge(fm.moduleType)}`}>{moduleTypeIcon(fm.moduleType)}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{fm.moduleTitle}</p>
        {meta && <p className="text-[10px] text-muted-foreground truncate mt-0.5">{meta}</p>}
      </div>
      <div className="flex items-center gap-0.5 shrink-0" onClick={e => e.stopPropagation()}>
        {(isUrl || isLms) && (
          <a href={lmsUrl} target="_blank" rel="noopener noreferrer"
            className="p-2 rounded text-muted-foreground hover:text-primary hover:bg-muted transition-colors" aria-label="Open">
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
        {canView && (
          <button onClick={onView} className="p-2 rounded text-muted-foreground hover:text-primary hover:bg-muted transition-colors" aria-label="View">
            <Eye className="w-4 h-4" />
          </button>
        )}
        {canDownload && (
          <a href={dlUrl} download className="p-2 rounded text-muted-foreground hover:text-primary hover:bg-muted transition-colors" aria-label="Download">
            <Download className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  );
}

// ─── Attendance ───────────────────────────────────────────────────────────────

function AttendanceView() {
  const [state, retry] = useAsync<ApiAttendance[]>(() => fetchJSON(`/v1/attendance`), []);
  const sorted = state.data ? [...state.data].sort((a, b) => attPct(a) - attPct(b)) : [];

  return (
    <div className="px-4 md:px-6 py-6 max-w-3xl mx-auto">
      {state.status === "loading" && <div className="border border-border rounded divide-y divide-border">{[1,2,3,4].map(i=><SkeletonRow key={i}/>)}</div>}
      {state.status === "error"   && <ErrorState message={state.error!} onRetry={retry} />}
      {state.status === "success" && (!sorted.length
        ? <EmptyState label="No attendance data available." />
        : <>
            <div className="border border-border rounded overflow-hidden divide-y divide-border">
              {sorted.map((rec, i) => {
                const pct = attPct(rec);
                return (
                  <div key={i} className="flex items-center gap-4 px-4 py-3 bg-card">
                    <AttendanceRing pct={pct} size={44} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground font-mono">{attCode(rec)}</p>
                      <p className="text-xs text-muted-foreground tabular-nums">{attPresent(rec)} present · {attAbsent(rec)} absent · {attTotal(rec)} total</p>
                    </div>
                    <p className={`text-lg font-semibold tabular-nums font-mono shrink-0 ${pct<75?"text-[#c9243f]":pct<85?"text-amber-600":"text-emerald-600"}`}>{pct}%</p>
                  </div>
                );
              })}
            </div>
            <p className="mt-3 text-xs text-muted-foreground">Sorted by lowest attendance first.</p>
          </>
      )}
    </div>
  );
}

// ─── Announcements ────────────────────────────────────────────────────────────

function AnnouncementsView() {
  const [showAll, setShowAll] = useState(false);
  const [state, retry] = useAsync<ApiAnnouncement[]>(
    () => fetchJSON(showAll ? `/v1/annoucement/all` : `/v1/annoucement`), [showAll]
  );
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  return (
    <div className="px-4 md:px-6 py-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-5">
        <div className="flex rounded border border-border overflow-hidden text-xs">
          <button onClick={() => setShowAll(false)} className={`px-3 py-1.5 transition-colors ${!showAll?"bg-primary text-primary-foreground":"bg-card text-muted-foreground hover:text-foreground"}`}>Recent</button>
          <button onClick={() => setShowAll(true)}  className={`px-3 py-1.5 transition-colors ${showAll ?"bg-primary text-primary-foreground":"bg-card text-muted-foreground hover:text-foreground"}`}>All history</button>
        </div>
      </div>
      {state.status === "loading" && <div className="border border-border rounded divide-y divide-border">{[1,2,3].map(i=><div key={i} className="p-4"><SkeletonRow/></div>)}</div>}
      {state.status === "error"   && <ErrorState message={state.error!} onRetry={retry} />}
      {state.status === "success" && (!state.data?.length
        ? <EmptyState label="No announcements found." />
        : <div className="divide-y divide-border border border-border rounded overflow-hidden">
            {state.data.map(a => {
              const id = annId(a); const body = annBodyText(a);
              return (
                <div key={id} className="bg-card px-4 py-4">
                  <div className="flex items-start justify-between gap-4 mb-1">
                    <p className="text-sm font-medium text-foreground">{annTitle(a)}</p>
                    <span className="text-xs text-muted-foreground shrink-0 tabular-nums">{annDate(a)}</span>
                  </div>
                  {annAuthor(a) && <p className="text-xs text-muted-foreground mb-2">{annAuthor(a)}</p>}
                  <p className={`text-sm text-foreground leading-relaxed whitespace-pre-line ${!expanded[id]?"line-clamp-3":""}`}>{body}</p>
                  {body.length > 150 && (
                    <button onClick={() => setExpanded(s => ({ ...s, [id]: !s[id] }))} className="mt-1.5 text-xs text-primary hover:underline">
                      {expanded[id] ? "Show less" : "Read more"}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
      )}
    </div>
  );
}

// ─── Calendar ─────────────────────────────────────────────────────────────────

function CalendarView() {
  const [state, retry] = useAsync<ApiCalendarEvent[]>(() => fetchJSON(`/v1/calendar`), []);
  const sorted = state.data ? [...state.data].sort((a, b) => evTimestamp(a) - evTimestamp(b)) : [];

  return (
    <div className="px-4 md:px-6 py-6 max-w-4xl mx-auto">
      {state.status === "loading" && <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">{[1,2,3,4,5,6].map(i=><SkeletonCard key={i}/>)}</div>}
      {state.status === "error"   && <ErrorState message={state.error!} onRetry={retry} />}
      {state.status === "success" && (!sorted.length
        ? <EmptyState label="No calendar events found." />
        : <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {sorted.map(ev => (
              <div key={evId(ev)} className="bg-card border border-border rounded p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${eventTypeColor(evType(ev))}`}>{eventTypeLabel(evType(ev))}</span>
                  <span className="text-xs text-muted-foreground font-mono tabular-nums shrink-0">{evDate(ev)}</span>
                </div>
                <p className="text-sm font-medium text-foreground leading-snug">{evTitle(ev)}</p>
              </div>
            ))}
          </div>
      )}
    </div>
  );
}

// ─── Profile ──────────────────────────────────────────────────────────────────

function ProfileView() {
  const [detailed, setDetailed] = useState(false);
  const [v1, retryV1] = useAsync<Record<string, unknown>>(() => fetchJSON(`/v1/user/profile`), []);
  const [v0, retryV0] = useAsync<Record<string, unknown>>(() => fetchJSON(`/v0/user/profile`), []);

  const V1_FIELDS: [string, string][] = [
    ["firstname","First name"],["lastname","Last name"],["rollid","Roll ID"],
    ["dob","Date of birth"],["city","City"],["town","Town"],
    ["fathername","Father's name"],["mothername","Mother's name"],
    ["phonenumber","Phone number"],["email","Email"],
  ];
  const V0_FIELDS: [string, string][] = [
    ["user_name","Username"],["roll_no","Roll no."],["gender","Gender"],
    ["dob","Date of birth"],["postal_code","Postal code"],["city","City"],
    ["country","Country"],["religion","Religion"],["category","Category"],
    ["father_name","Father's name"],["mother_name","Mother's name"],
    ["pmob_no","Phone"],["femail_id","Email"],["address","Address"],
  ];

  const activeState = detailed ? v0 : v1;
  const activeRetry = detailed ? retryV0 : retryV1;
  const fields      = detailed ? V0_FIELDS : V1_FIELDS;

  return (
    <div className="px-4 md:px-6 py-6 max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-5">
        <div className="flex rounded border border-border overflow-hidden text-xs">
          <button onClick={() => setDetailed(false)} className={`px-3 py-1.5 transition-colors ${!detailed?"bg-primary text-primary-foreground":"bg-card text-muted-foreground hover:text-foreground"}`}>Overview</button>
          <button onClick={() => setDetailed(true)}  className={`px-3 py-1.5 transition-colors ${detailed ?"bg-primary text-primary-foreground":"bg-card text-muted-foreground hover:text-foreground"}`}>Detailed</button>
        </div>
      </div>
      {activeState.status === "loading" && <div className="border border-border rounded divide-y divide-border">{[1,2,3,4,5].map(i=><SkeletonRow key={i}/>)}</div>}
      {activeState.status === "error"   && <ErrorState message={activeState.error!} onRetry={activeRetry} />}
      {activeState.status === "success" && (
        <div className="border border-border rounded overflow-hidden divide-y divide-border">
          {fields.map(([key, label]) => (
            <div key={key} className="flex items-start gap-4 px-4 py-3 bg-card">
              <span className="text-xs text-muted-foreground w-32 shrink-0 pt-0.5">{label}</span>
              <span className="text-sm text-foreground break-all">
                {activeState.data?.[key] != null && activeState.data[key] !== "" ? String(activeState.data[key]) : <span className="text-muted-foreground">—</span>}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Settings ─────────────────────────────────────────────────────────────────

function SettingsView({ theme, onThemeChange, onLogout }: {
  theme: Theme; onThemeChange: (t: Theme) => void; onLogout: () => void;
}) {
  const [signOutModal, setSignOutModal] = useState(false);
  const [clearModal,   setClearModal]   = useState(false);
  const [signingOut,   setSigningOut]   = useState(false);

  async function handleSignOut() {
    setSigningOut(true); await performLogout(); setSigningOut(false); setSignOutModal(false); onLogout();
  }
  function handleClearData() { clearAll(); setClearModal(false); onLogout(); }

  return (
    <div className="px-4 md:px-6 py-6 max-w-xl mx-auto space-y-8">
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Appearance</h2>
        <div className="bg-card border border-border rounded p-4">
          <p className="text-sm font-medium text-foreground mb-3">Theme</p>
          <div className="flex rounded border border-border overflow-hidden w-fit">
            {([["light",<Sun className="w-4 h-4"/>,"Light"],["dark",<Moon className="w-4 h-4"/>,"Dark"],["system",<Monitor className="w-4 h-4"/>,"System"]] as [Theme,React.ReactNode,string][]).map(([val,icon,label])=>(
              <button key={val} onClick={()=>onThemeChange(val)} className={`flex items-center gap-1.5 px-3 py-2 transition-colors ${theme===val?"bg-primary text-primary-foreground":"bg-card text-muted-foreground hover:text-foreground"}`}>
                {icon}<span className="text-xs">{label}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Session &amp; Data</h2>
        <div className="bg-card border border-border rounded divide-y divide-border overflow-hidden">
          <div className="px-4 py-3"><p className="text-sm text-muted-foreground">Session data is stored only in this browser. Signing out or clearing data removes it.</p></div>
          <div className="px-4 py-3 flex items-center justify-between gap-4">
            <div><p className="text-sm font-medium text-foreground">Sign out</p><p className="text-xs text-muted-foreground">Ends your session and returns to login</p></div>
            <Button variant="secondary" size="sm" onClick={() => setSignOutModal(true)}><LogOut className="w-3.5 h-3.5" />Sign out</Button>
          </div>
          <div className="px-4 py-3 flex items-center justify-between gap-4">
            <div><p className="text-sm font-medium text-foreground">Clear local data</p><p className="text-xs text-muted-foreground">Removes all stored keys and session data</p></div>
            <Button variant="destructive" size="sm" onClick={() => setClearModal(true)}><Trash2 className="w-3.5 h-3.5" />Clear data</Button>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">About</h2>
        <div className="bg-card border border-border rounded p-4 space-y-2">
          <p className="text-sm text-foreground">mydylms Client is open source. Report bugs, request features, or contribute.</p>
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 text-sm text-primary hover:underline">
            <Github className="w-4 h-4" />{GITHUB_LABEL}<ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </section>

      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Related Projects</h2>
        <div className="bg-card border border-border rounded p-4">
          <p className="text-sm font-semibold text-foreground mb-0.5">Uniclare Client</p>
          <p className="text-sm text-muted-foreground mb-3">See end-semester marks and result data your university portal doesn't show.</p>
          <div className="flex flex-wrap items-center gap-2">
            <a href={UNICLARE_WEB} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-primary text-primary-foreground rounded hover:bg-[#82152c] transition-colors">
              <ExternalLink className="w-3.5 h-3.5" />Open web app
            </a>
            <a href={UNICLARE_GITHUB} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-secondary text-secondary-foreground border border-border rounded hover:bg-muted transition-colors">
              <Github className="w-3.5 h-3.5" />GitHub
            </a>
          </div>
        </div>
      </section>

      <ConfirmModal open={signOutModal} title="Sign out"
        body="You will be returned to the login screen. Your session data will be cleared from this browser."
        confirmLabel={signingOut ? "Signing out…" : "Sign out"} onConfirm={handleSignOut} onCancel={() => setSignOutModal(false)} />
      <ConfirmModal open={clearModal} title="Clear all local data"
        body="This will remove your session token, API keys, and all locally stored data. You will need to sign in again."
        confirmLabel="Clear data" destructive onConfirm={handleClearData} onCancel={() => setClearModal(false)} />
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState<View>(() => isAuthenticated() ? "dashboard" : "login");
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [theme, setTheme] = useState<Theme>(() => {
    try { return (localStorage.getItem(THEME_KEY) as Theme) ?? "system"; } catch { return "system"; }
  });

  useEffect(() => { applyTheme(theme); }, [theme]);
  useEffect(() => {
    if (theme !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const h = () => applyTheme("system");
    mq.addEventListener("change", h); return () => mq.removeEventListener("change", h);
  }, [theme]);
  useEffect(() => {
    const h = () => { clearAll(); setView("login"); setSelectedCourseId(null); };
    window.addEventListener(SESSION_EXPIRED, h); return () => window.removeEventListener(SESSION_EXPIRED, h);
  }, []);
  useEffect(() => {
    if (view !== "login" && !isAuthenticated()) { clearAll(); setView("login"); setSelectedCourseId(null); }
  }, [view]);

  const handleThemeChange = useCallback((t: Theme) => {
    setTheme(t); try { localStorage.setItem(THEME_KEY, t); } catch {} applyTheme(t);
  }, []);
  const handleLogin  = useCallback(() => setView("dashboard"), []);
  const handleLogout = useCallback(async () => { await performLogout(); setView("login"); setSelectedCourseId(null); }, []);
  const handleNavigate = useCallback((v: View) => {
    if (!isAuthenticated()) { setView("login"); return; }
    setView(v); if (v !== "courseDetail") setSelectedCourseId(null);
  }, []);
  const handleSelectCourse = useCallback((id: string) => { setSelectedCourseId(id); setView("courseDetail"); }, []);

  if (view === "login" || !isAuthenticated()) return <LoginScreen onLogin={handleLogin} />;

  return (
    <>
      <style>{`
        body { font-family: 'Inter', system-ui, sans-serif; }
        .font-mono, [class*="tabular-nums"] { font-family: 'Geist Mono', 'Courier New', monospace; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--muted-foreground); }
      `}</style>
      <AppShell view={view} onNavigate={handleNavigate} onLogout={handleLogout}>
        {view === "dashboard"     && <DashboardView onNavigateCourse={handleSelectCourse} />}
        {view === "courses"       && <CoursesView onSelectCourse={handleSelectCourse} />}
        {view === "courseDetail"  && selectedCourseId && <CourseDetailView courseId={selectedCourseId} onBack={() => setView("courses")} />}
        {view === "attendance"    && <AttendanceView />}
        {view === "announcements" && <AnnouncementsView />}
        {view === "calendar"      && <CalendarView />}
        {view === "profile"       && <ProfileView />}
        {view === "settings"      && <SettingsView theme={theme} onThemeChange={handleThemeChange} onLogout={handleLogout} />}
      </AppShell>
    </>
  );
}
