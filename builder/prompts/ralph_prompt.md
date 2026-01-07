# RALPH VALIDATION LOOP

You are in a validation loop for feature #{feature_id}: "{feature_name}"

## VALIDATION TASK

Verify that the feature works correctly by following these steps:

{feature_steps}

## VALIDATION RULES

1. **If ALL steps pass:**
   - Output: `<promise>FEATURE_{feature_id}_VALIDATED</promise>`
   - This signals validation is complete

2. **If ANY step fails:**
   - Document the specific failure
   - Attempt to fix the issue
   - Re-run the validation
   - Continue until fixed or max attempts reached

## CURRENT STATUS

- **Attempt:** {attempt_count} / {max_attempts}
- **Last Error:** {last_error}

## SELF-CORRECTION PROCESS

When a step fails:

1. **Identify** - What exactly failed?
2. **Diagnose** - Why did it fail?
3. **Fix** - Make the necessary code changes
4. **Re-test** - Run the failing step again
5. **Repeat** - Until the step passes or you've exhausted options

## PROMISE-BASED COMPLETION

The validation loop continues until you output a promise:

- Success: `<promise>FEATURE_{feature_id}_VALIDATED</promise>`
- Max Attempts: `<promise>FEATURE_{feature_id}_BLOCKED</promise>`

If blocked, document:
- What specifically is failing
- What you've tried
- Suggested next steps

## EXAMPLE FLOW

```
Attempt 1:
- Step 1: Navigate to page... PASS
- Step 2: Click button... PASS
- Step 3: Verify result... FAIL (expected "Success", got error message)

Diagnosing... The API endpoint returns 500 error.
Fixing... Updating the endpoint handler to catch the exception.

Attempt 2:
- Step 1: Navigate to page... PASS
- Step 2: Click button... PASS
- Step 3: Verify result... PASS

<promise>FEATURE_42_VALIDATED</promise>
```

---

Begin validation now. Follow each step carefully and output a promise when done.
