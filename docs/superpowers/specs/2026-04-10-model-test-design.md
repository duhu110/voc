# Complaint Taxonomy Validator Model Test Design

## Goal

Add a pytest-based online model validation suite under `voc_agent/complaint_taxonomy_validator/tests/model_test` that:

- reads the configured OpenAI-compatible endpoint from the current repository env
- reads the model list from `model_list.text`
- derives five prompt cases from the existing prompt sample
- sends those prompts directly to each configured model through the OpenAI SDK
- writes success and failure artifacts into `voc_agent/complaint_taxonomy_validator/tests/model_test/output`

## Scope

This design only covers test-side code and test artifacts. It does not change the application runtime path used by `manual_validate_ticket.py`.

## Input Sources

- Prompt sample: `voc_agent/complaint_taxonomy_validator/tests/prompt_sample_2024121013451359982515.txt`
- Model list: `voc_agent/complaint_taxonomy_validator/tests/model_test/model_list.text`
- Endpoint config: `voc_agent/.env` through existing settings loading

## Prompt Case Design

Five prompt cases will reuse the sample prompt structure and category/tag lists, but vary the original ticket content and expected emphasis:

1. Base deny-order complaint copied from the sample ticket
2. Deny-order complaint with stronger channel responsibility hints
3. Auto-renew and continued charging complaint
4. Billing and refund-focused dispute
5. Network-quality complaint with urgency and escalation risk

Each case keeps the JSON-only output requirement so results are comparable across models.

## Output Design

Each invocation writes a JSON artifact containing:

- `case_name`
- `model_name`
- `prompt_path`
- `status`
- `error_type`
- `error_message`
- `duration_ms`
- `timestamp`

Success artifacts also include request metadata and raw model output. A run-level summary JSON will be written after the test completes.

## Failure Handling

- Timeout, API error, transport error, and malformed response all count as failures
- Failures are recorded to disk before the test asserts
- The pytest run fails if any model-case invocation fails

## Test Structure

- A helper module will build prompt cases, parse model IDs, execute calls, and write artifacts
- Unit-style pytest coverage will validate parsing and prompt generation first
- One integration pytest will execute live model calls
