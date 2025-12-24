"""DSPy optimization for diagnoser module."""
import dspy
from .agent import NetworkDiagnoser, configure_ollama
from .dataset import to_dspy_examples
from .signatures import DiagnosisResult


def metric(example, pred, trace=None):
    """Check if prediction matches expected diagnosis."""
    # pred is DiagnosisResult directly (not Prediction)
    if pred is None:
        return 0.0
    expected = example.diagnosis
    # Check all fields match
    if pred.issue_detected != expected.issue_detected:
        return 0.0
    if pred.issue_detected and pred.issue_type != expected.issue_type:
        return 0.5
    return 1.0


def optimize(model: str = "qwen3:1.7b", n: int = 5):
    """Run BootstrapFewShot optimization."""
    configure_ollama(model)
    trainset = to_dspy_examples(n=n)
    diagnoser = NetworkDiagnoser()

    optimizer = dspy.BootstrapFewShot(metric=metric, max_bootstrapped_demos=2)
    optimized = optimizer.compile(diagnoser, trainset=trainset)
    return optimized


def optimize_simba(model: str = "qwen3:1.7b", n: int = 20):
    """Run SIMBA optimization with larger dataset."""
    configure_ollama(model)
    trainset = to_dspy_examples(n=n)
    diagnoser = NetworkDiagnoser()
    optimizer = dspy.SIMBA(metric=metric, max_demos=4, max_steps=4)
    return optimizer.compile(diagnoser, trainset=trainset)


if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen3:1.7b"
    print(f"Optimizing with {model}...")
    opt = optimize(model)
    print("Done. Optimized diagnoser:")
    demos = getattr(opt.predict, "demos", [])
    print(f"  {len(demos)} demos learned")
