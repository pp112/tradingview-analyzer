import { Fragment, useEffect, useMemo, useState } from "react";

type Session = {
  id: string;
  label: string;
  start: string;
  end: string;
};

type SessionStatus = 
  | { active: true, minutesUntilEnd: number } 
  | { active: false, minutesUntilStart: number };

type SessionPhase = "idle" | "soon" | "active" | "ending";

type SessionWithStatus = {
  session: Session;
  st: SessionStatus;
};

const SESSIONS: Session[] = [
  { id: "tokyo", label: "Токио", start: "07:00", end: "13:00" },
  { id: "london", label: "Лондон", start: "15:00", end: "23:30" },
  { id: "ny", label: "Нью-Йорк", start: "21:30", end: "04:00" },
];

const TITLE_SESSIONS = SESSIONS
  .map((s) => `${s.label}: ${s.start} - ${s.end}`)
  .join("\n");

const SOON_MIN = 60;
const ENDING_MIN = 30;

const toMin = (t: string) => {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
};

function getStatus(session: Session, now: Date): SessionStatus {
  const curr = now.getHours() * 60 + now.getMinutes();
  const start = toMin(session.start);
  const end = toMin(session.end);

  const active = 
    start <= end
      ? curr >= start && curr < end
      : curr >= start || curr < end;

  return active 
    ? { active: true, minutesUntilEnd: (end - curr + 1440) % 1440 }
    : { active: false, minutesUntilStart: (start - curr + 1440) % 1440 };
}

function getPhase(st: SessionStatus): SessionPhase {
  if (st.active) {
    return st.minutesUntilEnd <= ENDING_MIN ? "ending" : "active";
  }
  return st.minutesUntilStart <= SOON_MIN ? "soon" : "idle";
}

const formatDuration = (min: number) => {
  const h = Math.floor(min / 60);
  const m = min % 60;
  if (h === 0) return `${m}м`;
  if (m === 0) return `${h}ч`;
  return `${h}ч ${m}м`;
};

function compareSessions(
  a: SessionWithStatus, 
  b: SessionWithStatus
) {
  if (a.st.active !== b.st.active) {
    return a.st.active ? -1 : 1;
  }

  if (a.st.active && b.st.active) {
    return a.st.minutesUntilEnd - b.st.minutesUntilEnd;
  }

  if (!a.st.active && !b.st.active) {
    return a.st.minutesUntilStart - b.st.minutesUntilStart;
  }

  return 0;
}

export function MarketSessions() {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const interval = setInterval(
      () => setNow(new Date()), 
      10_000,
    );
    return () => clearInterval(interval);
  }, []);

  const sorted = useMemo(() =>
    SESSIONS
      .map((session) => ({
        session,
        st: getStatus(session, now),
      }))
      .sort(compareSessions),
  [now])

  return (
    <div className="market-sessions" title={TITLE_SESSIONS}>
      {sorted.map(({ session, st }, index) => (
        <Fragment key={session.id}>
          <div className="market-session" data-phase={getPhase(st)}>
            <span className="market-session-label">{session.label}:</span>
            <span className="market-session-value">
              {st.active
                ? `активна (ещё ${formatDuration(st.minutesUntilEnd)})`
                : `через ${formatDuration(st.minutesUntilStart)}`}
            </span>
          </div>
          {index < SESSIONS.length - 1 && (
            <span className="market-session-divider" />
          )}
        </Fragment>
      ))}
    </div>
  );
}