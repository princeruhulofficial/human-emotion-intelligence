import OpenAI from "openai";
import { z } from "zod";
import {
  HEIConfig,
  HEIResponse,
  EmotionResult,
  IntentResult,
  StrategyResult,
  EvaluationResult,
  EmotionResultSchema,
  IntentResultSchema,
  StrategyResultSchema,
  EvaluationResultSchema,
  HEIError,
  HEIValidationError,
} from "./types";
import {
  EMOTION_SYSTEM_PROMPT,
  INTENT_SYSTEM_PROMPT,
  STRATEGY_SYSTEM_PROMPT,
  EVALUATION_SYSTEM_PROMPT,
  REWRITE_SYSTEM_PROMPT,
} from "./prompts";
import { EmotionalMemory, type MoodShift } from "./memory";

const MAX_MESSAGE_LENGTH = 8000;

export class HEI {
  private client: OpenAI;
  private model: string;
  public memory: EmotionalMemory;

  constructor(config: HEIConfig & { memory?: EmotionalMemory } = { apiKey: "" }) {
    this.client = new OpenAI({
      apiKey: config.apiKey,
      baseURL: config.baseURL,
      timeout: config.timeout ?? 30_000,
      maxRetries: config.maxRetries ?? 2,
    });
    this.model = config.model ?? "gpt-4o-mini";
    this.memory = config.memory ?? new EmotionalMemory();
  }

  private validateMessage(message: string): string {
    if (message == null) {
      throw new HEIValidationError("message cannot be null or undefined");
    }
    if (typeof message !== "string") {
      throw new HEIValidationError("message must be a string");
    }

    const cleaned = message.trim();
    if (!cleaned) {
      throw new HEIValidationError("message cannot be empty");
    }
    if (cleaned.length > MAX_MESSAGE_LENGTH) {
      throw new HEIValidationError(
        `message too long (${cleaned.length} chars). Max allowed: ${MAX_MESSAGE_LENGTH}`
      );
    }
    return cleaned;
  }

  private async chatJson<T>(
    system: string,
    user: string,
    schema: z.ZodType<T>
  ): Promise<T> {
    try {
      const response = await this.client.chat.completions.create({
        model: this.model,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
        temperature: 0.2,
        response_format: { type: "json_object" },
      });

      const content = response.choices[0]?.message?.content ?? "{}";
      const parsed = JSON.parse(content);
      return schema.parse(parsed);
    } catch (err: any) {
      if (err instanceof z.ZodError) {
        throw new HEIError(`Schema validation failed: ${err.message}`);
      }
      throw new HEIError(`LLM call failed: ${err?.message ?? String(err)}`);
    }
  }

  async analyzeEmotion(message: string): Promise<EmotionResult> {
    return this.chatJson<EmotionResult>(
      EMOTION_SYSTEM_PROMPT,
      `Analyze the emotional content of this message:\n\n"${message}"`,
      EmotionResultSchema
    );
  }

  async detectIntent(message: string, emotionContext?: string): Promise<IntentResult> {
    let userContent = `Message: ${message}`;
    if (emotionContext) {
      userContent += `\n\nDetected emotion context: ${emotionContext}`;
    }

    return this.chatJson<IntentResult>(
      INTENT_SYSTEM_PROMPT,
      userContent,
      IntentResultSchema
    );
  }

  async planStrategy(
    message: string,
    emotion: EmotionResult,
    intent: IntentResult,
    memoryContext?: string | null
  ): Promise<StrategyResult> {
    let context = `User message: ${message}

Emotion analysis:
- Primary: ${emotion.primary}
- Secondary: ${emotion.secondary ?? "null"}
- Hidden: ${emotion.hidden ?? "null"}
- Intensity: ${emotion.intensity}/10
- Confidence: ${emotion.confidence}

Intent analysis:
- Primary intent: ${intent.primary_intent}
- Confidence: ${intent.confidence}`;

    if (memoryContext) {
      context += `\n\nPrevious emotional context from this conversation:\n${memoryContext}`;
    }

    return this.chatJson<StrategyResult>(
      STRATEGY_SYSTEM_PROMPT,
      context,
      StrategyResultSchema
    );
  }

  /**
   * Full pipeline: Emotion → Intent → Strategy
   * Pass sessionId to enable Emotional Memory across turns.
   */
  async analyze(message: string, sessionId?: string): Promise<HEIResponse> {
    const clean = this.validateMessage(message);

    const emotion = await this.analyzeEmotion(clean);

    const emotionContext =
      `${emotion.primary} (intensity ${emotion.intensity}/10)` +
      (emotion.hidden ? `, hidden: ${emotion.hidden}` : "");

    const intent = await this.detectIntent(clean, emotionContext);

    const memoryContext = sessionId
      ? this.memory.getContextForStrategy(sessionId)
      : null;

    const strategy = await this.planStrategy(clean, emotion, intent, memoryContext);

    if (sessionId) {
      this.memory.addTurn(sessionId, clean, emotion, intent);
    }

    return {
      emotion,
      intent,
      strategy,
      raw_message: clean,
      model_used: this.model,
    };
  }

  /** Convenience helper for mood shift detection */
  getMoodShift(sessionId: string): MoodShift {
    return this.memory.detectMoodShift(sessionId);
  }

  async evaluateResponse(
    originalMessage: string,
    generatedResponse: string,
    strategy: StrategyResult
  ): Promise<EvaluationResult> {
    const clean = this.validateMessage(originalMessage);
    if (!generatedResponse?.trim()) {
      throw new HEIValidationError("generatedResponse cannot be empty");
    }

    const prompt = `Original user message:
${clean}

Strategy that should have been followed:
${JSON.stringify(strategy, null, 2)}

Generated response to evaluate:
${generatedResponse}`;

    return this.chatJson<EvaluationResult>(
      EVALUATION_SYSTEM_PROMPT,
      prompt,
      EvaluationResultSchema
    );
  }

  async rewrite(
    originalMessage: string,
    previousResponse: string,
    strategy: StrategyResult,
    feedback: string
  ): Promise<string> {
    const prompt = `Original user message:
${originalMessage}

Strategy to follow:
${JSON.stringify(strategy, null, 2)}

Previous (weak) response:
${previousResponse}

Feedback on what needs improvement:
${feedback}

Now write a significantly better response.`;

    try {
      const response = await this.client.chat.completions.create({
        model: this.model,
        messages: [
          { role: "system", content: REWRITE_SYSTEM_PROMPT },
          { role: "user", content: prompt },
        ],
        temperature: 0.6,
      });

      return (response.choices[0]?.message?.content ?? "").trim();
    } catch (err: any) {
      throw new HEIError(`Rewrite failed: ${err?.message ?? String(err)}`);
    }
  }

  /**
   * Evaluate + auto-rewrite if quality is low
   */
  async improveResponse(
    originalMessage: string,
    generatedResponse: string,
    strategy: StrategyResult,
    maxAttempts = 1
  ): Promise<{ response: string; evaluation: EvaluationResult }> {
    let current = generatedResponse;
    let evaluation = await this.evaluateResponse(originalMessage, current, strategy);

    let attempts = 0;
    while (evaluation.should_rewrite && attempts < maxAttempts) {
      attempts += 1;
      current = await this.rewrite(
        originalMessage,
        current,
        strategy,
        evaluation.feedback
      );
      evaluation = await this.evaluateResponse(originalMessage, current, strategy);
    }

    return { response: current, evaluation };
  }
}
