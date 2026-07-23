import type { EmotionResult, IntentResult } from "./types";

export type MoodShiftType =
  | "none"
  | "improving"
  | "declining"
  | "intensifying"
  | "stabilizing"
  | "mixed";

export interface MemoryTurn {
  timestamp: number;
  message: string;
  primary_emotion: string;
  secondary_emotion: string | null;
  hidden_emotion: string | null;
  intensity: number;
  confidence: number;
  intent: string;
  reasoning: string;
  salience: number;
}

export interface MoodShift {
  shift_type: MoodShiftType;
  from_emotion: string;
  to_emotion: string;
  from_intensity: number;
  to_intensity: number;
  summary: string;
}

const POSITIVE = new Set([
  "happiness",
  "excitement",
  "hope",
  "pride",
  "gratitude",
  "curiosity",
  "trust",
  "love",
  "optimism",
  "anticipation",
  "surprise",
]);

const NEGATIVE = new Set([
  "sadness",
  "anger",
  "fear",
  "anxiety",
  "shame",
  "guilt",
  "loneliness",
  "frustration",
  "disgust",
  "disappointment",
  "burnout",
]);

const HIGH_STAKES_INTENTS = new Set([
  "seeking_comfort",
  "venting",
  "celebrating",
  "seeking_validation",
]);

export function computeSalience(
  emotion: EmotionResult,
  intent: IntentResult
): number {
  const intensityN = emotion.intensity / 10;
  const conf = emotion.confidence;
  const hiddenBoost = emotion.hidden ? 0.15 : 0;
  const intentBoost = HIGH_STAKES_INTENTS.has(intent.primary_intent) ? 0.1 : 0;
  const raw = 0.45 * intensityN + 0.25 * conf + hiddenBoost + intentBoost;
  return Math.max(0, Math.min(1, raw));
}

/**
 * In-memory emotional timeline store with salience-aware context.
 */
export class EmotionalMemory {
  private store: Map<string, MemoryTurn[]> = new Map();
  private maxTurns: number;

  constructor(maxTurnsPerSession = 50) {
    this.maxTurns = maxTurnsPerSession;
  }

  addTurn(
    sessionId: string,
    message: string,
    emotion: EmotionResult,
    intent: IntentResult
  ): MemoryTurn {
    if (!this.store.has(sessionId)) {
      this.store.set(sessionId, []);
    }

    const turn: MemoryTurn = {
      timestamp: Date.now() / 1000,
      message,
      primary_emotion: emotion.primary,
      secondary_emotion: emotion.secondary ?? null,
      hidden_emotion: emotion.hidden ?? null,
      intensity: emotion.intensity,
      confidence: emotion.confidence,
      intent: intent.primary_intent,
      reasoning: emotion.reasoning,
      salience: computeSalience(emotion, intent),
    };

    const timeline = this.store.get(sessionId)!;
    timeline.push(turn);

    if (timeline.length > this.maxTurns) {
      this.store.set(sessionId, timeline.slice(-this.maxTurns));
    }

    return turn;
  }

  getTimeline(sessionId: string): MemoryTurn[] {
    return [...(this.store.get(sessionId) ?? [])];
  }

  getLastTurn(sessionId: string): MemoryTurn | null {
    const timeline = this.store.get(sessionId) ?? [];
    return timeline.length > 0 ? timeline[timeline.length - 1] : null;
  }

  getRecentEmotions(sessionId: string, n = 5): string[] {
    return this.getTimeline(sessionId)
      .slice(-n)
      .map((t) => t.primary_emotion);
  }

  detectMoodShift(sessionId: string): MoodShift {
    const timeline = this.getTimeline(sessionId);

    if (timeline.length < 2) {
      return {
        shift_type: "none",
        from_emotion: "",
        to_emotion: "",
        from_intensity: 0,
        to_intensity: 0,
        summary: "Not enough turns to detect a shift.",
      };
    }

    const prev = timeline[timeline.length - 2];
    const curr = timeline[timeline.length - 1];

    const prevPol = this.polarity(prev.primary_emotion);
    const currPol = this.polarity(curr.primary_emotion);

    let shift_type: MoodShiftType;
    let summary: string;

    if (prevPol === "negative" && currPol === "positive") {
      shift_type = "improving";
      summary = `Mood improved from ${prev.primary_emotion} to ${curr.primary_emotion}.`;
    } else if (prevPol === "positive" && currPol === "negative") {
      shift_type = "declining";
      summary = `Mood declined from ${prev.primary_emotion} to ${curr.primary_emotion}.`;
    } else if (
      prev.primary_emotion === curr.primary_emotion &&
      curr.intensity > prev.intensity + 2
    ) {
      shift_type = "intensifying";
      summary = `${curr.primary_emotion} is intensifying (${prev.intensity} → ${curr.intensity}).`;
    } else if (
      prev.primary_emotion === curr.primary_emotion &&
      curr.intensity < prev.intensity - 2
    ) {
      shift_type = "stabilizing";
      summary = `${curr.primary_emotion} is stabilizing (${prev.intensity} → ${curr.intensity}).`;
    } else {
      shift_type = "mixed";
      summary = `Mood moved from ${prev.primary_emotion} (${prev.intensity}) to ${curr.primary_emotion} (${curr.intensity}).`;
    }

    return {
      shift_type,
      from_emotion: prev.primary_emotion,
      to_emotion: curr.primary_emotion,
      from_intensity: prev.intensity,
      to_intensity: curr.intensity,
      summary,
    };
  }

  getContextForStrategy(sessionId: string): string {
    const timeline = this.getTimeline(sessionId);
    if (timeline.length === 0) {
      return "No previous emotional context.";
    }

    const recent = timeline.slice(-8);
    const ranked = [...recent]
      .sort((a, b) => b.salience - a.salience || b.timestamp - a.timestamp)
      .slice(0, 4)
      .sort((a, b) => a.timestamp - b.timestamp);

    const lines = ranked.map((t) => {
      const hidden = t.hidden_emotion ? `, hidden=${t.hidden_emotion}` : "";
      return `- ${t.primary_emotion} (intensity ${t.intensity}, salience ${t.salience.toFixed(2)})${hidden} | intent=${t.intent}`;
    });

    const shift = this.detectMoodShift(sessionId);
    const shiftText =
      shift.shift_type !== "none" ? `\nRecent mood shift: ${shift.summary}` : "";

    return (
      "Recent emotional timeline (salience-aware):\n" +
      lines.join("\n") +
      shiftText
    );
  }

  clearSession(sessionId: string): void {
    this.store.delete(sessionId);
  }

  private polarity(emotion: string): "positive" | "negative" | "neutral" {
    if (POSITIVE.has(emotion)) return "positive";
    if (NEGATIVE.has(emotion)) return "negative";
    return "neutral";
  }
}
