# L4-A Frontend Runtime Bootstrap Report v1

**Task ID**: T-L4A-02
**Executor**: vs--cc3
**Date**: 2026-02-19
**Status**: ✅ Completed

---

## 1. Build Results

### npm install
```
added 124 packages, and audited 125 packages in 39s

8 packages are looking for funding
  run `npm fund` for details

2 moderate severity vulnerabilities
```

### npm run build
```
> l4-workbench@1.0.0 build
> tsc && vite build

vite v5.4.21 building for production...
transforming...
✓ 48 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.79 kB │ gzip:  0.48 kB
dist/assets/index-C3LmKrJl.js   203.35 kB │ gzip: 63.68 kB │ map: 697.59 kB
✓ built in 627ms
```

### npm run dev
```
VITE v5.4.21  ready in 280 ms

➜  Local:   http://localhost:5173/
➜  Network: http://10.14.164.222:5173/
➜  Network: http://192.168.101.49:5173/
➜  Network: http://192.168.101.72:5173/
➜  Network: http://172.18.224.1:5173/
```

---

## 2. Acceptance Criteria Verification

### ✅ AC1: 双窗口可见 (Divergence / Work)

**Implementation**:
- Divergence Window (Left): Displays 10D cognition assessment with dimension cards
- Work Window (Right): Displays adopted work items with execution receipt

**Location**: `ui/app/src/views/L4Workbench.tsx`

```
┌─────────────────────────────────────────────────────────┐
│ L4 Workbench Toolbar                                    │
├──────────────────────────┬──────────────────────────────┤
│   Divergence Window      │    Work Window               │
│   (CognitionPanel)       │    (WorkItemPanel)           │
│                          │                              │
│   10D Dimensions         │    Work Item Display         │
│   Summary Card           │    Execution Receipt         │
│   Rejection Reasons      │    Adoption Info             │
├──────────────────────────┴──────────────────────────────┤
│ Adopt Action Bar                                        │
└─────────────────────────────────────────────────────────┘
```

### ✅ AC2: Adopt-to-Work 可操作

**Implementation**:
- `adoptWorkItem` async thunk in Redux slice
- Adopt button enabled only when validation passes
- Work item populated with execution receipt on successful adopt

**Code Flow**:
1. User clicks "Load Passed" → Cognition data loaded
2. Validation runs → Adopt button enabled
3. User clicks "Adopt to Work Item" → `adoptWorkItem` dispatched
4. Work item created with execution receipt → Divergence cleared

### ✅ AC3: 缺字段会阻断 (Fail-Closed)

**Implementation**:
- `validateCognitionData()` checks all 10 required fields
- `determineAdoptEnabled()` returns false if validation fails
- Adopt button `disabled` attribute bound to `adopt.is_enabled`

**Test Case**:
- Load "Rejected" demo data → Adopt button stays disabled
- Missing fields trigger E001 error code in blocked state

### ✅ AC4: 执行回执字段可见

**Fields Displayed**:

| Field | Type | Display Location |
|-------|------|-----------------|
| `gate_decision` | 'ALLOWED' \| 'DENIED' \| 'PENDING' | Work Window > Execution Receipt |
| `release_allowed` | boolean | Work Window > Execution Receipt |
| `error_code` | string \| null | Work Window > Execution Receipt |
| `run_id` | string | Work Window > Execution Receipt |
| `permit_id` | string \| null | Work Window > Execution Receipt |
| `replay_pointer` | string \| null | Work Window > Execution Receipt |

**Code Location**: `ui/app/src/components/WorkItemPanel.tsx` (lines 664-710)

---

## 3. File Structure

```
ui/app/
├── index.html              # HTML entry point
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── tsconfig.node.json      # TypeScript node config
├── vite.config.ts          # Vite configuration
└── src/
    ├── main.tsx            # React entry point
    ├── App.tsx             # Main app component
    ├── index.ts            # Exports
    ├── store/
    │   ├── index.ts        # Store configuration
    │   └── l4Slice.ts      # Redux slice with types
    ├── components/
    │   ├── index.ts        # Component exports
    │   ├── CognitionPanel.tsx   # 10D display
    │   └── WorkItemPanel.tsx    # Work item display
    └── views/
        ├── index.ts        # View exports
        └── L4Workbench.tsx # Main dual-window layout
```

---

## 4. Dependencies

```json
{
  "dependencies": {
    "@reduxjs/toolkit": "^2.2.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^9.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.56",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.1.4"
  }
}
```

---

## 5. Validation Results

| Check | Description | Status |
|-------|-------------|--------|
| T1 | Free text in Left does NOT appear in Right | ✅ PASS |
| T4 | Deleting a field disables the Adopt button | ✅ PASS |
| AC1 | Dual windows visible | ✅ PASS |
| AC2 | Adopt-to-Work operational | ✅ PASS |
| AC3 | Fail-Closed validation | ✅ PASS |
| AC4 | Execution receipt visible | ✅ PASS |

---

## 6. Demo Controls

The application includes demo controls for testing:

- **Load Passed**: Loads mock cognition data that passes all validations
- **Load Rejected**: Loads mock cognition data with critical dimension failures
- **Clear Work**: Clears the Work Window

---

## 7. Execution Receipt Example

When Adopt succeeds, the following execution receipt is generated:

```json
{
  "gate_decision": "ALLOWED",
  "release_allowed": true,
  "error_code": null,
  "run_id": "RUN-M5X2K9L",
  "permit_id": "PERMIT-ABC12345",
  "replay_pointer": "replay://RUN-M5X2K9L/WI-A1B2C3D4"
}
```

---

## 8. How to Run

```bash
cd D:\GM-SkillForge\ui\app
npm install
npm run build  # Production build
npm run dev    # Development server at http://localhost:5173
```

---

## 9. Conclusion

The L4-A Dual Window Frontend runtime bootstrap is complete. All acceptance criteria have been met:

- ✅ Dual windows visible and functional
- ✅ Adopt-to-Work action operational
- ✅ Fail-Closed validation enforced
- ✅ Execution receipt fields displayed

**Ready for T-L4A-03 (Verification/E2E Testing)**

---

**Report Generated**: 2026-02-19
**Version**: v1.0
