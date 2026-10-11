# Classification comparison against analyst gold labels

| approach                |   Category % |   Urgency % |   Team % |
|:------------------------|-------------:|------------:|---------:|
| Gemini (revised prompt) |        100   |         100 |    100   |
| HF zero-shot            |         87.5 |          50 |     87.5 |
| Rule-based              |         87.5 |          75 |     87.5 |

## Per-message predictions (category / urgency)

| message_id   | Gold                           | Gemini (revised prompt)        | HF zero-shot                   | Rule-based                     |
|:-------------|:-------------------------------|:-------------------------------|:-------------------------------|:-------------------------------|
| M1           | WATER / HIGH                   | WATER / HIGH                   | WATER / HIGH                   | WATER / HIGH                   |
| M2           | WASTE_RECYCLING / MEDIUM       | WASTE_RECYCLING / MEDIUM       | WASTE_RECYCLING / HIGH         | WASTE_RECYCLING / MEDIUM       |
| M3           | ENERGY / MEDIUM                | ENERGY / MEDIUM                | ENERGY / HIGH                  | ENERGY / HIGH                  |
| M4           | PROCUREMENT_SUPPLIER / MEDIUM  | PROCUREMENT_SUPPLIER / MEDIUM  | PROCUREMENT_SUPPLIER / HIGH    | PROCUREMENT_SUPPLIER / MEDIUM  |
| M5           | ACCESSIBILITY / HIGH           | ACCESSIBILITY / HIGH           | ACCESSIBILITY / HIGH           | ACCESSIBILITY / HIGH           |
| M6           | HAZARDOUS_MATERIALS / CRITICAL | HAZARDOUS_MATERIALS / CRITICAL | HAZARDOUS_MATERIALS / CRITICAL | HAZARDOUS_MATERIALS / CRITICAL |
| M7           | FACILITIES_GENERAL / LOW       | FACILITIES_GENERAL / LOW       | ENERGY / LOW                   | ENERGY / MEDIUM                |
| M8           | GOVERNANCE_CONDUCT / HIGH      | GOVERNANCE_CONDUCT / HIGH      | GOVERNANCE_CONDUCT / MEDIUM    | GOVERNANCE_CONDUCT / HIGH      |

## Gemini run-to-run consistency (3 runs, temperature 0)

- M1: consistent
- M2: consistent
- M3: consistent
- M4: consistent
- M5: consistent
- M6: consistent
- M7: consistent
- M8: consistent
