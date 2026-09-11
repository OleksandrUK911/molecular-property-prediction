# Predict page

Головний екран застосунку, шлях `/`.

## Layout

Одноколонковий, центрований контент, `max-width` ~700px, під app shell
(див. [app-shell.md](app-shell.md)).

```
┌──────────────────────────────────────────────┐
│  Predict molecular properties                 │
│  ┌──────────────────────────────────┐ ┌─────┐ │
│  │ SMILES input                     │ │Predict│
│  └──────────────────────────────────┘ └─────┘ │
│  Try an example: [Aspirin] [Caffeine] [Ibuprofen] │
│  ──────────────────────────────────────────── │
│  ┌───────────────┐  ┌───────────────────────┐ │
│  │                │  │ Predicted solubility:  │ │
│  │  2D structure  │  │   -2.31 log(mol/L)     │ │
│  │  (SVG, ~240px) │  │ ─────────────────────  │ │
│  │                │  │ MolWt:   180.16        │ │
│  └───────────────┘  │ LogP:      1.19         │ │
│                      │ TPSA:     63.6          │ │
│                      │ H-Donors:  1            │ │
│                      └───────────────────────┘ │
│  ┌──────────────────────────────────────────┐  │
│  │       Descriptor bar chart (full width)   │  │
│  └──────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

На мобільному (<640px): одна колонка, порядок зверху вниз — структура молекули → картка результатів → графік.

## Компоненти на сторінці
- `SmilesInput` — див. [components.md](components.md#smilesinput)
- `ExampleChips` — 3 приклади (Aspirin, Caffeine, Ibuprofen), клік підставляє SMILES в `SmilesInput` і одразу тригерить submit
- `MoleculeStructure` — 2D SVG від бекенду
- `ResultsCard` — див. [components.md](components.md#resultscard)
- `DescriptorBarChart` — див. [data-visualization.md](data-visualization.md#descriptor-bar-chart)
- `ErrorBanner` — inline під інпутом

## Стани

| Стан | Тригер | Що видно |
|---|---|---|
| **Idle** | Початкове завантаження сторінки | Лише input + example chips. Область результатів прихована (не показує порожню картку). |
| **Loading** | Після натискання Predict / вибору прикладу | Input і кнопка disabled, у місці результатів — spinner (замінює всю область структура+картка+графік) |
| **Success** | Відповідь `/predict` 200 OK | Структура, картка результатів і графік заповнюються даними. Попередній результат (якщо був) замінюється новим. |
| **Error: invalid SMILES** | 422 від API (не парситься RDKit) | `ErrorBanner` під input: "Could not parse this SMILES string — check the syntax." Область результатів лишається в попередньому стані (idle або попередній success, не стирається). |
| **Error: server unavailable** | Network error / 5xx | `ErrorBanner`: "Server unavailable, please try again." + кнопка "Retry" (повторює останній запит) |

## Флоу
1. Користувач вводить SMILES або клікає приклад → `SmilesInput` валідує базовий синтаксис на клієнті (непорожній рядок) → submit.
2. Запит `POST /predict { smiles }` → Loading стан.
3. Success → рендер структури, картки, графіка. Error → банер, попередній контент результатів зберігається.
4. Кожен успішний прогноз опційно зберігається в історію (локально або на бекенді) — див. `frontend/TODO_state_data_layer.md`.
