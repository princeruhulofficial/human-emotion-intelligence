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
  AppraisalSignalsSchema,
} from "../types";
import { computeSalience } from "../memory";

describe("Zod golden parse tests", () => {
  describe("PrimaryEmotionSchema", () => {
    it("accepts Plutchik-aligned and extended labels", () => {
      expect(PrimaryEmotionSchema.parse("sadness")).toBe("sadness");
      expect(PrimaryEmotionSchema.parse("trust")).toBe("trust");
      expect(PrimaryEmotionSchema.parse("disgust")).toBe("disgust");
      expect(PrimaryEmotionSchema.parse("anticipation")).toBe("anticipation");
      expect(PrimaryEmotionSchema.parse("love")).toBe("love");
      expect(PrimaryEmotionSchema.parse("burnout")).toBe("burnout");
    });

    it("rejects invalid emotions", () => {
      expect(() => PrimaryEmotionSchema.parse("rage")).toThrow();
    });
  });

  describe("AppraisalSignalsSchema", () => {
    it("parses appraisal with defaults", () => {
      const a = AppraisalSignalsSchema.parse({});
      expect(a.goal_relevance).toBe(0.5);
      expect(a.agency).toBe("unknown");
    });

    it("accepts explicit agency", () => {
      const a = AppraisalSignalsSchema.parse({
        goal_relevance: 0.9,
        coping_potential: 0.2,
        agency: "circumstances",
      });
      expect(a.agency).toBe("circumstances");
    });
  });

  describe("EmotionResultSchema", () => {
    const valid = {
      primary: "sadness",
      secondary: "frustration",
      hidden: "fear",
      intensity: 8,
      confidence: 0.87,
      reasoning: "Loss with underlying fear",
      appraisal: {
        goal_relevance: 0.9,
        coping_potential: 0.3,
        agency: "circumstances",
      },
    };

    it("parses full payload with appraisal", () => {
      const result = EmotionResultSchema.parse(valid);
      expect(result.primary).toBe("sadness");
      expect(result.appraisal?.goal_relevance).toBe(0.9);
    });

    it("allows omitted appraisal", () => {
      const { appraisal, ...rest } = valid;
      const result = EmotionResultSchema.parse(rest);
      expect(result.primary).toBe("sadness");
    });
  });

  describe("EvaluationResultSchema", () => {
    it("defaults felt_understood_score when omitted", () => {
      const result = EvaluationResultSchema.parse({
        empathy_score: 8,
        human_likeness: 7,
        safety_score: 9,
        clarity_score: 8,
        overall_score: 8,
        feedback: "ok",
        should_rewrite: false,
      });
      expect(result.felt_understood_score).toBe(5);
    });

    it("accepts explicit felt_understood_score", () => {
      const result = EvaluationResultSchema.parse({
        empathy_score: 8,
        human_likeness: 7,
        safety_score: 9,
        clarity_score: 8,
        felt_understood_score: 9,
        overall_score: 8.5,
        feedback: "strong",
        should_rewrite: false,
      });
      expect(result.felt_understood_score).toBe(9);
    });
  });

  describe("StrategyResultSchema", () => {
    const base = {
      current_emotion: "sadness",
      target_outcome: "feel understood",
      recommended_strategy: "validate",
      suggested_approach: "Name the loss",
      reasoning: "High stakes",
    };

    it("applies tone default when omitted", () => {
      const result = StrategyResultSchema.parse(base);
      expect(result.tone.warmth).toBe(0.7);
    });
  });

  describe("computeSalience", () => {
    it("raises salience for high intensity + hidden + comfort intent", () => {
      const s = computeSalience(
        {
          primary: "sadness",
          intensity: 9,
          confidence: 0.9,
          reasoning: "x",
          hidden: "fear",
        },
        {
          primary_intent: "seeking_comfort",
          confidence: 0.8,
          reasoning: "x",
        }
      );
      expect(s).toBeGreaterThan(0.7);
    });

    it("stays moderate for mild neutral share", () => {
      const s = computeSalience(
        {
          primary: "neutral",
          intensity: 2,
          confidence: 0.5,
          reasoning: "x",
        },
        {
          primary_intent: "sharing",
          confidence: 0.5,
          reasoning: "x",
        }
      );
      expect(s).toBeLessThan(0.5);
    });
  });

  describe("HEIResponseSchema", () => {
    it("parses pipeline response", () => {
      const payload = {
        emotion: {
          primary: "disappointment",
          intensity: 7,
          confidence: 0.8,
          reasoning: "setback",
        },
        intent: {
          primary_intent: "seeking_comfort",
          confidence: 0.85,
          reasoning: "support",
        },
        strategy: {
          current_emotion: "disappointment",
          target_outcome: "feel understood",
          recommended_strategy: "validate",
          suggested_approach: "Acknowledge",
          reasoning: "stakes",
        },
        raw_message: "I guess my startup is over.",
      };
      const result = HEIResponseSchema.parse(payload);
      expect(result.emotion.primary).toBe("disappointment");
    });
  });
});
