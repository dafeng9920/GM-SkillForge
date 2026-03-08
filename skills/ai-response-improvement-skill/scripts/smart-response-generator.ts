/**
 * 智能回复生成器
 * 用于替代简单的关键词匹配，提供真正的语义理解和上下文感知
 */

export interface Intent {
  type: string;
  confidence: number;
  entities: Record<string, any>;
  context: string[];
}

export interface ConversationContext {
  userId: string;
  sessionId: string;
  messageHistory: Message[];
  userPreferences: Record<string, any>;
  currentTopic: string | null;
  emotionalState: 'positive' | 'neutral' | 'negative' | 'frustrated';
}

export interface SmartResponse {
  content: string;
  confidence: number;
  intent: Intent;
  followUpSuggestions: string[];
  triggerActions: string[];
}

export class SmartResponseGenerator {
  private intentPatterns = {
    skill_request: {
      patterns: [
        /写.*skill/i,
        /创建.*skill/i,
        /帮.*做.*skill/i,
        /skill.*怎么/i,
        /能.*帮.*写/i
      ],
      confidence: 0.9
    },
    code_help: {
      patterns: [
        /代码/i,
        /函数/i,
        /bug/i,
        /实现/i,
        /怎么.*写/i,
        /如何.*做/i
      ],
      confidence: 0.8
    },
    system_complaint: {
      patterns: [
        /复读机/i,
        /模板/i,
        /预置.*回复/i,
        /不智能/i,
        /重复/i,
        /没用/i
      ],
      confidence: 0.95
    },
    feature_inquiry: {
      patterns: [
        /能做什么/i,
        /功能/i,
        /帮助/i,
        /help/i,
        /怎么用/i
      ],
      confidence: 0.7
    },
    greeting: {
      patterns: [
        /你好/i,
        /hello/i,
        /hi/i,
        /嗨/i
      ],
      confidence: 0.6
    }
  };

  /**
   * 检测用户意图
   */
  detectIntent(message: string): Intent {
    let bestMatch: Intent = {
      type: 'unknown',
      confidence: 0,
      entities: {},
      context: []
    };

    for (const [intentType, config] of Object.entries(this.intentPatterns)) {
      for (const pattern of config.patterns) {
        if (pattern.test(message)) {
          if (config.confidence > bestMatch.confidence) {
            bestMatch = {
              type: intentType,
              confidence: config.confidence,
              entities: this.extractEntities(message, intentType),
              context: this.extractContext(message)
            };
          }
        }
      }
    }

    return bestMatch;
  }

  /**
   * 提取实体信息
   */
  private extractEntities(message: string, intentType: string): Record<string, any> {
    const entities: Record<string, any> = {};

    switch (intentType) {
      case 'skill_request':
        // 提取skill类型、功能描述等
        const skillTypeMatch = message.match(/(API|数据库|文件|网络|UI|测试).*skill/i);
        if (skillTypeMatch) {
          entities.skillType = skillTypeMatch[1];
        }
        break;
      
      case 'code_help':
        // 提取编程语言、技术栈等
        const langMatch = message.match(/(JavaScript|TypeScript|Python|Java|React|Vue)/i);
        if (langMatch) {
          entities.language = langMatch[1];
        }
        break;
    }

    return entities;
  }

  /**
   * 提取上下文信息
   */
  private extractContext(message: string): string[] {
    const context: string[] = [];
    
    // 技术相关上下文
    if (/前端|UI|界面/i.test(message)) context.push('frontend');
    if (/后端|API|服务器/i.test(message)) context.push('backend');
    if (/数据库|SQL/i.test(message)) context.push('database');
    if (/测试|单元测试/i.test(message)) context.push('testing');
    
    return context;
  }

  /**
   * 生成智能回复
   */
  async generateResponse(
    message: string, 
    context: ConversationContext
  ): Promise<SmartResponse> {
    const intent = this.detectIntent(message);
    const isFirstMessage = context.messageHistory.length === 0;
    
    let responseContent = '';
    let followUpSuggestions: string[] = [];
    let triggerActions: string[] = [];

    switch (intent.type) {
      case 'skill_request':
        responseContent = this.generateSkillRequestResponse(message, intent, context);
        followUpSuggestions = [
          '描述skill的具体功能',
          '说明输入输出格式',
          '提及特殊要求或约束'
        ];
        triggerActions = ['show_skill_template', 'prepare_code_editor'];
        break;

      case 'system_complaint':
        responseContent = this.generateApologyAndImprovement(message, context);
        followUpSuggestions = [
          '请具体描述你的需求',
          '告诉我哪里可以改进',
          '让我重新理解你的问题'
        ];
        triggerActions = ['improve_response_quality'];
        break;

      case 'code_help':
        responseContent = this.generateCodeHelpResponse(message, intent, context);
        followUpSuggestions = [
          '提供具体的代码示例',
          '说明遇到的具体问题',
          '描述期望的实现效果'
        ];
        triggerActions = ['prepare_code_examples'];
        break;

      case 'feature_inquiry':
        responseContent = this.generateFeatureResponse(context);
        followUpSuggestions = [
          '尝试具体的功能',
          '描述你的使用场景',
          '告诉我你想解决什么问题'
        ];
        break;

      case 'greeting':
        responseContent = this.generateGreetingResponse(isFirstMessage);
        followUpSuggestions = [
          '告诉我你想做什么',
          '描述你的项目需求',
          '问我任何技术问题'
        ];
        break;

      default:
        responseContent = this.generateContextualResponse(message, context);
        followUpSuggestions = ['请提供更多详细信息'];
    }

    return {
      content: responseContent,
      confidence: intent.confidence,
      intent,
      followUpSuggestions,
      triggerActions
    };
  }

  private generateSkillRequestResponse(
    message: string, 
    intent: Intent, 
    context: ConversationContext
  ): string {
    const skillType = intent.entities.skillType || '通用';
    
    return `🛠️ 好的！我来帮你创建一个${skillType}skill。

为了给你最合适的帮助，请告诉我：

**基本信息：**
• 这个skill的主要功能是什么？
• 它需要处理什么类型的输入？
• 期望输出什么结果？

**技术要求：**
• 有特定的技术栈要求吗？
• 需要集成其他系统吗？
• 有性能或安全方面的考虑吗？

我会根据你的具体需求生成完整的skill结构、代码实现和文档。`;
  }

  private generateApologyAndImprovement(
    message: string, 
    context: ConversationContext
  ): string {
    return `😅 你说得完全正确！我刚才的回复确实太模板化了，就像个"复读机"。

让我重新来：我应该真正理解你的需求，而不是简单地匹配关键词。

**你刚才问的是要写个skill，对吧？**

我现在想了解的是：
• 你想要这个skill解决什么具体问题？
• 它应该在什么场景下使用？
• 你希望它有什么样的输入和输出？

这样我就能给你真正有用的、个性化的帮助，而不是千篇一律的模板回复。`;
  }

  private generateCodeHelpResponse(
    message: string, 
    intent: Intent, 
    context: ConversationContext
  ): string {
    const language = intent.entities.language || '';
    const langText = language ? `${language}` : '';
    
    return `💻 我来帮你解决${langText}代码问题！

基于你的描述，我理解你需要代码方面的帮助。

**为了给你最准确的建议：**
• 能描述一下具体遇到的问题吗？
• 有相关的错误信息可以分享吗？
• 你期望的功能或效果是什么样的？

我会提供具体的代码示例和解决方案，而不是泛泛而谈的建议。`;
  }

  private generateFeatureResponse(context: ConversationContext): string {
    return `🤖 我是L4工作台的AI助手，专门帮助开发者解决实际问题：

**我的核心能力：**
• 🛠️ **Skill开发** - 创建完整的skill包，包括代码、文档、测试
• 💻 **代码助手** - 提供具体的代码实现和问题解决方案  
• 🔍 **技术分析** - 进行10维认知分析，评估技术方案
• 📋 **文档生成** - 自动生成技术文档、API文档等
• 🚀 **项目支持** - 协助项目架构设计和最佳实践

**我的特点：**
• 理解上下文，不是简单的关键词匹配
• 提供个性化的解决方案
• 生成可直接使用的代码和配置

告诉我你的具体需求，我会给你最有针对性的帮助！`;
  }

  private generateGreetingResponse(isFirstMessage: boolean): string {
    if (isFirstMessage) {
      return `👋 你好！欢迎使用L4工作台！

我是你的AI开发助手，可以帮你：
• 创建和优化skill
• 解决代码问题
• 进行技术分析
• 生成项目文档

有什么我可以帮你的吗？`;
    } else {
      return `👋 你好！有什么新的问题需要我帮助解决吗？`;
    }
  }

  private generateContextualResponse(
    message: string, 
    context: ConversationContext
  ): string {
    // 基于对话历史和用户偏好生成个性化回复
    const recentTopics = context.messageHistory
      .slice(-3)
      .map(msg => msg.content)
      .join(' ');

    if (recentTopics.includes('skill')) {
      return `🔄 我注意到我们之前在讨论skill相关的内容。你是想继续这个话题，还是有新的需求？

请告诉我具体想要什么帮助，我会提供更有针对性的建议。`;
    }

    return `🤔 我正在理解你的需求...

为了给你最好的帮助，能否提供更多具体信息？比如：
• 你想解决什么问题？
• 涉及什么技术栈？
• 有什么特殊要求？`;
  }
}

// 消息接口定义
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}