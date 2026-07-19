import OpenAI from "openai";
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
} from "./types";
import {
  EMOTION_SYSTEM_PROMPT,
  INTENT_SYSTEM_PROMPT,
  STRATEGY_SYSTEM_PROMPT,
  EVALUATION_SYSTEM_PROMPT,
  REWRITE_SYSTEM_PROMPT,
} from "./prompts";

export class HEI {
  private client: OpenAI;
  private model: string;

  constructor(config: HEIConfig) {
    this.client = new OpenAI({
      apiKey: config.apiKey,
      baseURL: config.baseURL,
    });
    this.model = config.model ?? "gpt-4o-mini";
  }

  private async chatJson<T>(system: string, user: string, schema: any): Promise<T> {
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
    return schema.parse(parsed) as T;
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
    intent: IntentResult
  ): Promise<StrategyResult> {
    const context = `User message: ${message}

Emotion analysis:
- Primary: ${emotion.primary}
- Secondary: ${emotion.secondary ?? "null"}
- Hidden: ${emotion.hidden ?? "null"}
- Intensity: ${emotion.intensity}/10
- Confidence: ${emotion.confidence}

Intent analysis:
- Primary intent: ${intent.primary_intent}
- Confidence: ${intent.confidence}`;

    return this.chatJson<StrategyResult>(
      STRATEGY_SYSTEM_PROMPT,
      context,
      StrategyResultSchema
    );
  }

  /**
   * Full pipeline: Emotion → Intent → Strategy
   */
  async analyze(message: string): Promise<HEIResponse> {
    const emotion = await this.analyzeEmotion(message);

    const emotionContext =
      `${emotion.primary} (intensity ${emotion.intensity}/10)` +
      (emotion.hidden ? `, hidden: ${emotion.hidden}` : "");

    const intent = await this.detectIntent(message, emotionContext);
    const strategy = await this.planStrategy(message, emotion, intent);

    return {
      emotion,
      intent,
      strategy,
      raw_message: message,
      model_used: this.model,
    };
  }

  async evaluateResponse(
    originalMessage: string,
    generatedResponse: string,
    strategy: StrategyResult
  ): Promise<EvaluationResult> {
    const prompt = `Original user message:
${originalMessage}

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

    const response = await this.client.chat.completions.create({
      model: this.model,
      messages: [
        { role: "system", content: REWRITE_SYSTEM_PROMPT },
        { role: "user", content: prompt },
      ],
      temperature: 0.6,
    });

    return (response.choices[0]?.message?.content ?? "").trim();
  }

  /**
   * Evaluate + auto-rewrite if quality is low
   */
  async improveResponse(
    originalMessage: string,
    generatedResponse: string,
    strategy: StrategyResult
  ): Promise<{ response: string; evaluation: EvaluationResult }> {
    const evaluation = await this.evaluateResponse(
      originalMessage,
      generatedResponse,
      strategy
    );

    if (!evaluation.should_rewrite) {
      return { response: generatedResponse, evaluation };
    }

    const improved = await this.rewrite(
      originalMessage,
      generatedResponse,
      strategy,
      evaluation.feedback
    );

    const finalEval = await this.evaluateResponse(
      originalMessage,
      improved,
      strategy
    );

    return { response: improved, evaluation: finalEval };
  }
}
