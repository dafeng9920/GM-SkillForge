/**
 * L4Workbench Component - UI v2 (Dual Chat Mode)
 *
 * Main layout component with Divergence (Left) and Work (Right) chat windows.
 * Layout: Desktop 40%/60% split, Mobile stacked with view switching.
 * Features: Independent chat streams, Mock backend simulation for interaction.
 *
 * @module views/L4Workbench
 */

import React, { useCallback, useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../store';
import {
  adoptWorkItem,
  clearDivergence,
  setCognitionData,
  addDivergenceMessage,
  addWorkMessage,
  setDivergenceInput,
  setWorkInput,
  setWorkSending,
  L4State,
  Cognition10dData,
  Message,
  CRITICAL_DIMENSIONS,
  DIMENSION_LABELS,
} from '../store/l4Slice';
import { CognitionPanel } from '../components/CognitionPanel';
import WorkItemPanel from '../components/WorkItemPanel';
import '../styles/l4-workbench.css';

// 简化的智能回复生成器
class SimpleSmartResponseGenerator {
  generateResponse(message: string, context: any): { content: string; triggerCognition: boolean } {
    const input = message.toLowerCase();
    const isFirstMessage = context.isFirstMessage;
    
    // 检测用户意图
    if (input.includes('写') && input.includes('skill')) {
      return {
        content: `🛠️ 好的！我来帮你创建一个skill。

为了给你最合适的帮助，请告诉我：

**基本信息：**
• 这个skill的主要功能是什么？
• 它需要处理什么类型的输入？
• 期望输出什么结果？

**技术要求：**
• 有特定的技术栈要求吗？
• 需要集成其他系统吗？
• 有性能或安全方面的考虑吗？

我会根据你的具体需求生成完整的skill结构、代码实现和文档。`,
        triggerCognition: true
      };
    }
    
    if (input.includes('复读机') || input.includes('模板') || input.includes('预置')) {
      return {
        content: `😅 你说得完全正确！我刚才的回复确实太模板化了。

让我重新来：我应该真正理解你的需求，而不是简单地匹配关键词。

**你刚才问的是要写个skill，对吧？**

我现在想了解的是：
• 你想要这个skill解决什么具体问题？
• 它应该在什么场景下使用？
• 你希望它有什么样的输入和输出？

这样我就能给你真正有用的、个性化的帮助。`,
        triggerCognition: false
      };
    }
    
    if (input.includes('帮助') || input.includes('help') || input.includes('能做什么')) {
      return {
        content: `🤖 我是L4工作台的AI助手，专门帮助开发者解决实际问题：

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

告诉我你的具体需求，我会给你最有针对性的帮助！`,
        triggerCognition: false
      };
    }
    
    if (isFirstMessage) {
      return {
        content: `👋 欢迎使用L4工作台！我是你的AI开发助手。

我可以帮你：
• 创建和优化skill
• 解决代码问题
• 进行技术分析
• 生成项目文档

有什么我可以帮你的吗？`,
        triggerCognition: true
      };
    }
    
    // 默认智能回复
    const responses = [
      "🤔 让我理解一下你的具体需求...",
      "💡 这个问题很有意思，我来分析一下...",
      "🔍 我正在处理你的请求，请稍等...",
      "⚡ 收到！让我来帮你解决这个问题..."
    ];
    
    return {
      content: responses[Math.floor(Math.random() * responses.length)],
      triggerCognition: message.length > 30
    };
  }
}

// ============================================
// Responsive Hook
// ============================================

function useIsMobile(): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 900);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return isMobile;
}

// ============================================
// Mock Data Generator
// ============================================

function generateMockCognitionData(status: 'PASSED' | 'REJECTED'): Cognition10dData {
  const dimensionOrder: Array<'L1' | 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7' | 'L8' | 'L9' | 'L10'> =
    ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9', 'L10'];

  const dimensions = dimensionOrder.map((dimId) => {
    const isCritical = CRITICAL_DIMENSIONS.includes(dimId);
    const baseScore = status === 'PASSED'
      ? (isCritical ? 80 : 70)
      : (isCritical ? 45 : 65);

    return {
      dim_id: dimId,
      label: DIMENSION_LABELS[dimId],
      score: baseScore + Math.random() * 15,
      threshold: 60,
      verdict: (status === 'PASSED' || !isCritical) && Math.random() > 0.2
        ? 'PASS' as const
        : 'FAIL' as const,
      evidence_ref: `AuditPack/cognition_10d/mock/${dimId}.md`,
    };
  });

  if (status === 'REJECTED') {
    dimensions.forEach((dim) => {
      if (CRITICAL_DIMENSIONS.includes(dim.dim_id)) {
        dim.verdict = 'FAIL';
        dim.score = 40 + Math.random() * 15;
      }
    });
  }

  const passCount = dimensions.filter((d) => d.verdict === 'PASS').length;

  return {
    intent_id: 'cognition_10d',
    status,
    repo_url: 'https://github.com/skillforge/workflow-orchestration',
    commit_sha: 'a1b2c3d4e5f6789012345678901234567890abcd',
    at_time: new Date().toISOString(),
    rubric_version: '1.0.0',
    dimensions,
    overall_pass_count: passCount,
    rejection_reasons:
      status === 'REJECTED'
        ? ['Insufficient pass count', 'Critical dimension failure: L3, L5']
        : [],
    audit_pack_ref: 'AuditPack/cognition_10d/mock/',
    generated_at: new Date().toISOString(),
  };
}

// ============================================
// Sub-Components
// ============================================

const ProcessBar: React.FC<{
  steps: { id: string; label: string; status: 'idle' | 'active' | 'passed' | 'blocked' }[];
}> = ({ steps }) => (
  <div className="l4-process-bar">
    {steps.map((step, index) => (
      <React.Fragment key={step.id}>
        <div className={`l4-process-step l4-process-step--${step.status}`}>
          {step.status === 'passed' && <span>✓</span>}
          {step.status === 'blocked' && <span>✕</span>}
          {step.status === 'active' && <span>▶</span>}
          <span>{step.label}</span>
        </div>
        {index < steps.length - 1 && (
          <span className="l4-process-arrow">→</span>
        )}
      </React.Fragment>
    ))}
  </div>
);

const MobileTabs: React.FC<{
  activePanel: 'divergence' | 'work';
  onSwitch: (panel: 'divergence' | 'work') => void;
}> = ({ activePanel, onSwitch }) => (
  <div className="l4-mobile-tabs">
    <button
      className={`l4-mobile-tab ${activePanel === 'divergence' ? 'l4-mobile-tab--active' : ''}`}
      onClick={() => onSwitch('divergence')}
    >
      🧠 Divergence
    </button>
    <button
      className={`l4-mobile-tab ${activePanel === 'work' ? 'l4-mobile-tab--active' : ''}`}
      onClick={() => onSwitch('work')}
    >
      📋 Work
    </button>
  </div>
);

// ============================================
// Main Component
// ============================================

export const L4Workbench: React.FC = () => {
  const dispatch = useAppDispatch();
  const l4State = useSelector((state: { l4: L4State }) => state.l4);
  const isMobile = useIsMobile();
  const [mobileView, setMobileView] = useState<'divergence' | 'work'>('divergence');

  // 初始化智能回复生成器
  const [smartGenerator] = useState(() => new SimpleSmartResponseGenerator());

  const { divergence, work, adopt } = l4State;

  // -- Divergence Handlers --

  const handleDivergenceSend = useCallback(() => {
    if (!divergence.inputValue.trim()) return;

    const userMsg: Message = {
      id: `msg-div-${Date.now()}`,
      role: 'user',
      content: divergence.inputValue,
      timestamp: Date.now()
    };
    dispatch(addDivergenceMessage(userMsg));
    dispatch(setDivergenceInput(''));

    // 使用智能回复生成器
    setTimeout(() => {
      const context = {
        isFirstMessage: divergence.messages.length === 0,
        messageHistory: divergence.messages,
        userPreferences: {}
      };

      const smartResponse = smartGenerator.generateResponse(userMsg.content, context);

      const aiMsg: Message = {
        id: `msg-div-ai-${Date.now()}`,
        role: 'assistant',
        content: smartResponse.content,
        timestamp: Date.now()
      };
      dispatch(addDivergenceMessage(aiMsg));

      if (smartResponse.triggerCognition) {
        dispatch(setCognitionData(generateMockCognitionData('PASSED')));
      }
    }, 1000);
  }, [divergence.inputValue, divergence.messages, dispatch, smartGenerator]);


  // -- Work Handlers --

  const handleWorkSend = useCallback(() => {
    if (!work.inputValue.trim()) return;

    const userMsg: Message = {
      id: `msg-work-${Date.now()}`,
      role: 'user',
      content: work.inputValue,
      timestamp: Date.now()
    };
    dispatch(addWorkMessage(userMsg));
    dispatch(setWorkInput(''));
    dispatch(setWorkSending(true));

    // 使用智能回复生成器
    setTimeout(() => {
      dispatch(setWorkSending(false));
      
      const context = {
        isFirstMessage: work.messages.length === 0,
        messageHistory: work.messages,
        workMode: true
      };

      const smartResponse = smartGenerator.generateResponse(userMsg.content, context);
      
      const aiMsg: Message = {
        id: `msg-work-ai-${Date.now()}`,
        role: 'assistant',
        content: smartResponse.content,
        timestamp: Date.now()
      };
      dispatch(addWorkMessage(aiMsg));
    }, 1500);
  }, [work.inputValue, work.messages, dispatch, smartGenerator]);


  // -- Adopt & Existing Handlers --

  const handleAdopt = useCallback(() => {
    if (!adopt.is_enabled || adopt.is_processing) return;

    dispatch(adoptWorkItem({
      reason_card_id: `RC-${Date.now().toString(36).toUpperCase()}`,
      requester_id: 'l4-workbench-user',
      options: { verify_immediately: true, preserve_raw_content: true },
    }));

    // Switch to work view on adopt
    if (isMobile) setMobileView('work');

    // Add system message to Work Chat
    setTimeout(() => {
      dispatch(addWorkMessage({
        id: `sys-adopt-${Date.now()}`,
        role: 'system',
        content: "🎯 **工作项已成功采纳**\n\n• 发散分析结果已转移到工作窗口\n• 执行上下文已初始化\n• 治理框架已激活\n• 准备开始具体执行任务\n\n您现在可以开始执行相关的工作项了！",
        timestamp: Date.now()
      }));
    }, 500);

  }, [dispatch, adopt.is_enabled, adopt.is_processing, isMobile]);



  // -- Execute Handler --
  const handleExecute = useCallback(() => {
    if (work.blocked_state.is_blocked || !work.work_item) return;

    const msg: Message = {
      id: `sys-exec-${Date.now()}`,
      role: 'system',
      content: "🚀 **执行序列已启动**\n\n• 验证治理策略中...\n• 检查执行权限...\n• 分发任务到执行内核...\n• 启动审计跟踪...\n\n⏱️ 执行进行中，请稍候...",
      timestamp: Date.now()
    };
    dispatch(addWorkMessage(msg));
  }, [dispatch, work.blocked_state.is_blocked, work.work_item]);

  // Derived State for Process Bar (Visual Only)
  const getProcessSteps = () => [
    { id: '1', label: '1 Divergence', status: divergence.messages.length > 0 ? (divergence.cognition_data ? 'passed' : 'active') : 'idle' },
    { id: '2', label: '2 Cognition', status: divergence.cognition_data ? (divergence.cognition_data.status === 'PASSED' ? 'passed' : 'blocked') : (divergence.messages.length > 0 ? 'active' : 'idle') },
    { id: '3', label: '3 Adopt', status: work.work_item ? 'passed' : (divergence.cognition_data?.status === 'PASSED' ? 'active' : 'idle') },
    { id: '4', label: '4 Execution', status: work.work_item?.execution_receipt ? 'passed' : (work.work_item ? 'active' : 'idle') },
  ];

  return (
    <div className="l4-workbench">
      {/* Header */}
      <header className="l4-header">
        <div className="l4-header__left">
          <div className="l4-header__logo">
            <span className="l4-header__logo-icon">⚡</span>
            <span>L4 Workbench</span>
          </div>
          {!isMobile && (
            <div className="l4-window__subtitle">
              SkillForge / Governance / L4 Dual Window
            </div>
          )}
        </div>
        {!isMobile && <ProcessBar steps={getProcessSteps() as any} />}
        <div className="l4-header__right">
          <button className="l4-btn l4-btn--sm l4-btn--outline" onClick={() => dispatch(clearDivergence())}>Reset</button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="l4-main" style={{ display: 'flex', flex: 1, minHeight: 0, height: '100%' }}>
        {/* Left Pane: Divergence */}
        <div
          className={`l4-pane l4-pane--divergence l4-pane-left ${isMobile && mobileView !== 'divergence' ? 'hidden' : ''}`}
          style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}
        >
          <CognitionPanel
            messages={divergence.messages}
            inputValue={divergence.inputValue}
            onInputChange={(val) => dispatch(setDivergenceInput(val))}
            onSend={handleDivergenceSend}
            cognitionData={divergence.cognition_data}
            isLoading={divergence.is_loading}
            error={divergence.error}
          />
        </div>

        {/* Center Boundary (Desktop Only) */}
        {/* Center Boundary (Desktop Only) - Visual Divider handled by CSS */}
        {/* {!isMobile && <AdoptBoundary ... />} */}

        {/* Right Pane: Work */}
        <div
          className={`l4-pane l4-pane--work l4-pane-right ${isMobile && mobileView !== 'work' ? 'hidden' : ''}`}
          style={{ display: 'flex', flexDirection: 'column', flex: 1, height: '100%', minHeight: 0 }}
        >
          <WorkItemPanel
            // Chat
            workMessages={work.messages}
            workInput={work.inputValue}
            workSending={work.isSending}
            onWorkInputChange={(val) => dispatch(setWorkInput(val))}
            onWorkSend={handleWorkSend}

            // Adoption (MVP)
            onAdopt={handleAdopt}
            canAdopt={!!(adopt.is_enabled && !work.work_item)}

            // Governance
            permitStatus={work.work_item?.execution_receipt?.permit_status || 'PENDING'}
            gateDecision={work.work_item?.execution_receipt?.gate_decision || 'IDLE'}
            replayPointer={work.work_item?.execution_receipt?.replay_pointer || '-'}

            // Context
            workItem={work.work_item}

            // Execution
            onExecute={handleExecute}
            executeDisabled={work.isSending || work.blocked_state.is_blocked || !work.work_item}
            receiptText={work.work_item?.execution_receipt ? JSON.stringify(work.work_item.execution_receipt, null, 2) : undefined}

            // Blocking
            blockedCode={work.blocked_state.is_blocked ? work.blocked_state.error_code : null}
            blockedReason={work.blocked_state.error_message}

            // Legacy
            isLoading={work.is_loading}
            error={work.error}
          />
        </div>
      </main>


      {/* Mobile Tabs */}
      {isMobile && (
        <MobileTabs
          activePanel={mobileView}
          onSwitch={(panel) => setMobileView(panel)}
        />
      )}
    </div>
  );
};
