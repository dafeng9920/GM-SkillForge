/**
 * Application Entry Point
 *
 * Exports the main App component for the L4 Workbench.
 *
 * @module index
 */

export { App } from './App';
export { L4Workbench } from './views';
export {
  // Actions
  fetchCognition10d,
  adoptWorkItem,
  clearDivergence,
  clearWork,
  setActivePanel,
  setCognitionData,
  setWorkItem,
  setError,
  // Validation helpers
  validateCognitionData,
  checkOverallPolicyPassed,
  checkCriticalDimensionsPassed,
  determineBlockedState,
  determineAdoptEnabled,
  // Constants
  CRITICAL_DIMENSIONS,
  MIN_PASS_COUNT,
  ERROR_MESSAGES,
  DIMENSION_LABELS,
} from './store/l4Slice';
export type {
  // State types
  L4State,
  Cognition10dData,
  Dimension,
  WorkItem,
  BlockedState,
  ExecutionReceipt,
} from './store/l4Slice';
export { store } from './store';
export type { RootState, AppDispatch } from './store';
export type {
  GateDecision,
  N8nErrorEnvelope,
  N8nSuccessEnvelope,
  RunIntentData,
  RunIntentResponse,
  FetchPackData,
  FetchPackResponse,
  RagResultItem,
  QueryRagData,
  QueryRagResponse,
  FiveStageId,
  FiveStageStatus,
  FiveStageItem,
  FiveStageViewModel,
  ThreeCardKind,
  ThreeCard,
  ThreeCardsViewModel,
  OrchestrationProjection,
} from './types/orchestrationProjection';
export {
  mockRunIntentAllow,
  mockFetchPackAllow,
  mockQueryRagAllow,
  mockRunIntentBlocked,
  mockProjectionAllow,
  mockProjectionBlocked,
} from './mocks/orchestrationProjection.mock';
export {
  mapToOrchestrationProjection,
} from './mappers/orchestrationProjectionMapper';
export type {
  ProjectionMapperInput,
} from './mappers/orchestrationProjectionMapper';
