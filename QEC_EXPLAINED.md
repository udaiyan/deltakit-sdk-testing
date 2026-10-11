# Quantum Error Correction, Explained

A plain-English guide to what the Deltakit test suite is actually testing,
and why it matters. Written for interview preparation and general
understanding.

---

## Part 1: What is a Qubit?

### The Spinning Coin

Imagine a coin spinning on a table. While it spins, it is neither heads
nor tails. It is a blur of both at once.

That blur is a **superposition**. A classical computer bit is a coin
lying flat: it is definitely heads (1) or definitely tails (0). A
**qubit** is a coin still spinning. It holds both possibilities at once,
and that "both at once" property is what makes quantum computers
powerful.

### The Problem: Coins Fall Over

A spinning coin is fragile. A vibration, a draught, a stray magnetic
field, any tiny disturbance, and the coin wobbles and falls flat.

When that happens, the superposition is lost. The qubit becomes a plain
0 or 1, and the quantum computation is ruined.

Physicists call this **decoherence**. It is the single biggest obstacle
to building a useful quantum computer.

---

## Part 2: The Obvious Fix (That Doesn't Work)

### Classical Error Correction

Classical computers have solved this already. To store a "0", store
"000" instead. If one bit flips and the system reads "010", the majority
is 0 and the error is corrected.

Simple. Effective. Works.

### Why It Fails for Qubits

An unknown quantum state cannot be copied.

This is not an engineering limitation. It is a fundamental law of
physics called the **No-Cloning Theorem**.

Why? Because to copy a quantum state, the state must be measured. And
the moment a qubit is measured, its superposition collapses. The
spinning coin falls flat. The very thing being protected is destroyed.

### "But What About Copying a Known State?"

Fair question. If a qubit is definitely 0, as many copies as desired can
be made.

But here is the catch: **a known state is useless for quantum computing**.

The entire power of a quantum computer comes from processing *unknown*
states, states in superposition, entangled with other qubits. If the
state is already known, the computation is finished. There is nothing
left to compute.

So classical copying is not just forbidden. It is pointless.

---

## Part 3: The Real Fix - Quantum Error Correction

### Spreading, Not Copying

Since the state cannot be copied, something cleverer is needed.

The information is **spread across several qubits** and entangled
together.

Instead of one fragile coin, a team of coins is used, all spinning in a
coordinated way. If one coin wobbles, the others still carry the
information, and the wobble can be identified and fixed.

This team of physical qubits holding one piece of quantum information is
called a **logical qubit**.

### The Key Insight

The individual coins are never inspected directly. Only the
**relationships between them** are checked.

For example: "Is qubit A the same as qubit B?"

- If yes, they agree. No problem.
- If no, one of them has been disturbed.

An error has been detected **without ever measuring the data itself**.
The superposition survives.

---

## Part 4: How Do We Check Without Looking?

### The Ancilla Trick

To ask "are these two qubits the same?", a helper qubit is brought in,
called an **ancilla** (Latin for "maidservant").

Here is the recipe:

1. Start the ancilla at 0.
2. Use Qubit A to control a NOT operation on the ancilla.
3. Use Qubit B to control another NOT operation on the ancilla.
4. Measure the ancilla.

The result tells the **parity**, whether A and B agree.

| A | B | Ancilla after | Meaning |
|---|---|---------------|---------|
| 0 | 0 | 0 | Same |
| 1 | 1 | 0 | Same |
| 0 | 1 | 1 | Different |
| 1 | 0 | 1 | Different |

### Why This Doesn't Destroy the Data

The ancilla was measured, not the data qubits. The ancilla was just a
messenger. All that was learned was the *relationship* between A and B.

If the ancilla reads 0, Qubit A and Qubit B could both be 0, or both
be 1. The actual values remain unknown. The superposition is intact.

The error has been detected without destroying the information.

---

## Part 5: The Two Ways a Qubit Goes Wrong

A qubit can fail in two fundamental ways.

### Bit Flip

The coin physically flips over. A 0 becomes a 1, or a 1 becomes a 0.

This is like a classical bit flip, the only kind of error classical
computers face.

Bit flips are protected against using **Z stabilisers**.

### Phase Flip

This one has no classical equivalent. It is purely quantum.

A qubit can be in the state "0 + 1". There is another version with a
minus sign: "0 - 1".

A phase flip does not change whether the coin shows heads or tails. It
flips the *sign*, the relationship between the two possibilities:

- "0 + 1" becomes "0 - 1"
- "0 - 1" becomes "0 + 1"

Physically, this is a change in the phase of the quantum state.

Phase flips are protected against using **X stabilisers**.

### What is a "Stabiliser Type"?

When a repetition code is built in Deltakit, the type of error to
protect against is chosen:

    RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)   # bit flips
    RepetitionCode(distance=3, stabiliser_type=PauliBasis.X)   # phase flips

Simple repetition codes handle one or the other. Real QEC codes, like
the **surface code**, handle both at once.

---

## Part 6: The Repetition Code

### The Layout

A distance-3 repetition code looks like this:

    Data:    Q0 ----- Q2 ----- Q4
              |         |
    Ancilla: A1        A3

Three data qubits in a line, plus two ancilla qubits. Five total.

- Ancilla 1 checks: is Q0 the same as Q2?
- Ancilla 3 checks: is Q2 the same as Q4?

### The Clever Part: Overlapping Checks

Notice that Q2 is watched by **both** ancillas.

- If Q0 wobbles: only Ancilla 1 fires.
- If Q4 wobbles: only Ancilla 3 fires.
- If Q2 wobbles: **both** ancillas fire.

By comparing which ancillas fired, exactly which qubit went wrong can be
identified. That is the whole trick.

### What "Distance" Means

"Distance 3" means the code can detect and correct up to 1 error. In
general, a distance-d code can correct (d-1)/2 errors.

The larger the distance, the more errors the code can survive, but the
more qubits are required. There is always a trade-off.

### The Surface Code - The Real Thing

The repetition code is a teaching tool. It protects against one type of
error at a time. Real quantum computers need protection against both.

The **surface code** is the leading candidate for real-world QEC. It:

- Arranges qubits in a 2D grid rather than a line
- Has both X-stabilisers and Z-stabilisers running side by side
- Can correct bit flips and phase flips simultaneously
- Has a high error threshold: it keeps working even when around 1% of
  operations go wrong

The rotated planar code tested in Deltakit is a variant of the surface
code. It uses fewer qubits by rotating the lattice 45 degrees, but
provides the same protection.

Riverlane works extensively with surface codes. If fault-tolerant
quantum computing becomes a reality, the surface code will likely be a
big part of why.

---

## Part 7: The Decoder - The Detective

So far, detection has identified that *something* went wrong. But what
went wrong, and how to fix it, is not yet known.

That job belongs to the **decoder**.

### Why Decoding is Hard

The syndrome pattern (the ancilla readings) is a set of symptoms. Like
a doctor seeing a rash and a fever, the underlying cause cannot be
observed directly. Many different errors can produce the same syndrome.

Consider the repetition code. If Ancilla 1 fires but Ancilla 3 does not,
the error is on Qubit 0 or Qubit 2. It could be:

- A bit flip on Qubit 0 that made it disagree with Qubit 2
- A bit flip on Qubit 2 that made it disagree with both neighbours

The second option would normally trigger both ancillas, so the first is
more likely. The decoder's job is to reason like this: given a syndrome,
find the *most likely* set of errors that caused it.

### How a Decoder Works

Most decoders use one of two strategies.

**Matching.** Build a graph where the nodes are detector events. Find
the shortest path between them, treating each edge as a possible error.
The shortest path is the most likely explanation. This is how
Riverlane's **PyMatchingDecoder** works.

**Clustering.** Group nearby detector events into clusters and assign
each cluster an error type. Faster than matching, sometimes less
accurate. This is how Riverlane's proprietary **Ambiguity Clustering**
decoder works, a Riverlane invention.

### Why Speed Matters

A real quantum computer produces syndrome data thousands of times per
second. The decoder must keep up.

If it falls behind, errors accumulate faster than they can be corrected.
The quantum state decoheres before the correction arrives. This is why
Riverlane's decoders run on dedicated hardware, in real time.

Decoding is not just a maths problem. It is an engineering race.

---

## Part 8: A Brief History of QEC

**1994 - Peter Shor shocks the world.**

He shows that a quantum computer could factor large numbers
exponentially faster than any classical machine. Suddenly, everyone
wants to build one.

**1995 - The problem surfaces.**

Everyone realises qubits are too fragile. The No-Cloning Theorem seems
to make error correction impossible. Quantum computing looks dead on
arrival.

**1995 - Shor does it again.**

In a moment of brilliance, Shor invents the first quantum error
correcting code. He shows that quantum information can be protected
without copying it, using entanglement instead.

**1996 - CSS codes.**

Calderbank, Shor and Steane independently develop a family of codes that
protect against both bit flips and phase flips. These are still the
backbone of practical QEC today.

**1998 - The surface code.**

Alexei Kitaev proposes the surface code, a 2D arrangement of qubits that
is far easier to build than earlier designs.

**2010s - The experimental race begins.**

Google, IBM and startups worldwide start building real quantum hardware.
QEC moves from theory to engineering.

**2024 - Below threshold.**

Google demonstrates that adding more physical qubits actually reduces
the logical error rate. This is the first time QEC has been shown to
work at scale, a milestone the field had been chasing for 30 years.

**Today - The real-time challenge.**

Attention shifts to decoders that can keep up with quantum hardware.
This is where Riverlane plays.

The field is barely 30 years old. Much remains to be invented.

---

## Part 9: What Riverlane Does

### The Timing Problem

Quantum computers make errors in **microseconds**. If the error
correction software is slow, the quantum state will have decohered
before the correction arrives.

This is not a problem that can be solved by throwing more time at it.
The correction must happen in real time, at the speed of the quantum
hardware.

### Deltaflow - The Real-Time Control Stack

Riverlane's **Deltaflow** is the middle layer between quantum hardware
and classical computers.

It has three jobs:

1. **Collect syndromes.** Read the ancilla measurements from the quantum
   hardware, at speed.
2. **Decode.** Run the decoder to figure out the most likely error.
3. **Send corrections.** Tell the quantum hardware which operations to
   apply.

All of this happens in **microseconds**, faster than a qubit decoheres.

### The Hardware Challenge

Real quantum hardware today:

| System | Qubits |
|---|---|
| Google's Willow | ~100 |
| IBM's Condor | ~1,000 |
| A useful surface code patch | ~1,000-10,000 physical qubits per logical qubit |

The field is at the very beginning. Riverlane's bet is that real-time
decoding becomes the bottleneck once hardware scales. That is what
Deltaflow is built for.

### Deltakit - The Design Studio

**Deltakit** is Riverlane's open-source software toolkit for designing,
simulating and analysing QEC experiments.

Think of it like this:

- **Deltaflow** is the engine: runs in real time, close to the hardware
- **Deltakit** is the design studio: where scientists build and test
  experiments before they run on real hardware

Both are essential. Deltaflow without Deltakit has no experiments to
run. Deltakit without Deltaflow has no hardware to run on.

---

## Part 10: What My Repo Tests

### The Big Idea

I did not build the quantum computer. I built the **quality control
system** for the software that designs quantum error correction.

Think of it like a restaurant critic visiting a restaurant, rather than
the chef tasting their own food. Independent verification, not
self-assessment.

### The Pipeline I Tested

    Build a team of qubits              (RepetitionCode)
              |
              v
    Write the rulebook for inspectors   (parity_check_matrices)
              |
              v
    Set up the experiment               (css_code_memory_circuit)
              |
              v
    Add realistic noise                 (SI1000Noise)
              |
              v
    Run 1,000 simulations               (simulate_with_stim)
              |
              v
    Interpret the results               (to_detectors_and_observables)
              |
              v
    Verify physics is respected         (integration tests)

Each stage can fail. My tests catch failures at every stage.

### Why Do The Names Sound So Strange?

The names come from quantum information theory, but each one describes a
concrete object. Here is what they actually mean.

**`RepetitionCode` - the blueprint.**

A `RepetitionCode` is a blueprint: a set of instructions that tells the
quantum computer three things:

1. How many qubits to use
2. How to arrange them physically (in a line, a grid, etc.)
3. Which qubits the ancillas should watch

The name comes from classical computing. To protect a single bit from
errors, it is stored three times: instead of `0`, store `000`. If one
bit flips and the system reads `010`, the original was `000` by majority
vote.

A quantum repetition code does the same thing, but with a twist. An
unknown quantum state cannot be copied (that is the No-Cloning Theorem).
So instead of copying the *state*, the code **spreads the information
across multiple qubits using entanglement**.

For a distance-3 code, three data qubits are used. The information is
encoded so that:

- Logical `0` becomes a state where all three qubits agree: `000`
- Logical `1` becomes `111`

If one qubit flips, say the middle one becomes `010`, the ancillas
detect the disagreement, and exactly which qubit to fix is known.

When the code is built with:

    RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)

The `distance=3` means "use three data qubits in a line." The number 3
also tells how many errors the code can survive: a distance-d code can
correct up to (d-1)/2 errors. So distance 3 corrects 1 error; distance 5
corrects 2; distance 7 corrects 3, and so on.

The `RepetitionCode` object is not the experiment itself. It is the
*plan* for the experiment. To actually run something, this blueprint
must be turned into a circuit, which is the next step in the pipeline.

**`parity_check_matrices` - the rulebook.**

A pair of matrices (one for X checks, one for Z checks) that list which
data qubits each ancilla watches. Every `1` in the matrix means "this
ancilla is connected to this data qubit". Every `0` means "not
connected". This is how the physical wiring is described
mathematically.

**`css_code_memory_circuit` - the experiment recipe.**

Given a code, this function builds the actual sequence of quantum gates
that:

1. Prepares the qubits in the right starting state
2. Runs several rounds of error detection
3. Measures the logical qubit at the end to see if it survived

The `css` prefix refers to CSS codes (Calderbank-Shor-Steane), a family
of QEC codes that handle X and Z errors separately. Most practical QEC
codes, including the surface code, are CSS codes.

The word **memory** refers to a memory experiment, the simplest possible
QEC experiment. It asks one question: *"If a logical qubit is stored for
a while, does it survive?"*

A memory experiment has three stages:

**Stage 1 - Initialise.** Prepare the logical qubit in a known state.
For a Z-basis memory experiment, logical `0` is prepared (all data
qubits in state 0). For an X-basis memory experiment, logical `+` is
prepared (a superposition state).

**Stage 2 - Store and correct.** Run several rounds of error detection.
Each round, the ancillas check the data qubits, the syndrome is
recorded, and (in a real system) the decoder figures out errors and
corrections are applied. The longer the storage, the more rounds run,
and the more chances errors have to accumulate.

**Stage 3 - Measure.** At the end, the logical qubit is measured. Did it
survive as `0`, or did it flip to `1`? If it flipped when it should not
have, the code failed.

The output is a **logical error rate**: the fraction of shots where the
logical qubit flipped incorrectly. If 1,000 shots are run and 50 show
the wrong logical value, the logical error rate is 5%.

A good QEC code has a logical error rate far lower than the physical
error rate. That is the whole point: many noisy physical qubits, working
together, produce one reliable logical qubit.

So the name `css_code_memory_circuit` literally says: "Build a memory
experiment circuit for a CSS code."

**`SI1000Noise` - the noise model.**

A noise model is a recipe that says: *"Here is how often each type of
quantum operation goes wrong."*

`SI1000Noise` is a specific, standardised recipe from academic
literature. It is designed to mimic the noise behaviour of real
**superconducting qubits**, the technology used by Google, IBM, and most
current quantum hardware.

The name comes from the original paper by Gidney et al. (2021) and
stands for:

**S**uperconducting **I**nspired with **1000** nanosecond cycle

- **Superconducting Inspired**: the error rates are based on
  measurements from real superconducting quantum hardware
- **1000 nanosecond cycle**: the model assumes each round of error
  correction takes about 1 microsecond, which is typical for
  superconducting devices

The model has a single parameter `p`, the base error rate. Different
operations have different error rates, scaled from `p`:

| Operation | Error probability | Why |
|---|---|---|
| Idle qubits | p/10 | Qubits sitting idle still decohere, but slowly |
| Idle during measurement/reset | 2p/10 | Idle qubits suffer extra noise when neighbours are being measured |
| Single-qubit gates | 2p/10 | One-qubit operations are relatively reliable |
| Two-qubit gates | p | Two-qubit gates are the noisiest operation |
| Measurement | p | Reading a qubit can flip the result |
| Reset | 5p/10 | Preparing a qubit in state 0 can fail |

The key insight: **two-qubit gates are the bottleneck.** That is why
real quantum hardware developers spend so much effort making them
better.

When the model is used with:

    SI1000Noise(p=0.01)

This says: "Assume a base error rate of 1%." That means 1 in 100
two-qubit gates fails, 1 in 100 measurements gives the wrong answer, and
1 in 1,000 idle moments causes a problem.

This is roughly the level of current real quantum hardware. It is also
close to the **threshold**, the error rate below which QEC actually
improves things. Above the threshold, adding more qubits makes things
worse. Below it, adding more qubits makes things better.

The SI1000 model predicts a threshold of around **0.3%-0.5%** for the
surface code. The test used `p=0.01` (1%), which is above threshold. So
the logical error rate in the simulation would be *higher* than the
physical rate: the code is not yet helping. But the tests still verify
that the pipeline runs correctly and produces physically sensible
behaviour.

Deltakit's `SI1000NoiseModel` also supports a parameter `p_l` for
**leakage**, a specific type of error where a qubit leaves the
computational space entirely (it goes to a state that is neither 0 nor
1). This is a real problem in superconducting qubits and is more complex
to correct than a simple bit flip.

**`simulate_with_stim` - the simulator.**

`simulate_with_stim` runs the experiment many times and records what the
ancillas saw each time.

The "stim" in the name refers to **Stim**, an open-source simulator for
quantum error correction circuits, created by Craig Gidney at Google
Quantum AI. Stim is purpose-built for QEC and is the de facto standard
in the field.

Stim is fast. For the kinds of circuits used in QEC (Clifford circuits,
which is the class of quantum operations QEC relies on), it can simulate
millions of shots per second. A classical full-state simulator would
struggle with even a hundred qubits. Stim handles thousands.

It achieves this by exploiting the mathematical structure of stabiliser
circuits. Instead of tracking the full quantum state, it tracks only the
Pauli operators that define the state. This is a massive simplification
that makes large-scale QEC simulation practical.

Deltakit wraps Stim and provides a Python-friendly interface. When the
test calls:

    simulate_with_stim(stim_circuit, shots=1000)

Stim runs the circuit 1,000 times and returns two things:

- **Measurements**: the ancilla readings from each shot
- **LeakageFlags** (optional): whether any qubit leaked out of the
  computational space

Each "shot" is one complete run of the experiment, from preparation
through to measurement. Running many shots is necessary because the
errors are probabilistic: one shot tells very little, but 1,000 shots
reveal the underlying error rate.

**`to_detectors_and_observables` - the interpreter.**

Converts raw ancilla readings into two things:

- **Detector events**: where an error was spotted (a change between
  rounds)
- **Observable flips**: whether the logical qubit value ended up wrong

These two outputs are what a decoder needs.

### The Five Layers of Testing

| Layer       | What it verifies                              |
|-------------|-----------------------------------------------|
| Unit        | Code construction is correct                  |
| Contract    | Public API returns the shapes it promises     |
| Negative    | Invalid inputs are rejected                   |
| Integration | The full pipeline produces physically sensible results |
| Cloud       | Token-gated decoders work                     |

### The Most Important Tests

Two integration tests stand out.

**`test_higher_noise_yields_more_detector_events`**

Turn up the noise, and more errors should appear. If they do not,
something is wired up backwards.

**`test_zero_noise_produces_no_detections`**

Turn noise to zero, and nothing should fire. If a single event fires,
the software is inventing phantom errors.

These tests verify that the software obeys **physics**, not just that it
runs without crashing.

### Basis Coverage

QEC has two independent choices.

**Choice 1: The code's stabiliser basis.**

This asks: *what kind of error does the code watch for?*

- A **Z-stabiliser code** watches for **bit flips** (the coin flipping
  over: 0 becomes 1, or 1 becomes 0)
- An **X-stabiliser code** watches for **phase flips** (the subtle
  quantum sign change)
- A **rotated planar code** watches for **both at once**

**Choice 2: The logical memory basis.**

This asks: *which logical property is being protected?*

- A **Z-basis logical memory** prepares the logical qubit as a "logical
  0 or 1" and checks whether that value survived
- An **X-basis logical memory** prepares the logical qubit as a "logical
  plus or minus" and checks whether *that* survived

Both are legitimate experiments. They test different aspects of the
code.

**Why both choices matter.**

The two choices are independent. It is possible to run:

- A Z-stabiliser code with a Z-basis logical memory (protects against
  bit flips, stores a Z-logical qubit)
- A Z-stabiliser code with an X-basis logical memory (the code still
  watches for bit flips, but the check is whether the *X* logical
  operator survived)

The second case is a genuinely useful experiment in QEC research. It
verifies that the code protects both logical operators equally well, a
property called **code symmetry**.

The test suite covers all four combinations, so a bug in any one of them
would be caught.

---

## Part 11: What I Found

Testing real software finds real problems. Two were found.

### DEFECT-001: The Code Forgets What It Was Told

A `RepetitionCode` can be told which basis to use:

    RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)

But afterwards, it cannot be asked:

    code.stabiliser_type   # AttributeError

The code used the choice internally and then forgot it. This is an
**API ergonomics defect**. The code still works correctly, but consumers
cannot inspect it.

### DEFECT-002: Impossible Noise Levels Accepted

Noise probabilities must be between 0 and 1. There is no such thing as
-10% noise.

But the SDK accepts:

    SI1000Noise(p=-0.1)   # No error
    SI1000Noise(p=1.5)    # No error

This is a **high-severity defect**. The SDK silently accepts a
physically meaningless state, and downstream simulations may produce
nonsense.

### Why Documenting Defects Matters

Finding bugs is easy. Finding bugs and *explaining why they matter* is
the job.

A Staff Test Engineer does not just say "this test failed". They say:
"this test failed, here is the root cause, here is the severity, here
is the recommended fix, and here is the test that will verify it when
fixed."

That is what `TESTING.md` in the repo does.

---

## Part 12: Why This Matters?

When Riverlane (or anyone) asks about the repo, here is the story:

1. **The domain is understood.** QEC is understood: what it is, why it
   matters, and how it fits into Riverlane's mission.
2. **Independent testing.** Contributions were not made to Deltakit's
   own test suite. It was tested as a *consumer*, the way a real user
   would.
3. **Physics is verified, not just code.** The integration tests check
   that the pipeline produces physically sensible results, not just that
   it runs.
4. **Real defects were found.** Two of them, documented with severity
   and recommended fixes.
5. **Coverage was thought about.** A matrix across bases was built and
   all combinations verified, not just the happy path.
6. **The method was documented.** The `investigations/` folder shows how
   the API was discovered before tests were written against it.

The repo is not just code. It is evidence of how I figure things out.

---

## Glossary

**Ancilla**: A helper qubit used to perform checks without measuring the
data qubits directly.

**Bit flip**: A classical error where 0 becomes 1 or 1 becomes 0.

**CSS code**: A class of quantum error correcting codes named after
Calderbank, Shor, and Steane. Most practical QEC codes are CSS codes.

**Decoherence**: The process by which a qubit loses its quantum state
due to environmental interference.

**Detector event**: A signal that something changed between two rounds
of measurement. The raw input to a decoder.

**Distance**: A measure of how many errors a code can correct.
Distance-d corrects (d-1)/2 errors.

**Logical qubit**: One piece of quantum information encoded across many
physical qubits.

**No-Cloning Theorem**: A fundamental law of quantum mechanics: an
unknown quantum state cannot be copied.

**Parity**: Whether two qubits are the same (even parity) or different
(odd parity).

**Phase flip**: A purely quantum error that flips the sign of a
superposition.

**Physical qubit**: A single qubit, made of real hardware. Fragile.

**QEC**: Quantum Error Correction. The discipline of protecting quantum
information from errors.

**Stabiliser**: A measurement that checks a relationship between qubits
without measuring them individually.

**Stim**: An open-source, high-speed simulator for stabiliser circuits,
developed by Craig Gidney at Google Quantum AI. The de facto standard
for QEC simulation.

**Superposition**: A quantum state where a qubit holds multiple
possibilities at once.

**Threshold**: The physical error rate below which QEC improves logical
error rates. Above it, adding more qubits makes things worse.