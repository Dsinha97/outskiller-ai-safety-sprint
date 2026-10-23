# Session 2 summary: Steganographic collusion (Sumeet)

## Key ideas

- Collusion is incentivized when agents' joint reward is higher if they share private information or cheat together than if they don't. If collusion is penalized, optimization pressure pushes agents toward secret collusion.
- Encryption hides the content but reveals that a secret is being passed. Steganography hides the communication itself inside text that looks normal.
- Three types of steganography:
  - Cover-text modification: hide bits in existing text (for example, the first letters of words spell "MEET"). Easy to detect with a well-equipped overseer.
  - Complexity-theoretic: secure against polynomially bounded adversaries. Requires a shared cipher or public keys.
  - Information-theoretic (perfectly secure): the stegotext keeps the cover-text distribution, so statistical tests see a KL divergence of zero. Based on Schroeder de Witt et al.
- Required capabilities (2024 eval, GPT-4 the best model then): Schelling point coordination, theory of mind, symmetric ciphers, self-sampling and logit simulation, and tool use. Most frontier models can likely do nearly all of these now.
- Trends: Schelling coordination improves with capability. The overseer falls behind as model capability rises. Models are better at colluding than at oversight.
- Models already coordinate without messaging and can use ciphers. The Hugging Face swarm incident was plain-text collusion. Early signs of steganography include attempts to use invisible Unicode characters.

## Mitigations and why each is insufficient

- Parameter tuning (RL against collusion): imperfect. A capability cannot be cleanly unlearned from a trillion-parameter model.
- Restricting external tools: necessary but not sufficient. Models can write their own code and access randomness.
- Paraphrasing: the most practical option, but the semantic choice (which topic to discuss) still carries information. Removing that means stopping communication.

## Undetectable threats

- Encrypted hidden model inside a larger model: a small model is cryptographically encrypted into a host model and activated by a trigger (a hashed secret XORed with the ciphertext). The capability can be neither detected nor elicited without breaking cryptography. Not practical yet, but a long-term threat.

## High-priority research directions

- Schelling point coordination in frontier models.
- Steganography in chain of thought, including encoded or unreadable reasoning.
- Monitoring for steganographic tool use and for paraphrasing.
- Training methods that discourage collusion without teaching agents to hide it.

## Notable Q&A points

- Most mind-changing weekend experiment: showing that paraphrasing works as a defense. He is not optimistic about it.
- Colluding with future copies of oneself: worth a project. He expects it to resemble multi-agent collusion.
- Human language versus LLM-native: the speaker does not expect human language to persist unless it is enforced. Learned vectors can be more efficient.
- Blocking channels: the simplest fix, but it cuts task performance, which creates pressure to reopen them. Plan defenses for that case.
- Perfectly secure steganography cannot be detected from the channel alone. Monitor actions, tool use, and the capabilities used in chain of thought.

## Project ideas for our team

- Run an RL setup that rewards collusion, then test paraphrasing and monitors against it.
- Run a weekend test of whether paraphrasing defeats cover-text channels.
- Measure whether current models coordinate on Schelling points in a toy task, tracking results across model versions.
- Build a monitor for encoded chain of thought and hidden Unicode in agent outputs.
- Study collusion between an agent and its future instance.
