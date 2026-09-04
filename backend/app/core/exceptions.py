class ReviveException(Exception):
    """Base exception for all REVIVE operational and safety errors."""
    def __init__(self, message: str, code: str = "REVIVE_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class PolicyViolationException(ReviveException):
    """Raised when an action violates merchant policy."""
    def __init__(self, message: str, policy_name: str = "general"):
        super().__init__(message, code="POLICY_VIOLATION", status_code=422)
        self.policy_name = policy_name


class StoppingRuleException(ReviveException):
    """Raised when a stopping rule blocks further intervention."""
    def __init__(self, message: str, rule_name: str = "general"):
        super().__init__(message, code="STOPPING_RULE_TRIGGERED", status_code=422)
        self.rule_name = rule_name


class InvalidStateTransitionException(ReviveException):
    """Raised when an illegal state machine transition is attempted."""
    def __init__(self, current_state: str, target_state: str):
        message = f"Illegal transition from state '{current_state}' to '{target_state}'."
        super().__init__(message, code="INVALID_STATE_TRANSITION", status_code=409)
        self.current_state = current_state
        self.target_state = target_state


class IdempotencyConflictException(ReviveException):
    """Raised when duplicate action with same idempotency key is detected."""
    def __init__(self, key: str):
        message = f"Duplicate action detected for idempotency key '{key}'."
        super().__init__(message, code="IDEMPOTENCY_CONFLICT", status_code=409)
        self.key = key


class RazorpayIntegrationException(ReviveException):
    """Raised when Razorpay API or signature verification fails."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, code="RAZORPAY_ERROR", status_code=status_code)


class ExecutorUnavailableException(ReviveException):
    """Raised when execution gateway/service is unreachable."""
    def __init__(self, message: str = "Execution gateway is temporarily unavailable."):
        super().__init__(message, code="EXECUTOR_UNAVAILABLE", status_code=503)


class InvalidAIOutputException(ReviveException):
    """Raised when AI proposes an invalid, out-of-schema, or unsafe action."""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_AI_OUTPUT", status_code=422)
