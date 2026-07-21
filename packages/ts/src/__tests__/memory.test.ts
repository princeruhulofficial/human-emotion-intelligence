import { describe, it, expect, beforeEach } from "vitest";
import { EmotionalMemory } from "../memory";
import type { EmotionResult, IntentResult } from "../types";

function makeEmotion(
  primary: string,
  intensity = 5,
  hidden?: string
): EmotionResult {
  return {
    primary: primary as any,
    secondary: null,
    hidden: (hidden as any) ?? null,
    intensity,
    confidence: 0.85,
    reasoning: "test",
  };
}

function makeIntent(intent = "seeking_comfort"): IntentResult {
  return {
    primary_intent: intent as any,
    secondary_intent: null,
    confidence: 0.8,
    reasoning: "test",
  };
}

describe("EmotionalMemory", () => {
  let memory: EmotionalMemory;

  beforeEach(() => {
    memory = new EmotionalMemory();
  });

  it("starts with empty timeline", () => {
    expect(memory.getTimeline("s1")).toEqual([]);
    expect(memory.getLastTurn("s1")).toBeNull();
  });

  it("records turns and returns timeline", () => {
    memory.addTurn("s1", "I failed", makeEmotion("sadness", 8), makeIntent());
    memory.addTurn("s1", "Maybe tomorrow", makeEmotion("hope", 4), makeIntent("sharing"));

    const timeline = memory.getTimeline("s1");
    expect(timeline).toHaveLength(2);
    expect(timeline[0].primary_emotion).toBe("sadness");
    expect(timeline[1].primary_emotion).toBe("hope");
    expect(timeline[0].intensity).toBe(8);
  });

  it("detects improving mood shift", () => {
    memory.addTurn("s1", "Everything is ruined", makeEmotion("sadness", 9), makeIntent());
    memory.addTurn("s1", "I got a new opportunity", makeEmotion("hope", 7), makeIntent("celebrating"));

    const shift = memory.detectMoodShift("s1");
    expect(shift.shift_type).toBe("improving");
    expect(shift.from_emotion).toBe("sadness");
    expect(shift.to_emotion).toBe("hope");
  });

  it("detects declining mood shift", () => {
    memory.addTurn("s1", "I got the job!", makeEmotion("excitement", 9), makeIntent("celebrating"));
    memory.addTurn("s1", "They rescinded the offer", makeEmotion("sadness", 8), makeIntent());

    const shift = memory.detectMoodShift("s1");
    expect(shift.shift_type).toBe("declining");
  });

  it("detects intensifying", () => {
    memory.addTurn("s1", "I'm annoyed", makeEmotion("anger", 4), makeIntent("venting"));
    memory.addTurn("s1", "I'm furious now", makeEmotion("anger", 9), makeIntent("venting"));

    const shift = memory.detectMoodShift("s1");
    expect(shift.shift_type).toBe("intensifying");
  });

  it("returns none when less than 2 turns", () => {
    memory.addTurn("s1", "Hello", makeEmotion("neutral", 2), makeIntent("sharing"));
    const shift = memory.detectMoodShift("s1");
    expect(shift.shift_type).toBe("none");
  });

  it("builds strategy context", () => {
    memory.addTurn("s1", "I failed", makeEmotion("sadness", 8, "fear"), makeIntent());
    memory.addTurn("s1", "Trying to stay positive", makeEmotion("hope", 5), makeIntent("sharing"));

    const ctx = memory.getContextForStrategy("s1");
    expect(ctx).toContain("sadness");
    expect(ctx).toContain("hope");
    expect(ctx).toContain("Recent mood shift");
  });

  it("respects max turns", () => {
    const small = new EmotionalMemory(3);
    for (let i = 0; i < 5; i++) {
      small.addTurn("s1", `msg ${i}`, makeEmotion("neutral", 3), makeIntent());
    }
    expect(small.getTimeline("s1")).toHaveLength(3);
  });

  it("clears session", () => {
    memory.addTurn("s1", "hi", makeEmotion("happiness", 6), makeIntent("sharing"));
    memory.clearSession("s1");
    expect(memory.getTimeline("s1")).toEqual([]);
  });

  it("isolates sessions", () => {
    memory.addTurn("s1", "sad", makeEmotion("sadness", 7), makeIntent());
    memory.addTurn("s2", "happy", makeEmotion("happiness", 8), makeIntent("celebrating"));

    expect(memory.getTimeline("s1")[0].primary_emotion).toBe("sadness");
    expect(memory.getTimeline("s2")[0].primary_emotion).toBe("happiness");
  });
});
