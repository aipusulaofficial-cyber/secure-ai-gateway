# Platform Contract Verification

This suite is the integration-test contract for the component.

## Required checks
1. Correlation/trace context is present.
2. Versioned policy is loaded and invalid policy fails closed.
3. Timeouts and retry budgets are bounded.
4. Security/cost/quality decisions are explicit.
5. Audit output contains decision, reason and timestamp.
6. Failure paths return deterministic errors.

## Evidence
Run repository-specific tests and publish their real output in CI. Do not replace measurements with placeholders or fabricated numbers.
