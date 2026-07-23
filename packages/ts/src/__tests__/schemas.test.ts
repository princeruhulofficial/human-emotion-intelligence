import { describe, it, expect } from "vitest";
import {
  PrimaryEmotionSchema,
  EmotionalIntentSchema,
  ToneConfigSchema,
  EmotionResultSchema,
  IntentResultSchema,
  StrategyResultSchema,
  EvaluationResultSchema,
  HEIResponseSchema,
} from "../types";

describe("Zod golden parse tests", () => {
  // ---------- PrimaryEmotion ----------
  describe("PrimaryEmotionSchema", () => {
    it("accepts valid emotions", () => {
      expect(PrimaryEmotionSchema.parse("sadness")).toBe("sadness");
      expect(PrimaryEmotionSchema.parse("hope")).toBe("hope");
      expect(PrimaryEmotionSchema.parse("neutral")).toBe("neutral");
    });

    it("rejects invalid emotions", () => {
      expect(() => PrimaryEmotionSchema.parse("rage")).toThrow();
      expect(() => PrimaryEmotionSchema.parse("")).toThrow();
      expect(() => PrimaryEmotionSchema.parse(123)).toThrow();
    });
  });

  // ---------- EmotionalIntent ----------
  describe("EmotionalIntentSchema", () => {
    it("accepts valid intents", () => {
      expect(EmotionalIntentSchema.parse("seeking_comfort")).toBe("seeking_comfort");
      expect(EmotionalIntentSchema.parse("venting")).toBe("venting");
    });

    it("rejects invalid intents", () => {
      expect(() => EmotionalIntentSchema.parse("yelling")).toThrow();
    });
  });

  // ---------- ToneConfig ----------
  describe("ToneConfigSchema", () => {
    it("applies defaults when empty", () => {
      const tone = ToneConfigSchema.parse({});
      expect(tone.warmth).toBe(0.7);
      expect(tone.directness).toBe(0.5);
      expect(tone.formality).toBe(0.4);
      expect(tone.optimism).toBe(0.5);
    });

    it("accepts partial overrides", () => {
      const tone = ToneConfigSchema.parse({ warmth: 0.9 });
      expect(tone.warmth).toBe(0.9);
      expect(tone.directness).toBe(0.5);
    });

    it("rejects out-of-range values", () => {
      expect(() => ToneConfigSchema.parse({ warmth: 1.5 })).toThrow();
      expect(() => ToneConfigSchema.parse({ warmth: -0.1 })).toThrow();
    });
  });

  // ---------- EmotionResult ----------
  describe("EmotionResultSchema", () => {
    const valid = {
      primary: "sadness",
      secondary: "frustration",
      hidden: "fear",
      intensity: 8,
      confidence: 0.87,
      reasoning: "Loss with underlying fear",
    };

    it("parses a full valid payload", () => {
      const result = EmotionResultSchema.parse(valid);
      expect(result.primary).toBe("sadness");
      expect(result.intensity).toBe(8);
      expect(result.hidden).toBe("fear");
    });

    it("allows null optional fields", () => {
      const result = EmotionResultSchema.parse({
        ...valid,
        secondary: null,
        hidden: null,
      });
      expect(result.secondary).toBeNull();
      expect(result.hidden).toBeNull();
    });

    it("allows omitted optional fields", () => {
      const { secondary, hidden, ...minimal } = valid;
      const result = EmotionResultSchema.parse(minimal);
      expect(result.primary).toBe("sadness");
    });

    it("rejects intensity out of range", () => {
      expect(() =>
        EmotionResultSchema.parse({ ...valid, intensity: 0 })
      ).toThrow();
      expect(() =>
        EmotionResultSchema.parse({ ...valid, intensity: 11 })
      ).toThrow();
    });

    it("rejects confidence out of range", () => {
      expect(() =>
        EmotionResultSchema.parse({ ...valid, confidence: 1.5 })
      ).toThrow();
    });

    it("rejects missing required fields", () => {
      expect(() => EmotionResultSchema.parse({ primary: "sadness" })).toThrow();
    });
  });

  // ---------- IntentResult ----------
  describe("IntentResultSchema", () => {
    const valid = {
      primary_intent: "seeking_comfort",
      secondary_intent: "seeking_advice",
      confidence: 0.8,
      reasoning: "Needs emotional support",
    };

    it("parses valid payload", () => {
      const result = IntentResultSchema.parse(valid);
      expect(result.primary_intent).toBe("seeking_comfort");
    });

    it("allows null secondary_intent", () => {
      const result = IntentResultSchema.parse({
        ...valid,
        secondary_intent: null,
      });
      expect(result.secondary_intent).toBeNull();
    });

    it("rejects invalid intent enum", () => {
      expect(() =>
        IntentResultSchema.parse({ ...valid, primary_intent: "screaming" })
      ).toThrow();
    });
  });

  // ---------- StrategyResult (critical for previous CI bug) ----------
  describe("StrategyResultSchema", () => {
    const base = {
      current_emotion: "sadness",
      target_outcome: "feel understood",
      recommended_strategy: "validate then support",
      suggested_approach: "Acknowledge the loss without empty reassurance",
      reasoning: "User is grieving a failure",
    };

    it("parses full payload with tone", () => {
      const result = StrategyResultSchema.parse({
        ...base,
        tone: { warmth: 0.9, directness: 0.4, formality: 0.3, optimism: 0.5 },
        things_to_avoid: ["cheer up", "look on the bright side"],
      });
      expect(result.tone.warmth).toBe(0.9);
      expect(result.things_to_avoid).toHaveLength(2);
    });

    it("applies tone default when tone is omitted (golden case)", () => {
      const result = StrategyResultSchema.parse(base);
      expect(result.tone).toEqual({
        warmth: 0.7,
        directness: 0.5,
        formality: 0.4,
        optimism: 0.5,
      });
    });

    it("applies empty things_to_avoid default", () => {
      const result = StrategyResultSchema.parse(base);
      expect(result.things_to_avoid).toEqual([]);
    });

    it("rejects incomplete tone object", () => {
      expect(() =>
        StrategyResultSchema.parse({
          ...base,
          tone: { warmth: 0.9 }, // missing other required fields inside tone
        })
      ).toThrow();
    });

    it("rejects missing required strategy fields", () => {
      expect(() =>
        StrategyResultSchema.parse({
          current_emotion: "sadness",
        })
      ).toThrow();
    });
  });

  // ---------- EvaluationResult ----------
  describe("EvaluationResultSchema", () => {
    const valid = {
      empathy_score: 8,
      human_likeness: 7,
      safety_score: 9,
      clarity_score: 8,
      overall_score: 8,
      feedback: "Good empathy, slightly generic",
      should_rewrite: false,
      rewrite_suggestion: null,
    };

    it("parses valid evaluation", () => {
      const result = EvaluationResultSchema.parse(valid);
      expect(result.overall_score).toBe(8);
      expect(result.should_rewrite).toBe(false);
    });

    it("allows omitted rewrite_suggestion", () => {
      const { rewrite_suggestion, ...rest } = valid;
      const result = EvaluationResultSchema.parse(rest);
      expect(result.overall_score).toBe(8);
    });

    it("rejects scores out of range", () => {
      expect(() =>
        EvaluationResultSchema.parse({ ...valid, overall_score: 11 })
      ).toThrow();
      expect(() =>
        EvaluationResultSchema.parse({ ...valid, empathy_score: -1 })
      ).toThrow();
    });
  });

  // ---------- Full HEIResponse ----------
  describe("HEIResponseSchema", () => {
    it("parses a complete pipeline response", () => {
      const payload = {
        emotion: {
          primary: "sadness",
          secondary: null,
          hidden: "fear",
          intensity: 8,
          confidence: 0.9,
          reasoning: "Startup failure",
        },
        intent: {
          primary_intent: "seeking_comfort",
          secondary_intent: null,
          confidence: 0.85,
          reasoning: "Needs support",
        },
        strategy: {
          current_emotion: "sadness",
          target_outcome: "feel understood",
          recommended_strategy: "validate",
          suggested_approach: "Acknowledge the loss",
          reasoning: "User is grieving",
          // tone + things_to_avoid use defaults
        },
        raw_message: "I guess my startup is over.",
        model_used: "gpt-4o-mini",
      };

      const result = HEIResponseSchema.parse(payload);
      expect(result.emotion.primary).toBe("sadness");
      expect(result.intent.primary_intent).toBe("seeking_comfort");
      expect(result.strategy.tone.warmth).toBe(0.7);
      expect(result.raw_message).toContain("startup");
    });

    it("rejects broken nested emotion", () => {
      expect(() =>
        HEIResponseSchema.parse({
          emotion: { primary: "sadness" }, // incomplete
          intent: {
            primary_intent: "seeking_comfort",
            confidence: 0.8,
            reasoning: "x",
          },
          strategy: {
            current_emotion: "sadness",
            target_outcome: "x",
            recommended_strategy: "x",
            suggested_approach: "x",
            reasoning: "x",
          },
          raw_message: "hi",
        })
      ).toThrow();
    });
  });
});
