# A Simple Signaling Game: Physician Testing

## Abstract

We study a signaling game where a physician decides whether to conduct a diagnostic test based on a patient's symptoms. The physician has incomplete information about the patient's true condition.

## 1. Model Setup

### 1.1 Players

The game involves two players:
- **Physician (P)**: Makes testing decisions to maximize expected utility
- **Nature (N)**: Determines patient's true condition (not a strategic player)

### 1.2 Patient Types

Nature draws the patient's type from a binary set:
- **Sick (S)**: Patient has the condition (probability π₀ = 0.3)
- **Healthy (H)**: Patient is healthy (probability 1 - π₀ = 0.7)

### 1.3 Information Structure

- The patient's true type is **private information**
- The physician observes a noisy **signal** σ ∈ {s, h}:
  - If patient is Sick: P(σ = s | S) = 0.8 (signal accuracy)
  - If patient is Healthy: P(σ = h | H) = 0.9 (signal specificity)

### 1.4 Actions

The physician can choose:
- **Test (T)**: Conduct diagnostic test (cost c = 10)
- **No Test (NT)**: Skip testing (cost 0)

### 1.5 Payoffs

The physician's utility function:
```
U(a, θ) = v(a, θ) - c(a)
```

Where:
- v(Test, Sick) = 100 (correct treatment after test)
- v(Test, Healthy) = 50 (no unnecessary treatment)
- v(NoTest, Sick) = -200 (misdiagnosis, patient suffers)
- v(NoTest, Healthy) = 50 (correct decision, no waste)
- c(Test) = 10 (testing cost)
- c(NoTest) = 0 (no cost)

## 2. Game Timeline

**Stage 1**: Nature draws patient type θ ∈ {S, H} according to prior π₀

**Stage 2**: Physician observes signal σ ∈ {s, h}

**Stage 3**: Physician updates belief using Bayes' rule:
```
P(S | σ=s) = P(σ=s | S) · π₀ / P(σ=s)
```

**Stage 4**: Physician chooses action a ∈ {Test, NoTest} to maximize expected utility

## 3. Equilibrium Analysis

### 3.1 Belief Updating

Using Bayes' rule:

**After observing σ = s (sick signal)**:
```
π(S | s) = (0.8 × 0.3) / (0.8 × 0.3 + 0.1 × 0.7) 
         = 0.24 / 0.31 
         ≈ 0.774
```

**After observing σ = h (healthy signal)**:
```
π(S | h) = (0.2 × 0.3) / (0.2 × 0.3 + 0.9 × 0.7)
         = 0.06 / 0.69
         ≈ 0.087
```

### 3.2 Optimal Decision Rule

The physician tests if and only if the expected gain from testing exceeds the cost.

Expected utility of testing:
```
EU(Test | σ) = π(S|σ) · (100 - 10) + (1 - π(S|σ)) · (50 - 10)
              = π(S|σ) · 90 + (1 - π(S|σ)) · 40
```

Expected utility of not testing:
```
EU(NoTest | σ) = π(S|σ) · (-200) + (1 - π(S|σ)) · 50
```

### 3.3 Threshold Analysis

The physician tests when:
```
EU(Test | σ) ≥ EU(NoTest | σ)
```

This simplifies to:
```
π(S|σ) ≥ π* = (50 + c) / (290 + c)
```

Where π* is the belief threshold. With c = 10:
```
π* = 60 / 300 = 0.2
```

## 4. Theoretical Results

**Proposition 1** (Signal Response): 
In equilibrium, the physician always tests after observing the sick signal (σ = s) and never tests after observing the healthy signal (σ = h).

*Proof*: After σ = s, the posterior belief π(S|s) ≈ 0.774 > 0.2 = π*, so testing is optimal. After σ = h, the posterior belief π(S|h) ≈ 0.087 < 0.2 = π*, so not testing is optimal. ∎

**Proposition 2** (Monotonicity): 
The testing threshold π* is strictly increasing in the testing cost c.

*Proof*: Taking the derivative: dπ*/dc = 240/(290+c)² > 0 for all c ≥ 0. ∎

**Corollary 1** (High Cost Limit):
As c → ∞, the threshold π* → 1, meaning the physician only tests when almost certain the patient is sick.

**Lemma 1** (Value of Information):
The expected value of observing the signal before deciding is:
```
VoI = E[EU(optimal | σ)] - EU(optimal | no signal) ≥ 0
```

## 5. Comparative Statics

**Result 1**: Increasing signal accuracy (sensitivity) increases the posterior belief π(S|s) and decreases π(S|h), making the signal more informative.

**Result 2**: For sufficiently low cost (c < 50), the physician would test regardless of signal. For very high cost (c > 250), the physician never tests.

## 6. Numerical Example

Consider baseline parameters:
- Prior: π₀ = 0.3
- Signal accuracy: P(s|S) = 0.8, P(h|H) = 0.9  
- Testing cost: c = 10
- Payoffs: v(T,S)=100, v(T,H)=50, v(NT,S)=-200, v(NT,H)=50

Equilibrium strategy:
- After σ = s: Test (EU ≈ 79.7)
- After σ = h: Don't test (EU ≈ 32.6)

Expected welfare: E[U] ≈ 0.31 × 79.7 + 0.69 × 32.6 ≈ 47.2

## 7. Discussion

This simple model illustrates:
1. **Information value**: Signals enable better decisions
2. **Cost-benefit tradeoffs**: Testing cost affects threshold
3. **Bayesian updating**: Rational belief revision
4. **Perfect Bayesian Equilibrium**: Solution concept for dynamic games with incomplete information

## References

- Spence, M. (1973). Job Market Signaling. *Quarterly Journal of Economics*.
- Cho, I.-K., & Kreps, D. M. (1987). Signaling Games and Stable Equilibria. *Quarterly Journal of Economics*.
