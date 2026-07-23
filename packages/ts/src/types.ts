import { z } from "zod";

export const PrimaryEmotionSchema = z.enum([
  // Plutchik-inspired core
  "happiness",
  "trust",
  "fear",
  "surprise",
  "sadness",
  "disgust",
  "anger",
  "anticipation",
  // Extended
  "anxiety",
  "excitement",
  "hope",
  "pride",
  "shame",
  "guilt",
  "loneliness",
  "frustration",
  "gratitude",
  "curiosity",
  "love",
  "optimism",
  "disappointment",
  "burnout",
  "neutral",
  "mixed",
]);

export type PrimaryEmotion = z.infer<typeof PrimaryEmotionSchema>;

export const EmotionalIntentSchema = z.enum([
  "seeking_comfort",
  "seeking_advice",
  "seeking_validation",
  "venting",
  "celebrating",
  "complaining",
  "sharing",
  "asking_question",
  "negotiating",
  "unknown",
]);

export type EmotionalIntent = z.infer<typeof EmotionalIntentSchema>;

export const ToneConfigSchema = z.object({
  warmth: z.number().min(0).max(1).default(0.7),
  directness: z.number().min(0).max(1).default(0.5),
  formality: z.number().min(0).max(1).default(0.4),
  optimism: z.number().min(0).max(1).default(0.5),
});

export type ToneConfig = z.infer<typeof ToneConfigSchema>;

export const AppraisalSignalsSchema = z.object({
  goal_relevance: z.number().min(0).max(1).default(0.5),
  coping_potential: z.number().min(0).max(1).default(0.5),
  agency: z.enum(["self", "other", "circumstances", "unknown"]).default("unknown"),
});

export type AppraisalSignals = z.infer<typeof AppraisalSignalsSchema>;

export const EmotionResultSchema = z.object({
  primary: PrimaryEmotionSchema,
  secondary: PrimaryEmotionSchema.nullable().optional(),
  hidden: PrimaryEmotionSchema.nullable().optional(),
  intensity: z.number().min(1).max(10),
  confidence: z.number().min(0).max(1),
  reasoning: z.string(),
  appraisal: AppraisalSignalsSchema.optional(),
});

export type EmotionResult = z.infer<typeof EmotionResultSchema>;

export const IntentResultSchema = z.object({
  primary_intent: EmotionalIntentSchema,
  secondary_intent: EmotionalIntentSchema.nullable().optional(),
  confidence: z.number().min(0).max(1),
  reasoning: z.string(),
});

export type IntentResult = z.infer<typeof IntentResultSchema>;

export const StrategyResultSchema = z.object({
  current_emotion: z.string(),
  target_outcome: z.string(),
  recommended_strategy: z.string(),
  tone: z
    .object({
      warmth: z.number().min(0).max(1),
      directness: z.number().min(0).max(1),
      formality: z.number().min(0).max(1),
      optimism: z.number().min(0).max(1),
    })
    .default({
      warmth: 0.7,
      directness: 0.5,
      formality: 0.4,
      optimism: 0.5,
    }),
  things_to_avoid: z.array(z.string()).default([]),
  suggested_approach: z.string(),
  reasoning: z.string(),
});

export type StrategyResult = z.infer<typeof StrategyResultSchema>;

export const EvaluationResultSchema = z.object({
  empathy_score: z.number().min(0).max(10),
  human_likeness: z.number().min(0).max(10),
  safety_score: z.number().min(0).max(10),
  clarity_score: z.number().min(0).max(10),
  felt_understood_score: z.number().min(0).max(10).default(5),
  overall_score: z.number().min(0).max(10),
  feedback: z.string(),
  should_rewrite: z.boolean(),
  rewrite_suggestion: z.string().nullable().optional(),
});

export type EvaluationResult = z.infer<typeof EvaluationResultSchema>;

export const HEIResponseSchema = z.object({
  emotion: EmotionResultSchema,
  intent: IntentResultSchema,
  strategy: StrategyResultSchema,
  raw_message: z.string(),
  model_used: z.string().optional(),
});

export type HEIResponse = z.infer<typeof HEIResponseSchema>;

export interface HEIConfig {
  apiKey: string;
  baseURL?: string;
  model?: string;
  timeout?: number;
  maxRetries?: number;
}

export class HEIError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "HEIError";
  }
}

export class HEIValidationError extends HEIError {
  constructor(message: string) {
    super(message);
    this.name = "HEIValidationError";
  }
}
