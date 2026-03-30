# GM LITE Plugin Local Release Judgment v1 Task Board

## Task Set
- `RJ1` local-use release criteria and threshold judgment
- `RJ2` blocker / non-blocker classification
- `RJ3` installed-state usability and stability judgment
- `RJ4` final local release decision and next-cut direction

## Release Order
- 第一波并行：`RJ1 + RJ2`
- 第二波串行：`RJ3`
- 第三波串行：`RJ4`

## Gate Rule
- `RJ1-RJ4` 三件套齐全后，才允许模块级收口
