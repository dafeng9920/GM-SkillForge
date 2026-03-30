# GM LITE Field Test Validation v1 Task Board

## 状态
- module_id: `gm_lite_field_test_validation_v1`
- status: `IN_PROGRESS`

## 任务卡
- `FT1` 现场 happy path 验证
- `FT2` 现场 blockage / recovery 验证
- `FT3` 测试报告与现场结果一致性验证
- `FT4` 现场结论 / 缺口 / 下一步判断

## 放行顺序
1. 第一波并行：
   - `FT1`
   - `FT2`
2. 第二波串行：
   - `FT3`
3. 第三波串行：
   - `FT4`
