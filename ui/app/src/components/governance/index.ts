/**
 * Governance Components - Index
 *
 * @module components/governance
 */

export { PipelineStepPanel } from './PipelineStepPanel';
export type {
  PipelineStep,
  PipelineStepStatus,
  AuditLayer,
  AuditLayerStatus,
  PipelineStepPanelProps,
} from './PipelineStepPanel';

// TASK-MAIN-04A: Main Chain Step Panel
export { MainChainStepPanel, generateMockMainChainSteps } from './MainChainStepPanel';
export type {
  MainChainStep,
  MainChainStepId,
  MainChainStepStatus,
  MainChainStepPanelProps,
} from './MainChainStepPanel';

// TASK-MAIN-04B: Main Chain Status Panel (承接真实 RunResult & ArtifactManifest)
export { MainChainStatusPanel } from './MainChainStatusPanel';
export type { MainChainStatusPanelProps } from './MainChainStatusPanel';
